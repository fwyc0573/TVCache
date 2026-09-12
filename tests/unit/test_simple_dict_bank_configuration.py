from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from tvclient.fork.dict_bank import SimpleDictBank
from tvclient.tools.tool_call_env import ToolCallEnv


DICT_BANK_PATH = (
    Path(__file__).resolve().parents[2]
    / "tvcache/client/tvclient/fork/dict_bank.py"
)


class ConfiguredEnvironment(ToolCallEnv):
    created: list[tuple[str | None, str, str]] = []

    def __init__(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
        marker: str = "unset",
    ):
        self.env_id = env_id or f"{task_name}-root"
        self.task_name = task_name
        self.marker = marker
        self.created.append((env_id, task_name, marker))

    async def stop(self, **kwargs: Any) -> None:
        return None

    async def execute(self, tool_call: Any, **kwargs: Any) -> str:
        return "ok"

    async def fork(self, **kwargs: Any) -> "ConfiguredEnvironment":
        return ConfiguredEnvironment(
            env_id=f"{self.env_id}-fork",
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


class EmptyCacheClient:
    async def get_all_envs(self, task_name: str) -> list[str]:
        return []

    async def unref(self, env_id: str, task_name: str) -> None:
        return None

    async def close(self) -> None:
        return None


class ReferencedCacheClient(EmptyCacheClient):
    def __init__(
        self,
        env_ids: list[str],
        *,
        unref_error: BaseException | None = None,
    ) -> None:
        self.env_ids = list(env_ids)
        self.unref_error = unref_error
        self.unref_calls: list[tuple[str, str]] = []

    async def get_all_envs(self, task_name: str) -> list[str]:
        return list(self.env_ids)

    async def unref(self, env_id: str, task_name: str) -> None:
        self.unref_calls.append((env_id, task_name))
        if self.unref_error is not None:
            raise self.unref_error


class FailingRootEnvironment(ToolCallEnv):
    instances: list["FailingRootEnvironment"] = []
    fork_attempts = 0

    def __init__(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
    ):
        self.env_id = env_id or f"{task_name}-parent-{len(self.instances)}"
        self.task_name = task_name
        self.stopped = False
        self.instances.append(self)

    async def stop(self, **kwargs: Any) -> None:
        self.stopped = True

    async def execute(self, tool_call: Any, **kwargs: Any) -> str:
        return "ok"

    async def fork(self, **kwargs: Any) -> "FailingRootEnvironment":
        type(self).fork_attempts += 1
        if self.fork_attempts == 2:
            raise RuntimeError("fork failed")
        return FailingRootEnvironment(
            env_id=f"{self.task_name}-fork-{self.fork_attempts}",
            task_name=self.task_name,
        )

    async def get_state(self, **kwargs: Any) -> dict[str, str]:
        return {}

    def get_id(self, **kwargs: Any) -> str:
        return self.env_id

    async def test(self) -> str:
        return "ok"

    async def hash(self) -> str:
        return self.env_id


class WithdrawEnvironment(ToolCallEnv):
    stop_calls: list[str] = []

    def __init__(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
    ):
        self.env_id = env_id or f"{task_name}-root"

    async def stop(self, **kwargs: Any) -> None:
        self.stop_calls.append(self.env_id)
        if self.env_id == "fork-1":
            raise RuntimeError("fork stop failed")

    async def execute(self, tool_call: Any, **kwargs: Any) -> str:
        return "ok"

    async def fork(self, **kwargs: Any) -> "WithdrawEnvironment":
        return WithdrawEnvironment("forked")

    async def get_state(self, **kwargs: Any) -> dict[str, str]:
        return {}

    def get_id(self, **kwargs: Any) -> str:
        return self.env_id

    async def test(self) -> str:
        return "ok"

    async def hash(self) -> str:
        return self.env_id


@pytest.mark.asyncio
async def test_fork_bank_materializes_root_with_configuration() -> None:
    ConfiguredEnvironment.created.clear()
    SimpleDictBank.warmed_environments.clear()
    bank = SimpleDictBank(
        env_class=ConfiguredEnvironment,
        tvcache_base_url="http://cache.test:8001",
        env_kwargs={"marker": "configured"},
    )
    assert bank.cache_client.base_url == "http://cache.test:8001"
    bank.cache_client = EmptyCacheClient()

    await bank.deposit(task_name="task-1", rollout_count=1)

    assert ConfiguredEnvironment.created == [
        (None, "task-1", "configured"),
        ("task-1-root-fork", "task-1", "configured"),
    ]
    assert bank.get_forked_env("task-1", "root") == "task-1-root-fork"
    assert bank.get_stats() == {"environment_forks": 1}

    await bank.withdraw("task-1")


@pytest.mark.asyncio
async def test_fork_bank_cleans_partial_deposit_on_fork_failure() -> None:
    FailingRootEnvironment.instances.clear()
    FailingRootEnvironment.fork_attempts = 0
    SimpleDictBank.warmed_environments.clear()
    bank = SimpleDictBank(env_class=FailingRootEnvironment)
    bank.cache_client = EmptyCacheClient()

    with pytest.raises(RuntimeError, match="fork failed"):
        await bank.deposit(task_name="task-1", rollout_count=2)

    parents = [
        environment
        for environment in FailingRootEnvironment.instances
        if "-parent-" in environment.env_id
    ]
    forks = [
        environment
        for environment in FailingRootEnvironment.instances
        if "-fork-" in environment.env_id
    ]
    assert len(parents) == 2
    assert len(forks) == 1
    assert all(environment.stopped for environment in parents)
    assert all(environment.stopped for environment in forks)
    assert "task-1" not in SimpleDictBank.warmed_environments


@pytest.mark.asyncio
async def test_fork_bank_releases_references_on_partial_deposit_failure() -> None:
    FailingRootEnvironment.instances.clear()
    FailingRootEnvironment.fork_attempts = 0
    SimpleDictBank.warmed_environments.clear()
    bank = SimpleDictBank(env_class=FailingRootEnvironment)
    cache_client = ReferencedCacheClient(["cached-parent"])
    bank.cache_client = cache_client

    with pytest.raises(RuntimeError, match="fork failed"):
        await bank.deposit(task_name="task-1", rollout_count=2)

    assert cache_client.unref_calls == [("cached-parent", "task-1")]
    assert "task-1" not in SimpleDictBank.warmed_environments


@pytest.mark.asyncio
async def test_fork_bank_preserves_deposit_and_unref_failures() -> None:
    FailingRootEnvironment.instances.clear()
    FailingRootEnvironment.fork_attempts = 0
    SimpleDictBank.warmed_environments.clear()
    bank = SimpleDictBank(env_class=FailingRootEnvironment)
    cache_client = ReferencedCacheClient(
        ["cached-parent"],
        unref_error=RuntimeError("unref failed"),
    )
    bank.cache_client = cache_client

    with pytest.raises(RuntimeError) as exc_info:
        await bank.deposit(task_name="task-1", rollout_count=2)

    assert "fork failed" in str(exc_info.value)
    assert "unref failed" in str(exc_info.value)
    assert cache_client.unref_calls == [("cached-parent", "task-1")]


@pytest.mark.asyncio
async def test_fork_bank_closes_owned_cache_client() -> None:
    class RecordingCacheClient(EmptyCacheClient):
        def __init__(self) -> None:
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    bank = SimpleDictBank(env_class=ConfiguredEnvironment)
    recording_client = RecordingCacheClient()
    bank.cache_client = recording_client

    await bank.close()

    assert recording_client.closed is True


@pytest.mark.asyncio
async def test_fork_bank_withdraw_attempts_every_fork_after_failure() -> None:
    WithdrawEnvironment.stop_calls.clear()
    SimpleDictBank.warmed_environments.clear()
    SimpleDictBank.warmed_environments["task-1"] = {
        "root": ["fork-1", "fork-2"]
    }
    bank = SimpleDictBank(env_class=WithdrawEnvironment)

    with pytest.raises(RuntimeError, match="fork stop failed"):
        await bank.withdraw("task-1")

    assert WithdrawEnvironment.stop_calls == ["fork-1", "fork-2"]


@pytest.mark.asyncio
async def test_fork_bank_withdraw_retries_only_failed_forks() -> None:
    WithdrawEnvironment.stop_calls.clear()
    SimpleDictBank.warmed_environments.clear()
    SimpleDictBank.warmed_environments["task-1"] = {
        "root": ["fork-1", "fork-2"]
    }
    bank = SimpleDictBank(env_class=WithdrawEnvironment)

    with pytest.raises(RuntimeError, match="fork stop failed"):
        await bank.withdraw("task-1")

    assert WithdrawEnvironment.stop_calls == ["fork-1", "fork-2"]
    assert SimpleDictBank.warmed_environments["task-1"] == {
        "root": ["fork-1"]
    }

    with pytest.raises(RuntimeError, match="fork stop failed"):
        await bank.withdraw("task-1")

    assert WithdrawEnvironment.stop_calls == [
        "fork-1",
        "fork-2",
        "fork-1",
    ]


def test_fork_bank_import_has_no_file_logging_side_effect() -> None:
    tree = ast.parse(DICT_BANK_PATH.read_text())
    file_handler_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "FileHandler"
    ]

    assert file_handler_calls == []
