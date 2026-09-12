from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import httpx
import pytest


class RecordingCacheClient:
    def __init__(self) -> None:
        self.environments = {
            "task-a": ["environment-1", "environment-2"],
            "task-b": ["environment-3"],
        }
        self.drain_calls: list[tuple[str, str]] = []
        self.ack_calls: list[tuple[str, str]] = []
        self.close_calls = 0
        self.drain_failures: set[str] = set()
        self.ack_failures: set[str] = set()

    async def drain_task(
        self,
        task_name: str,
        drain_id: str,
    ) -> list[str]:
        self.drain_calls.append((task_name, drain_id))
        if task_name in self.drain_failures:
            raise RuntimeError(f"drain failed: {task_name}")
        return self.environments.pop(task_name, [])

    async def ack_task_drain(
        self,
        task_name: str,
        drain_id: str,
    ) -> None:
        self.ack_calls.append((task_name, drain_id))
        if task_name in self.ack_failures:
            raise RuntimeError(f"ack failed: {task_name}")

    async def close(self) -> None:
        self.close_calls += 1


class RecordingEnvironment:
    stop_attempts: list[tuple[str, str, str]] = []
    stop_failures: set[str] = set()

    def __init__(
        self,
        env_id: str,
        task_name: str,
        sandbox_base_url: str,
    ) -> None:
        self.env_id = env_id
        self.task_name = task_name
        self.sandbox_base_url = sandbox_base_url

    async def stop(self, **kwargs: Any) -> None:
        self.stop_attempts.append(
            (self.task_name, self.env_id, self.sandbox_base_url)
        )
        if self.env_id in self.stop_failures:
            raise RuntimeError(f"stop failed: {self.env_id}")


@pytest.mark.asyncio
async def test_run_lifecycle_retries_only_failed_environment_stops() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    RecordingEnvironment.stop_attempts.clear()
    RecordingEnvironment.stop_failures = {"environment-2"}
    client = RecordingCacheClient()
    lifecycle = TVCacheRunLifecycle(
        environment_class=RecordingEnvironment,
        tvcache_base_url="http://cache.test",
        env_kwargs={"sandbox_base_url": "http://sandbox.test"},
    )
    lifecycle.client = client
    lifecycle.register_task("task-b")
    lifecycle.register_task("task-a")
    lifecycle.register_task("task-a")

    with pytest.raises(RuntimeError, match="stop failed: environment-2"):
        await lifecycle.close()

    assert [task_name for task_name, _ in client.drain_calls] == [
        "task-a",
        "task-b",
    ]
    drain_ids = dict(client.drain_calls)
    assert client.ack_calls == [("task-b", drain_ids["task-b"])]
    assert client.close_calls == 1
    assert RecordingEnvironment.stop_attempts == [
        ("task-a", "environment-1", "http://sandbox.test"),
        ("task-a", "environment-2", "http://sandbox.test"),
        ("task-b", "environment-3", "http://sandbox.test"),
    ]

    RecordingEnvironment.stop_failures.clear()
    await lifecycle.close()

    assert [task_name for task_name, _ in client.drain_calls] == [
        "task-a",
        "task-b",
    ]
    assert client.ack_calls == [
        ("task-b", drain_ids["task-b"]),
        ("task-a", drain_ids["task-a"]),
    ]
    assert client.close_calls == 2
    assert RecordingEnvironment.stop_attempts == [
        ("task-a", "environment-1", "http://sandbox.test"),
        ("task-a", "environment-2", "http://sandbox.test"),
        ("task-b", "environment-3", "http://sandbox.test"),
        ("task-a", "environment-2", "http://sandbox.test"),
    ]


