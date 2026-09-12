from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest

from tvclient.tools.async_semantic_stateful_executor import (
    AsyncSemanticStatefulExecutor,
    ExecutorLifecycleError,
    TestToolCall as ExecutorTestToolCall,
)
from tvclient.tools.tool_call_env import ToolCall, ToolCallEnv


class LifecycleToolCall(ToolCall):
    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name}

    @staticmethod
    def from_dict(data: dict[str, str]) -> "LifecycleToolCall":
        return LifecycleToolCall(data["name"])

    def will_mutate_state(self) -> bool:
        return True


class ConcreteTestToolCall(ExecutorTestToolCall):
    def will_mutate_state(self) -> bool:
        return False


class LifecycleEnvironment(ToolCallEnv):
    instances: list["LifecycleEnvironment"] = []
    stop_calls: list[str] = []
    next_id = 0
    fork_failures: set[str] = set()
    execute_failures: set[str] = set()
    get_id_failures: set[str] = set()
    stop_failures: set[str] = set()

    def __init__(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
    ):
        if env_id is None:
            type(self).next_id += 1
            env_id = f"{task_name}-environment-{self.next_id}"
        self.env_id = env_id
        self.task_name = task_name
        self.instances.append(self)

    @classmethod
    def reset(cls) -> None:
        cls.instances.clear()
        cls.stop_calls.clear()
        cls.next_id = 0
        cls.fork_failures.clear()
        cls.execute_failures.clear()
        cls.get_id_failures.clear()
        cls.stop_failures.clear()

    @classmethod
    def by_id(cls, env_id: str) -> "LifecycleEnvironment":
        return next(
            environment
            for environment in reversed(cls.instances)
            if environment.env_id == env_id
        )

    async def stop(self, **kwargs: Any) -> None:
        self.stop_calls.append(self.env_id)
        if self.env_id in self.stop_failures:
            raise RuntimeError(f"stop failed: {self.env_id}")

    async def execute(
        self,
        tool_call: LifecycleToolCall,
        **kwargs: Any,
    ) -> str:
        if self.env_id in self.execute_failures:
            raise RuntimeError(f"execute failed: {self.env_id}")
        return f"{self.env_id}:{tool_call.name}"

    async def fork(self, **kwargs: Any) -> "LifecycleEnvironment":
        if self.env_id in self.fork_failures:
            raise RuntimeError(f"fork failed: {self.env_id}")
        type(self).next_id += 1
        return LifecycleEnvironment(
            env_id=f"{self.env_id}-fork-{self.next_id}",
            task_name=self.task_name,
        )

    async def get_state(self, **kwargs: Any) -> dict[str, str]:
        return {"env_id": self.env_id}

    def get_id(self, **kwargs: Any) -> str:
        if self.env_id in self.get_id_failures:
            raise RuntimeError(f"get ID failed: {self.env_id}")
        return self.env_id

    async def test(self) -> str:
        return "test-result"

    async def hash(self) -> str:
        return self.env_id


