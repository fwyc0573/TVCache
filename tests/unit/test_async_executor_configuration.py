from __future__ import annotations

from typing import Any

import pytest

from tvclient.tools.async_semantic_stateful_executor import (
    AsyncSemanticStatefulExecutor,
)
from tvclient.tools.tool_call_env import ToolCall, ToolCallEnv


class DummyToolCall(ToolCall):
    def __init__(self, name: str, mutates: bool = True):
        self.name = name
        self.mutates = mutates

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "mutates": self.mutates}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DummyToolCall":
        return DummyToolCall(data["name"], data["mutates"])

    def will_mutate_state(self) -> bool:
        return self.mutates


class DummyEnvironment(ToolCallEnv):
    created: list[tuple[str | None, str, str]] = []
    next_fork_id = 0

    def __init__(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
        marker: str = "unset",
    ):
        self.env_id = env_id or f"{task_name}-new"
        self.task_name = task_name
        self.marker = marker
        self.stopped = False
        self.created.append((env_id, task_name, marker))

    async def stop(self, **kwargs: Any) -> None:
        self.stopped = True

    async def execute(self, tool_call: DummyToolCall, **kwargs: Any) -> str:
        return f"{self.marker}:{tool_call.name}"

    async def fork(self, **kwargs: Any) -> "DummyEnvironment":
        type(self).next_fork_id += 1
        return DummyEnvironment(
            env_id=f"{self.env_id}-fork-{self.next_fork_id}",
            task_name=self.task_name,
            marker=self.marker,
        )

    async def get_state(self, **kwargs: Any) -> dict[str, str]:
        return {"marker": self.marker}

    def get_id(self, **kwargs: Any) -> str:
        return self.env_id

    async def test(self) -> str:
        return "ok"

    async def hash(self) -> str:
        return self.env_id


class FakeCacheClient:
    async def exact_match(self, task_name: str, tool_calls: list[str]) -> bool:
        return False

    async def prefix_match(
        self, task_name: str, tool_calls: list[str]
    ) -> tuple[None, list[str]]:
        return None, []

    async def get(
        self, task_name: str, tool_calls: list[str]
    ) -> tuple[None, None, float]:
        return None, None, 0.0

    async def put(self, *args: Any, **kwargs: Any) -> list[str]:
        return []

    async def close(self) -> None:
        return None


class RootForkBank:
    def get_forked_env(self, task_name: str, parent_env_id: str) -> str | None:
        if parent_env_id == "root":
            return "warmed-root"
        return None


@pytest.mark.asyncio
async def test_executor_propagates_configuration_and_reports_cache_stats() -> None:
    DummyEnvironment.created.clear()
    executor = AsyncSemanticStatefulExecutor(
        tool_call_env_class=DummyEnvironment,
        tool_call_class=DummyToolCall,
        task_id="task-1",
        tvcache_base_url="http://cache.test:8001",
        env_kwargs={"marker": "configured"},
    )
    assert executor.client.base_url == "http://cache.test:8001"

    executor.client = FakeCacheClient()
    executor.set_fork_bank(RootForkBank())

    result = await executor.execute([DummyToolCall("prepare")])

    assert result == "configured:prepare"
    assert DummyEnvironment.created[0] == ("warmed-root", "task-1", "configured")
    assert executor.get_stats() == {
        "total_calls": 1,
        "exact_hits": 0,
        "prefix_hits": 0,
        "cache_misses": 1,
        "tool_executions": 1,
        "environment_forks": 1,
        "cache_puts": 1,
    }

    await executor.close()

