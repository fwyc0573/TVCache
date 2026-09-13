from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest


SERVER_ROOT = Path(__file__).resolve().parents[2] / "tvcache" / "server"
sys.path.insert(0, str(SERVER_ROOT))

from tvcache import ImmutableEnvPrefixTreeCache
from tvclient.tools.async_semantic_stateful_executor import (
    AsyncSemanticStatefulExecutor,
)
from tvclient.tools.tool_call_env import ToolCall, ToolCallEnv


class DeterministicToolCall(ToolCall):
    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name}

    @staticmethod
    def from_dict(data: dict[str, str]) -> "DeterministicToolCall":
        return DeterministicToolCall(data["name"])

    def will_mutate_state(self) -> bool:
        return True


class ReadOnlyDeterministicToolCall(DeterministicToolCall):
    """A deterministic history entry omitted from the stateful cache chain."""

    def will_mutate_state(self) -> bool:
        return False


class DeterministicEnvironment(ToolCallEnv):
    states: dict[str, list[str]] = {}
    backend_executions: list[str] = []
    stopped_environments: list[str] = []
    next_id = 0

    def __init__(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
    ):
        if env_id is None:
            type(self).next_id += 1
            env_id = f"{task_name}-environment-{self.next_id}"
            self.states[env_id] = []
        if env_id not in self.states:
            raise KeyError(f"Unknown deterministic environment: {env_id}")
        self.env_id = env_id
        self.task_name = task_name

    async def stop(self, **kwargs: Any) -> None:
        self.stopped_environments.append(self.env_id)
        self.states.pop(self.env_id, None)

    async def execute(
        self,
        tool_call: DeterministicToolCall,
        **kwargs: Any,
    ) -> str:
        self.backend_executions.append(tool_call.name)
        self.states[self.env_id].append(tool_call.name)
        return "/".join(self.states[self.env_id])

    async def fork(self, **kwargs: Any) -> "DeterministicEnvironment":
        type(self).next_id += 1
        fork_id = f"{self.task_name}-environment-{self.next_id}"
        self.states[fork_id] = list(self.states[self.env_id])
        return DeterministicEnvironment(
            env_id=fork_id,
            task_name=self.task_name,
        )

    async def get_state(self, **kwargs: Any) -> list[str]:
        return list(self.states[self.env_id])

    def get_id(self, **kwargs: Any) -> str:
        return self.env_id

    async def test(self) -> str:
        return "ok"

    async def hash(self) -> str:
        return self.env_id