class ScriptedCacheClient:
    def __init__(
        self,
        *,
        prefix_result: tuple[str | None, list[str]] = (None, []),
        get_result: tuple[str | None, Any | None, float | None] = (
            None,
            None,
            None,
        ),
        put_removed_envs: list[str] | None = None,
        put_error: BaseException | None = None,
        unref_error: BaseException | None = None,
        close_error: BaseException | None = None,
        store_test_result_error: BaseException | None = None,
        cached_test_result: tuple[bool, str | None] = (False, None),
    ):
        self.prefix_result = prefix_result
        self.get_result = get_result
        self.put_removed_envs = list(put_removed_envs or [])
        self.put_error = put_error
        self.unref_error = unref_error
        self.close_error = close_error
        self.store_test_result_error = store_test_result_error
        self.cached_test_result = cached_test_result
        self.unref_calls: list[tuple[str, str]] = []
        self.close_calls = 0

    async def exact_match(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> bool:
        return False

    async def prefix_match(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> tuple[str | None, list[str]]:
        return self.prefix_result

    async def get(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> tuple[str | None, Any | None, float | None]:
        return self.get_result

    async def put(self, *args: Any, **kwargs: Any) -> list[str]:
        if self.put_error is not None:
            raise self.put_error
        return self.put_removed_envs

    async def unref(self, env_id: str, task_name: str) -> bool:
        self.unref_calls.append((env_id, task_name))
        if self.unref_error is not None:
            raise self.unref_error
        return True

    async def store_test_result(
        self,
        task_name: str,
        history: list[str],
        test_result: str,
    ) -> bool:
        if self.store_test_result_error is not None:
            raise self.store_test_result_error
        return True

    async def get_test_result(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> tuple[bool, str | None]:
        return self.cached_test_result

    async def close(self) -> None:
        self.close_calls += 1
        if self.close_error is not None:
            raise self.close_error


def _new_executor(
    client: ScriptedCacheClient,
) -> AsyncSemanticStatefulExecutor:
    executor = AsyncSemanticStatefulExecutor(
        tool_call_env_class=LifecycleEnvironment,
        tool_call_class=LifecycleToolCall,
        task_id="lifecycle-task",
    )
    executor.client = client
    return executor


@pytest.fixture(autouse=True)
def _reset_lifecycle_environment() -> None:
    LifecycleEnvironment.reset()


@pytest.mark.asyncio
async def test_prefix_hit_is_not_also_counted_as_cache_miss() -> None:
    first_call = LifecycleToolCall("prepare")
    serialized_first_call = '{"name": "prepare"}'
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", [serialized_first_call]),
        get_result=("already-cached", "value", 0.1),
    )
    executor = _new_executor(client)

    result = await executor.execute(
        [first_call, LifecycleToolCall("query")]
    )
    stats = executor.get_stats()

    assert result.endswith(":query")
    assert stats["total_calls"] == 1
    assert stats["exact_hits"] == 0
    assert stats["prefix_hits"] == 1
    assert stats["cache_misses"] == 0
    assert (
        stats["exact_hits"]
        + stats["prefix_hits"]
        + stats["cache_misses"]
        == stats["total_calls"]
    )

    await executor.close()


@pytest.mark.asyncio
async def test_cached_test_result_is_classified_as_exact_hit() -> None:
    client = ScriptedCacheClient(
        cached_test_result=(True, "cached-test-result")
    )
    executor = _new_executor(client)

    result = await executor.test([LifecycleToolCall("prepare")])
    stats = executor.get_stats()

    assert result == "cached-test-result"
    assert stats["total_calls"] == 1
    assert stats["exact_hits"] == 1
    assert stats["prefix_hits"] == 0
    assert stats["cache_misses"] == 0

    await executor.close()


@pytest.mark.asyncio
async def test_full_prefix_match_releases_cache_reference() -> None:
    serialized_call = '{"name": "prepare"}'
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", [serialized_call]),
        get_result=("cached-parent", "cached-value", 0.1),
    )
    executor = _new_executor(client)

    result = await executor.execute([LifecycleToolCall("prepare")])

    assert result == "cached-value"
    assert client.unref_calls == [("cached-parent", "lifecycle-task")]
    assert executor.get_stats()["exact_hits"] == 1

    await executor.close()


@pytest.mark.asyncio
async def test_redundant_prefix_match_releases_cache_reference() -> None:
    serialized_call = '{"name": "prepare"}'
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", [serialized_call]),
        get_result=("already-cached", "value", 0.1),
    )
    executor = _new_executor(client)
    executor.executed_commands = 1
    executor.rollout_environment = LifecycleEnvironment(
        env_id="active-rollout",
        task_name="lifecycle-task",
    )

    result = await executor.execute(
        [
            LifecycleToolCall("prepare"),
            LifecycleToolCall("query"),
        ]
    )

    assert result == "active-rollout:query"
    assert client.unref_calls == [("cached-parent", "lifecycle-task")]
    assert executor.get_stats()["prefix_hits"] == 1

    await executor.close()


@pytest.mark.asyncio
async def test_cache_put_failure_stops_unpublished_fork() -> None:
    client = ScriptedCacheClient(
        put_error=RuntimeError("cache put failed")
    )
    executor = _new_executor(client)

    with pytest.raises(RuntimeError, match="cache put failed"):
        await executor.execute([LifecycleToolCall("prepare")])

    forked_environment = next(
        environment
        for environment in LifecycleEnvironment.instances
        if "-fork-" in environment.env_id
    )
    assert forked_environment.env_id in LifecycleEnvironment.stop_calls

    await executor.close()


@pytest.mark.asyncio
async def test_cache_put_and_fork_cleanup_failures_preserve_both_errors() -> None:
    forked_env_id = "lifecycle-task-environment-1-fork-2"
    client = ScriptedCacheClient(
        put_error=RuntimeError("cache put failed")
    )
    executor = _new_executor(client)
    LifecycleEnvironment.stop_failures.add(forked_env_id)

    with pytest.raises(RuntimeError) as exc_info:
        await executor.execute([LifecycleToolCall("prepare")])

    assert "cache put failed" in str(exc_info.value)
    assert "stop failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is not None
    assert "cache put failed" in str(exc_info.value.__cause__)
    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 1

    LifecycleEnvironment.stop_failures.clear()
    await executor.close()
    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 2


@pytest.mark.asyncio
async def test_prefix_fork_failure_releases_cache_reference() -> None:
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}'])
    )
    executor = _new_executor(client)
    LifecycleEnvironment.fork_failures.add("cached-parent")

    with pytest.raises(RuntimeError, match="fork failed: cached-parent"):
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert client.unref_calls == [("cached-parent", "lifecycle-task")]

    await executor.close()