@pytest.mark.asyncio
async def test_run_lifecycle_retries_failed_task_drain() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    RecordingEnvironment.stop_attempts.clear()
    RecordingEnvironment.stop_failures.clear()
    client = RecordingCacheClient()
    client.environments = {"task-a": ["environment-1"]}
    client.drain_failures = {"task-a"}
    lifecycle = TVCacheRunLifecycle(
        environment_class=RecordingEnvironment,
        tvcache_base_url="http://cache.test",
        env_kwargs={"sandbox_base_url": "http://sandbox.test"},
    )
    lifecycle.client = client
    lifecycle.register_task("task-a")

    with pytest.raises(RuntimeError, match="drain failed: task-a"):
        await lifecycle.close()

    client.drain_failures.clear()
    await lifecycle.close()

    assert [task_name for task_name, _ in client.drain_calls] == [
        "task-a",
        "task-a",
    ]
    assert client.drain_calls[0][1] == client.drain_calls[1][1]
    assert RecordingEnvironment.stop_attempts == [
        ("task-a", "environment-1", "http://sandbox.test"),
    ]
    assert client.ack_calls == [client.drain_calls[1]]


@pytest.mark.asyncio
async def test_run_lifecycle_preserves_primary_and_cleanup_errors() -> None:
    from utils.tvcache_run_lifecycle import (
        TVCacheRunLifecycle,
        TVCacheRunLifecycleError,
    )

    RecordingEnvironment.stop_attempts.clear()
    RecordingEnvironment.stop_failures = {"environment-1"}
    client = RecordingCacheClient()
    client.environments = {"task-a": ["environment-1"]}
    lifecycle = TVCacheRunLifecycle(
        environment_class=RecordingEnvironment,
        tvcache_base_url="http://cache.test",
        env_kwargs={"sandbox_base_url": "http://sandbox.test"},
    )
    lifecycle.client = client

    with pytest.raises(TVCacheRunLifecycleError) as exc_info:
        async with lifecycle:
            lifecycle.register_task("task-a")
            raise ValueError("training failed")

    assert str(exc_info.value.primary_error) == "training failed"
    assert len(exc_info.value.cleanup_errors) == 1
    assert "stop failed: environment-1" in str(
        exc_info.value.cleanup_errors[0]
    )


class CommitThenLoseDrainResponseClient(RecordingCacheClient):
    def __init__(self) -> None:
        super().__init__()
        self.environments = {"task-a": ["environment-1"]}
        self.committed_drains: dict[str, list[str]] = {}

    async def drain_task(
        self,
        task_name: str,
        drain_id: str,
    ) -> list[str]:
        self.drain_calls.append((task_name, drain_id))
        if drain_id not in self.committed_drains:
            self.committed_drains[drain_id] = self.environments.pop(
                task_name,
                [],
            )
            raise RuntimeError("drain response lost after commit")
        return list(self.committed_drains[drain_id])


@pytest.mark.asyncio
async def test_run_lifecycle_reuses_drain_id_after_commit_response_loss() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    RecordingEnvironment.stop_attempts.clear()
    RecordingEnvironment.stop_failures.clear()
    client = CommitThenLoseDrainResponseClient()
    lifecycle = TVCacheRunLifecycle(
        environment_class=RecordingEnvironment,
        tvcache_base_url="http://cache.test",
        env_kwargs={"sandbox_base_url": "http://sandbox.test"},
    )
    lifecycle.client = client
    lifecycle.register_task("task-a")

    with pytest.raises(
        RuntimeError,
        match="drain response lost after commit",
    ):
        await lifecycle.close()

    assert RecordingEnvironment.stop_attempts == []

    await lifecycle.close()

    assert len(client.drain_calls) == 2
    assert client.drain_calls[0] == client.drain_calls[1]
    assert RecordingEnvironment.stop_attempts == [
        ("task-a", "environment-1", "http://sandbox.test"),
    ]
    assert client.ack_calls == [client.drain_calls[1]]


class CommitThenLoseAckResponseClient(RecordingCacheClient):
    def __init__(self) -> None:
        super().__init__()
        self.environments = {"task-a": ["environment-1"]}
        self.committed_ack_ids: set[str] = set()

    async def ack_task_drain(
        self,
        task_name: str,
        drain_id: str,
    ) -> None:
        self.ack_calls.append((task_name, drain_id))
        if drain_id not in self.committed_ack_ids:
            self.committed_ack_ids.add(drain_id)
            raise RuntimeError("ack response lost after commit")