class InMemoryAsyncCacheClient:
    def __init__(self, cache: ImmutableEnvPrefixTreeCache):
        self.cache = cache

    async def exact_match(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> bool:
        found, _, _, _ = self.cache.get(task_name, tool_calls)
        return found

    async def get(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> tuple[str | None, Any | None, float | None]:
        found, env_id, value, tool_exec_time = self.cache.get(
            task_name,
            tool_calls,
        )
        if not found:
            return None, None, None
        return env_id, value, tool_exec_time

    async def prefix_match(
        self,
        task_name: str,
        tool_calls: list[str],
    ) -> tuple[str | None, list[str]]:
        found, env_id, history = self.cache.prefix_match(
            task_name,
            tool_calls,
        )
        if not found:
            return None, []
        return env_id, history

    async def put(
        self,
        task_name: str,
        history: list[str],
        env_id: str | None,
        values: list[str],
        tool_exec_times: list[float],
        start_idx: int,
    ) -> list[str]:
        success, removed = self.cache.put(
            task_name,
            history,
            env_id,
            values,
            tool_exec_times,
            start_idx,
        )
        assert success
        return removed

    async def unref(self, env_id: str, task_name: str) -> None:
        self.cache.unref(env_id, task_name)

    async def close(self) -> None:
        return None

    async def drain_task(
        self,
        task_name: str,
        drain_id: str,
    ) -> list[str]:
        return self.cache.drain_task(task_name, drain_id)

    async def ack_task_drain(
        self,
        task_name: str,
        drain_id: str,
    ) -> None:
        self.cache.ack_task_drain(task_name, drain_id)


def _new_executor(
    client: InMemoryAsyncCacheClient,
) -> AsyncSemanticStatefulExecutor:
    executor = AsyncSemanticStatefulExecutor(
        tool_call_env_class=DeterministicEnvironment,
        tool_call_class=DeterministicToolCall,
        task_id="cache-reuse-test",
    )
    executor.client = client
    return executor


@pytest.mark.asyncio
async def test_exact_hit_and_partial_prefix_reuse_backend_execution() -> None:
    DeterministicEnvironment.states.clear()
    DeterministicEnvironment.backend_executions.clear()
    DeterministicEnvironment.stopped_environments.clear()
    DeterministicEnvironment.next_id = 0
    cache = ImmutableEnvPrefixTreeCache()
    client = InMemoryAsyncCacheClient(cache)

    try:
        first_executor = _new_executor(client)
        first_result = await first_executor.execute(
            [DeterministicToolCall("prepare")]
        )
        first_backend_count = len(
            DeterministicEnvironment.backend_executions
        )

        exact_executor = _new_executor(client)
        exact_result = await exact_executor.execute(
            [DeterministicToolCall("prepare")]
        )
        exact_backend_count = len(
            DeterministicEnvironment.backend_executions
        )

        prefix_executor = _new_executor(client)
        prefix_result = await prefix_executor.execute(
            [
                DeterministicToolCall("prepare"),
                DeterministicToolCall("query"),
            ]
        )
        prefix_backend_count = len(
            DeterministicEnvironment.backend_executions
        )

        assert first_result == "prepare"
        assert exact_result == "prepare"
        assert prefix_result == "prepare/query"
        assert first_backend_count == 1
        assert exact_backend_count == 1
        assert prefix_backend_count == 2
        assert exact_executor.get_stats()["exact_hits"] == 1
        assert exact_executor.get_stats()["tool_executions"] == 0
        assert prefix_executor.get_stats()["prefix_hits"] == 1
        assert prefix_executor.get_stats()["tool_executions"] == 1
    finally:
        cache.ttl_cleanup_stop_event.set()
        cache.ttl_cleanup_thread.join(timeout=1)

    assert not cache.ttl_cleanup_thread.is_alive()


@pytest.mark.asyncio
@pytest.mark.xfail(
    strict=True,
    reason=(
        "B01: filtered stateful-prefix length is used as a cursor into "
        "the original tool-call history"
    ),
)
async def test_filtered_prefix_cursor_does_not_replay_prior_mutation() -> None:
    """Lock the mixed mutating/read-only cursor regression without fixing it."""
    DeterministicEnvironment.states.clear()
    DeterministicEnvironment.backend_executions.clear()
    DeterministicEnvironment.stopped_environments.clear()
    DeterministicEnvironment.next_id = 0
    cache = ImmutableEnvPrefixTreeCache()
    client = InMemoryAsyncCacheClient(cache)

    try:
        donor = _new_executor(client)
        await donor.execute(
            [
                DeterministicToolCall("M1"),
                ReadOnlyDeterministicToolCall("R1"),
                DeterministicToolCall("M2"),
            ]
        )
        assert DeterministicEnvironment.backend_executions == ["M1", "M2"]

        recipient = _new_executor(client)
        result = await recipient.execute(
            [
                DeterministicToolCall("M1"),
                ReadOnlyDeterministicToolCall("R1"),
                DeterministicToolCall("M2"),
                DeterministicToolCall("M3"),
            ]
        )

        # A filtered prefix [M1, M2] must map to raw index 3 after M1/R1/M2.
        assert result == "M1/M2/M3"
        assert DeterministicEnvironment.backend_executions == ["M1", "M2", "M3"]
    finally:
        cache.ttl_cleanup_stop_event.set()
        cache.ttl_cleanup_thread.join(timeout=1)

    assert not cache.ttl_cleanup_thread.is_alive()


def test_task_drain_rejects_active_references_without_mutating_cache() -> None:
    cache = ImmutableEnvPrefixTreeCache()

    try:
        success, removed = cache.put(
            "active-reference-task",
            ["prepare"],
            "environment-1",
            ["prepared"],
            [0.1],
        )
        assert success is True
        assert removed == []

        found, env_id, history = cache.prefix_match(
            "active-reference-task",
            ["prepare", "query"],
        )
        assert (found, env_id, history) == (
            True,
            "environment-1",
            ["prepare"],
        )

        with pytest.raises(RuntimeError, match="active cache reference"):
            cache.drain_task(
                "active-reference-task",
                "active-reference-drain",
            )

        assert cache.get(
            "active-reference-task",
            ["prepare"],
        )[:2] == (True, "environment-1")
        assert cache.prefix_tree_env_count["active-reference-task"] == 1
    finally:
        cache.ttl_cleanup_stop_event.set()
        cache.ttl_cleanup_thread.join(timeout=1)

    assert not cache.ttl_cleanup_thread.is_alive()


def test_task_drain_replays_detached_ids_until_ack() -> None:
    cache = ImmutableEnvPrefixTreeCache()

    try:
        for history, env_id in [
            (["prepare"], "environment-1"),
            (["inspect"], "environment-2"),
        ]:
            success, removed = cache.put(
                "retry-safe-drain-task",
                history,
                env_id,
                [history[0]],
                [0.1],
            )
            assert success is True
            assert removed == []

        first_result = cache.drain_task(
            "retry-safe-drain-task",
            "drain-operation-1",
        )
        replay_result = cache.drain_task(
            "retry-safe-drain-task",
            "drain-operation-1",
        )

        assert first_result == ["environment-1", "environment-2"]
        assert replay_result == first_result
        assert cache.prefix_tree_env_count["retry-safe-drain-task"] == 0

        with pytest.raises(RuntimeError, match="pending drain"):
            cache.drain_task(
                "retry-safe-drain-task",
                "competing-drain-operation",
            )

        assert cache.ack_task_drain(
            "retry-safe-drain-task",
            "drain-operation-1",
        ) is True
        assert cache.ack_task_drain(
            "retry-safe-drain-task",
            "drain-operation-1",
        ) is True
    finally:
        cache.ttl_cleanup_stop_event.set()
        cache.ttl_cleanup_thread.join(timeout=1)

    assert not cache.ttl_cleanup_thread.is_alive()


@pytest.mark.asyncio
async def test_run_lifecycle_drains_cache_after_parallel_reuse() -> None:
    from utils.tvcache_run_lifecycle import TVCacheRunLifecycle

    DeterministicEnvironment.states.clear()
    DeterministicEnvironment.backend_executions.clear()
    DeterministicEnvironment.stopped_environments.clear()
    DeterministicEnvironment.next_id = 0
    cache = ImmutableEnvPrefixTreeCache()
    client = InMemoryAsyncCacheClient(cache)

    try:
        publishing_executor = _new_executor(client)
        reusing_executor = _new_executor(client)

        assert await publishing_executor.execute(
            [DeterministicToolCall("prepare")]
        ) == "prepare"
        assert await reusing_executor.execute(
            [DeterministicToolCall("prepare")]
        ) == "prepare"
        assert reusing_executor.get_stats()["exact_hits"] == 1

        found, cached_env_id, _, _ = cache.get(
            "cache-reuse-test",
            ['{"name": "prepare"}'],
        )
        assert found is True
        assert cached_env_id in DeterministicEnvironment.states

        await publishing_executor.close()
        await reusing_executor.close()

        assert cached_env_id in DeterministicEnvironment.states
        assert cache.prefix_tree_env_count["cache-reuse-test"] == 1

        lifecycle = TVCacheRunLifecycle(
            environment_class=DeterministicEnvironment,
            tvcache_base_url="http://cache.test",
        )
        lifecycle.client = client
        lifecycle.register_task("cache-reuse-test")

        await lifecycle.close()

        assert cache.get(
            "cache-reuse-test",
            ['{"name": "prepare"}'],
        )[0] is False
        assert cache.prefix_tree_env_count["cache-reuse-test"] == 0
        assert DeterministicEnvironment.states == {}
        assert cached_env_id in (
            DeterministicEnvironment.stopped_environments
        )
    finally:
        cache.ttl_cleanup_stop_event.set()
        cache.ttl_cleanup_thread.join(timeout=1)

    assert not cache.ttl_cleanup_thread.is_alive()