@pytest.mark.asyncio
async def test_prefix_setup_cleanup_failure_is_retried_by_close() -> None:
    forked_env_id = "cached-parent-fork-1"
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}'])
    )
    executor = _new_executor(client)
    LifecycleEnvironment.get_id_failures.add(forked_env_id)
    LifecycleEnvironment.stop_failures.add(forked_env_id)

    with pytest.raises(ExecutorLifecycleError) as exc_info:
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert "get ID failed" in str(exc_info.value)
    assert f"stop failed: {forked_env_id}" in str(exc_info.value)
    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 1

    LifecycleEnvironment.get_id_failures.clear()
    LifecycleEnvironment.stop_failures.clear()
    await executor.close()

    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 2


@pytest.mark.asyncio
async def test_prefix_unref_failure_stops_unowned_fork() -> None:
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}']),
        unref_error=RuntimeError("unref failed"),
    )
    executor = _new_executor(client)

    with pytest.raises(RuntimeError, match="unref failed"):
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    forked_environment = next(
        environment
        for environment in LifecycleEnvironment.instances
        if environment.env_id.startswith("cached-parent-fork-")
    )
    assert client.unref_calls == [("cached-parent", "lifecycle-task")]
    assert forked_environment.env_id in LifecycleEnvironment.stop_calls

    await executor.close()


@pytest.mark.asyncio
async def test_prefix_unref_cleanup_failure_is_retried_by_close() -> None:
    forked_env_id = "cached-parent-fork-1"
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}']),
        unref_error=RuntimeError("unref failed"),
    )
    executor = _new_executor(client)
    LifecycleEnvironment.stop_failures.add(forked_env_id)

    with pytest.raises(ExecutorLifecycleError) as exc_info:
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert "unref failed" in str(exc_info.value)
    assert f"stop failed: {forked_env_id}" in str(exc_info.value)
    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 1

    LifecycleEnvironment.stop_failures.clear()
    await executor.close()

    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 2


@pytest.mark.asyncio
async def test_prefix_suffix_failure_stops_unowned_fork() -> None:
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}'])
    )
    executor = _new_executor(client)
    LifecycleEnvironment.execute_failures.add("cached-parent-fork-1")

    with pytest.raises(RuntimeError, match="execute failed"):
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert client.unref_calls == [("cached-parent", "lifecycle-task")]
    assert "cached-parent-fork-1" in LifecycleEnvironment.stop_calls
    assert executor.rollout_environment is None

    await executor.close()


@pytest.mark.asyncio
async def test_prefix_suffix_cleanup_failure_is_retried_by_close() -> None:
    forked_env_id = "cached-parent-fork-1"
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}'])
    )
    executor = _new_executor(client)
    LifecycleEnvironment.execute_failures.add(forked_env_id)
    LifecycleEnvironment.stop_failures.add(forked_env_id)

    with pytest.raises(ExecutorLifecycleError) as exc_info:
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert f"execute failed: {forked_env_id}" in str(exc_info.value)
    assert f"stop failed: {forked_env_id}" in str(exc_info.value)
    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 1

    LifecycleEnvironment.stop_failures.clear()
    await executor.close()

    assert LifecycleEnvironment.stop_calls.count(forked_env_id) == 2