@pytest.mark.asyncio
async def test_run_lifecycle_retries_ack_without_repeating_stops() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    RecordingEnvironment.stop_attempts.clear()
    RecordingEnvironment.stop_failures.clear()
    client = CommitThenLoseAckResponseClient()
    lifecycle = TVCacheRunLifecycle(
        environment_class=RecordingEnvironment,
        tvcache_base_url="http://cache.test",
        env_kwargs={"sandbox_base_url": "http://sandbox.test"},
    )
    lifecycle.client = client
    lifecycle.register_task("task-a")

    with pytest.raises(
        RuntimeError,
        match="ack response lost after commit",
    ):
        await lifecycle.close()

    assert RecordingEnvironment.stop_attempts == [
        ("task-a", "environment-1", "http://sandbox.test"),
    ]

    await lifecycle.close()

    assert len(client.drain_calls) == 1
    assert RecordingEnvironment.stop_attempts == [
        ("task-a", "environment-1", "http://sandbox.test"),
    ]
    assert client.ack_calls == [
        client.drain_calls[0],
        client.drain_calls[0],
    ]


class CommitThenLoseStopResponseEnvironment:
    stop_calls: list[tuple[str, str]] = []
    completed_operation_ids: set[str] = set()

    def __init__(
        self,
        env_id: str,
        task_name: str,
        **kwargs: Any,
    ) -> None:
        self.env_id = env_id
        self.task_name = task_name

    async def stop(self, **kwargs: Any) -> None:
        operation_id = kwargs["operation_id"]
        self.stop_calls.append((self.env_id, operation_id))
        if operation_id not in self.completed_operation_ids:
            self.completed_operation_ids.add(operation_id)
            raise RuntimeError("stop response lost after commit")


@pytest.mark.asyncio
async def test_run_lifecycle_reuses_stop_id_after_commit_response_loss() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    CommitThenLoseStopResponseEnvironment.stop_calls.clear()
    CommitThenLoseStopResponseEnvironment.completed_operation_ids.clear()
    client = RecordingCacheClient()
    client.environments = {"task-a": ["environment-1"]}
    lifecycle = TVCacheRunLifecycle(
        environment_class=CommitThenLoseStopResponseEnvironment,
        tvcache_base_url="http://cache.test",
    )
    lifecycle.client = client
    lifecycle.register_task("task-a")

    with pytest.raises(
        RuntimeError,
        match="stop response lost after commit",
    ):
        await lifecycle.close()

    await lifecycle.close()

    assert len(CommitThenLoseStopResponseEnvironment.stop_calls) == 2
    assert (
        CommitThenLoseStopResponseEnvironment.stop_calls[0]
        == CommitThenLoseStopResponseEnvironment.stop_calls[1]
    )
    assert client.ack_calls == [client.drain_calls[0]]


class CommitThenLoseEachTeardownResponseClient(RecordingCacheClient):
    def __init__(self) -> None:
        super().__init__()
        self.environments = {"task-a": ["environment-1"]}
        self.committed_drains: dict[str, list[str]] = {}
        self.committed_ack_ids: set[str] = set()

    async def drain_task(
        self,
        task_name: str,
        drain_id: str,
    ) -> list[str]:
        self.drain_calls.append((task_name, drain_id))
        if drain_id not in self.committed_drains:
            self.committed_drains[drain_id] = self.environments.pop(
                task_name,
                [],
            )
            raise httpx.ReadError(
                "drain response lost after commit",
                request=httpx.Request(
                    "POST",
                    "http://cache.test/drain_task",
                ),
            )
        return list(self.committed_drains[drain_id])

    async def ack_task_drain(
        self,
        task_name: str,
        drain_id: str,
    ) -> None:
        self.ack_calls.append((task_name, drain_id))
        if drain_id not in self.committed_ack_ids:
            self.committed_ack_ids.add(drain_id)
            raise httpx.ReadError(
                "ack response lost after commit",
                request=httpx.Request(
                    "POST",
                    "http://cache.test/ack_task_drain",
                ),
            )


class CommitThenLoseStopTransportResponseEnvironment:
    stop_calls: list[tuple[str, str]] = []
    completed_operation_ids: set[str] = set()

    def __init__(
        self,
        env_id: str,
        task_name: str,
        **kwargs: Any,
    ) -> None:
        self.env_id = env_id
        self.task_name = task_name

    async def stop(self, **kwargs: Any) -> None:
        operation_id = kwargs["operation_id"]
        self.stop_calls.append((self.env_id, operation_id))
        if operation_id not in self.completed_operation_ids:
            self.completed_operation_ids.add(operation_id)
            raise httpx.ReadError(
                "stop response lost after commit",
                request=httpx.Request(
                    "POST",
                    "http://sandbox.test/stop",
                ),
            )


@pytest.mark.asyncio
async def test_async_context_retries_transport_loss_until_teardown_converges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import utils.tvcache_run_lifecycle as lifecycle_module

    retry_delays: list[float] = []

    async def record_retry_delay(delay_seconds: float) -> None:
        retry_delays.append(delay_seconds)

    monkeypatch.setattr(
        lifecycle_module,
        "asyncio",
        SimpleNamespace(sleep=record_retry_delay),
        raising=False,
    )
    CommitThenLoseStopTransportResponseEnvironment.stop_calls.clear()
    (
        CommitThenLoseStopTransportResponseEnvironment
        .completed_operation_ids.clear()
    )
    client = CommitThenLoseEachTeardownResponseClient()
    lifecycle = lifecycle_module.TVCacheRunLifecycle(
        environment_class=CommitThenLoseStopTransportResponseEnvironment,
        tvcache_base_url="http://cache.test",
    )
    lifecycle.client = client

    async with lifecycle:
        lifecycle.register_task("task-a")

    assert len(client.drain_calls) == 2
    assert client.drain_calls[0] == client.drain_calls[1]
    assert (
        len(CommitThenLoseStopTransportResponseEnvironment.stop_calls)
        == 2
    )
    assert (
        CommitThenLoseStopTransportResponseEnvironment.stop_calls[0]
        == CommitThenLoseStopTransportResponseEnvironment.stop_calls[1]
    )
    assert client.ack_calls == [
        client.drain_calls[0],
        client.drain_calls[0],
    ]
    assert retry_delays == [1.0, 1.0, 1.0]
    assert lifecycle._pending_task_drains == {}
    assert lifecycle._pending_environment_stops == {}
    assert lifecycle._pending_drain_acks == {}
    assert client.close_calls == 4


class SemanticDrainFailureClient(RecordingCacheClient):
    async def drain_task(
        self,
        task_name: str,
        drain_id: str,
    ) -> list[str]:
        self.drain_calls.append((task_name, drain_id))
        request = httpx.Request(
            "POST",
            "http://cache.test/drain_task",
        )
        response = httpx.Response(
            status_code=409,
            request=request,
        )
        raise httpx.HTTPStatusError(
            "drain rejected",
            request=request,
            response=response,
        )


@pytest.mark.asyncio
async def test_async_context_does_not_retry_semantic_teardown_error() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    client = SemanticDrainFailureClient()
    lifecycle = TVCacheRunLifecycle(
        environment_class=RecordingEnvironment,
        tvcache_base_url="http://cache.test",
        env_kwargs={"sandbox_base_url": "http://sandbox.test"},
    )
    lifecycle.client = client

    with pytest.raises(httpx.HTTPStatusError, match="drain rejected"):
        async with lifecycle:
            lifecycle.register_task("task-a")

    assert len(client.drain_calls) == 1
    assert client.close_calls == 1