@pytest.mark.asyncio
async def test_replacing_rollout_environment_is_transactional() -> None:
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}']),
        get_result=("already-cached", "value", 0.1),
    )
    executor = _new_executor(client)
    old_environment = LifecycleEnvironment(
        env_id="old-rollout",
        task_name="lifecycle-task",
    )
    executor.rollout_environment = old_environment
    LifecycleEnvironment.stop_failures.add("old-rollout")

    with pytest.raises(RuntimeError, match="stop failed: old-rollout"):
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert executor.rollout_environment is old_environment
    assert "cached-parent-fork-1" in LifecycleEnvironment.stop_calls
    LifecycleEnvironment.stop_failures.clear()
    await executor.close()
    assert LifecycleEnvironment.stop_calls.count("old-rollout") == 2


@pytest.mark.asyncio
async def test_replacing_rollout_environment_preserves_both_stop_failures() -> None:
    client = ScriptedCacheClient(
        prefix_result=("cached-parent", ['{"name": "prepare"}']),
        get_result=("already-cached", "value", 0.1),
    )
    executor = _new_executor(client)
    old_environment = LifecycleEnvironment(
        env_id="old-rollout",
        task_name="lifecycle-task",
    )
    executor.rollout_environment = old_environment
    LifecycleEnvironment.stop_failures.update(
        {"old-rollout", "cached-parent-fork-1"}
    )

    with pytest.raises(ExecutorLifecycleError) as exc_info:
        await executor.execute(
            [
                LifecycleToolCall("prepare"),
                LifecycleToolCall("query"),
            ]
        )

    assert "stop failed: old-rollout" in str(exc_info.value)
    assert "stop failed: cached-parent-fork-1" in str(exc_info.value)
    assert executor.rollout_environment is old_environment

    LifecycleEnvironment.stop_failures.clear()
    await executor.close()
    assert LifecycleEnvironment.stop_calls.count("old-rollout") == 2
    assert LifecycleEnvironment.stop_calls.count("cached-parent-fork-1") == 2


@pytest.mark.asyncio
async def test_removed_environment_cleanup_failure_is_not_detached() -> None:
    removed_env_id = "evicted-env"
    client = ScriptedCacheClient(put_removed_envs=["evicted-env"])
    executor = _new_executor(client)
    LifecycleEnvironment.stop_failures.add(removed_env_id)

    with pytest.raises(RuntimeError, match="stop failed: evicted-env"):
        await executor.execute([LifecycleToolCall("prepare")])

    assert LifecycleEnvironment.stop_calls.count(removed_env_id) == 1
    LifecycleEnvironment.stop_failures.clear()
    await executor.close()
    assert LifecycleEnvironment.stop_calls.count(removed_env_id) == 2


@pytest.mark.asyncio
async def test_close_attempts_environment_stop_when_client_close_fails() -> None:
    client = ScriptedCacheClient(
        close_error=RuntimeError("client close failed")
    )
    executor = _new_executor(client)
    environment = LifecycleEnvironment(
        env_id="active-rollout",
        task_name="lifecycle-task",
    )
    executor.rollout_environment = environment

    with pytest.raises(RuntimeError, match="client close failed"):
        await executor.close()

    assert "active-rollout" in LifecycleEnvironment.stop_calls


@pytest.mark.asyncio
async def test_close_removes_and_closes_owned_file_handler(
    tmp_path: Path,
) -> None:
    executor = _new_executor(ScriptedCacheClient())
    rollout_id = "owned-handler-rollout"
    executor.set_rollout_id(rollout_id, tmp_path)
    owned_handlers = [
        handler
        for handler in executor.logger.handlers
        if isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename).name == f"{rollout_id}.log"
    ]
    assert len(owned_handlers) == 1
    handler = owned_handlers[0]
    assert handler.stream is not None

    await executor.close()

    assert handler not in executor.logger.handlers
    assert handler.stream is None


@pytest.mark.asyncio
async def test_test_result_awaits_async_value_and_stops_environment() -> None:
    executor = _new_executor(ScriptedCacheClient())
    environment = LifecycleEnvironment(
        env_id="test-rollout",
        task_name="lifecycle-task",
    )
    executor.rollout_environment = environment

    result = await executor._execute_and_put(
        [ConcreteTestToolCall("")],
        0,
        environment,
    )

    assert result == "test-result"
    assert LifecycleEnvironment.stop_calls == ["test-rollout"]
    assert executor.rollout_environment is None

    await executor.close()
