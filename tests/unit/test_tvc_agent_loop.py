from __future__ import annotations

import asyncio
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


@pytest.fixture
def tvc_agent_loop_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    tinker_module = ModuleType("tinker")
    tinker_types_module = ModuleType("tinker.types")
    sampling_params_module = ModuleType("tinker.types.sampling_params")
    sampling_params_module.SamplingParams = object
    tinker_module.SamplingClient = object
    tinker_module.SampleResponse = object
    tinker_module.types = tinker_types_module

    cookbook_module = ModuleType("tinker_cookbook")
    renderers_module = ModuleType("tinker_cookbook.renderers")
    renderers_module.Renderer = object
    completers_module = ModuleType("tinker_cookbook.completers")
    rl_module = ModuleType("tinker_cookbook.rl")
    rl_types_module = ModuleType("tinker_cookbook.rl.types")

    @dataclass
    class TokensWithLogprobs:
        tokens: list[int]
        maybe_logprobs: list[float] | None

        @property
        def logprobs(self) -> list[float]:
            assert self.maybe_logprobs is not None
            return self.maybe_logprobs

    @dataclass
    class Transition:
        ob: object
        ac: TokensWithLogprobs
        reward: float
        episode_done: bool

    @dataclass
    class Trajectory:
        transitions: list[Transition]
        final_ob: object

    completers_module.TokensWithLogprobs = TokensWithLogprobs
    rl_types_module.Transition = Transition
    rl_types_module.Trajectory = Trajectory

    tool_schema_module = ModuleType("tool_schema")
    tool_schema_module.Response = object

    monkeypatch.setitem(sys.modules, "tinker", tinker_module)
    monkeypatch.setitem(sys.modules, "tinker.types", tinker_types_module)
    monkeypatch.setitem(
        sys.modules,
        "tinker.types.sampling_params",
        sampling_params_module,
    )
    monkeypatch.setitem(sys.modules, "tinker_cookbook", cookbook_module)
    monkeypatch.setitem(sys.modules, "tinker_cookbook.renderers", renderers_module)
    monkeypatch.setitem(
        sys.modules,
        "tinker_cookbook.completers",
        completers_module,
    )
    monkeypatch.setitem(sys.modules, "tinker_cookbook.rl", rl_module)
    monkeypatch.setitem(
        sys.modules,
        "tinker_cookbook.rl.types",
        rl_types_module,
    )
    monkeypatch.setitem(sys.modules, "tool_schema", tool_schema_module)
    monkeypatch.delitem(sys.modules, "tvc_agent_loop", raising=False)

    return importlib.import_module("tvc_agent_loop")


def test_video_sandbox_env_uses_configured_base_url(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class RecordingSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        RecordingSandboxClient,
    )

    environment = tvc_agent_loop_module.VideoSandboxEnv(
        task_name="task-1",
        sandbox_base_url="http://sandbox.test:5000",
    )

    assert environment.sandbox_client.base_url == "http://sandbox.test:5000"


@pytest.mark.asyncio
async def test_video_sandbox_env_preserves_base_url_when_forking(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class ForkingSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None

        async def start_sandbox(self, sandbox_id: str) -> dict[str, str]:
            self.sandbox_id = sandbox_id
            return {"sandbox_id": sandbox_id}

        async def fork(self) -> dict[str, str]:
            return {"sandbox_id": "forked-environment"}

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        ForkingSandboxClient,
    )
    environment = tvc_agent_loop_module.VideoSandboxEnv(
        task_name="task-1",
        sandbox_base_url="http://sandbox.test:5000",
    )

    forked_environment = await environment.fork()

    assert (
        forked_environment.sandbox_client.base_url
        == "http://sandbox.test:5000"
    )


@pytest.mark.asyncio
async def test_video_sandbox_env_starts_only_once_for_multiple_tool_calls(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class CountingSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None
            self.start_calls = 0

        async def start_sandbox(self, sandbox_id: str) -> dict[str, str]:
            self.start_calls += 1
            self.sandbox_id = sandbox_id
            return {"sandbox_id": sandbox_id}

        async def execute(
            self,
            function_name: str,
            argument: str,
        ) -> dict[str, str]:
            return {"result": f"{function_name}:{argument}"}

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        CountingSandboxClient,
    )
    environment = tvc_agent_loop_module.VideoSandboxEnv(task_name="task-1")

    await environment.execute(
        tvc_agent_loop_module.VideoToolCall("prepare", "video-1")
    )
    await environment.execute(
        tvc_agent_loop_module.VideoToolCall("query", "question-1")
    )

    assert environment.sandbox_client.start_calls == 1


@pytest.mark.asyncio
async def test_video_sandbox_env_raises_on_malformed_tool_result(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class MalformedResultSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None

        async def start_sandbox(self, sandbox_id: str) -> dict[str, str]:
            self.sandbox_id = sandbox_id
            return {"sandbox_id": sandbox_id}

        async def execute(
            self,
            function_name: str,
            argument: str,
        ) -> dict[str, str]:
            return {"error": "missing result"}

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        MalformedResultSandboxClient,
    )
    environment = tvc_agent_loop_module.VideoSandboxEnv(task_name="task-1")

    with pytest.raises(KeyError, match="result"):
        await environment.execute(
            tvc_agent_loop_module.VideoToolCall("query", "question-1")
        )


@pytest.mark.asyncio
async def test_video_sandbox_env_propagates_stop_failure(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class FailingStopSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None

        async def stop_sandbox(
            self,
            sandbox_id: str,
            operation_id: str,
        ) -> dict[str, str]:
            raise RuntimeError("sandbox stop failed")

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        FailingStopSandboxClient,
    )
    environment = tvc_agent_loop_module.VideoSandboxEnv(task_name="task-1")

    with pytest.raises(RuntimeError, match="sandbox stop failed"):
        await environment.stop()


@pytest.mark.asyncio
async def test_video_sandbox_env_reuses_stable_stop_operation_id(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class RecordingStopSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None
            self.stop_calls: list[tuple[str, str]] = []

        async def stop_sandbox(
            self,
            sandbox_id: str,
            operation_id: str,
        ) -> dict[str, object]:
            self.stop_calls.append((sandbox_id, operation_id))
            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "operation_id": operation_id,
            }

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        RecordingStopSandboxClient,
    )
    environment = tvc_agent_loop_module.VideoSandboxEnv(
        env_id="environment-1",
        task_name="task-1",
    )

    await environment.stop()
    await environment.stop()

    assert len(environment.sandbox_client.stop_calls) == 2
    first_call, second_call = environment.sandbox_client.stop_calls
    assert first_call == second_call
    assert first_call[0] == "environment-1"
    assert first_call[1]


@pytest.mark.asyncio
async def test_video_sandbox_env_forwards_explicit_stop_operation_id(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class RecordingStopSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.sandbox_id: str | None = None
            self.stop_calls: list[tuple[str, str]] = []

        async def stop_sandbox(
            self,
            sandbox_id: str,
            operation_id: str,
        ) -> dict[str, object]:
            self.stop_calls.append((sandbox_id, operation_id))
            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "operation_id": operation_id,
            }

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SandboxClient",
        RecordingStopSandboxClient,
    )
    environment = tvc_agent_loop_module.VideoSandboxEnv(
        env_id="environment-1",
        task_name="task-1",
    )

    await environment.stop(operation_id="drain-1:environment-1")

    assert environment.sandbox_client.stop_calls == [
        ("environment-1", "drain-1:environment-1"),
    ]


def test_video_agent_loop_propagates_sandbox_configuration(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class RecordingExecutor:
        instances: list["RecordingExecutor"] = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.fork_bank = None
            self.instances.append(self)

        def set_fork_bank(self, fork_bank) -> None:
            self.fork_bank = fork_bank

    class RecordingForkBank:
        instances: list["RecordingForkBank"] = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.instances.append(self)

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        RecordingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        RecordingForkBank,
    )

    tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        sandbox_base_url="http://sandbox.test:5000",
        task_id="task-1",
    )

    assert RecordingExecutor.instances[0].kwargs["env_kwargs"] == {
        "sandbox_base_url": "http://sandbox.test:5000"
    }
    assert RecordingForkBank.instances[0].kwargs["env_kwargs"] == {
        "sandbox_base_url": "http://sandbox.test:5000"
    }


def test_video_agent_loop_propagates_tvcache_configuration(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class RecordingExecutor:
        instances: list["RecordingExecutor"] = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.instances.append(self)

        def set_fork_bank(self, fork_bank) -> None:
            return None

    class RecordingForkBank:
        instances: list["RecordingForkBank"] = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.instances.append(self)

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        RecordingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        RecordingForkBank,
    )

    tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        tvcache_base_url="http://cache.test:8001",
        task_id="task-1",
    )

    assert (
        RecordingExecutor.instances[0].kwargs["tvcache_base_url"]
        == "http://cache.test:8001"
    )
    assert (
        RecordingForkBank.instances[0].kwargs["tvcache_base_url"]
        == "http://cache.test:8001"
    )


def test_video_agent_loop_exposes_executor_statistics(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    executor_stats = {
        "total_calls": 3,
        "exact_hits": 1,
        "prefix_hits": 1,
        "cache_misses": 1,
        "tool_executions": 2,
        "environment_forks": 2,
        "cache_puts": 2,
    }
    expected_stats = executor_stats | {"environment_forks": 6}

    class RecordingExecutor:
        def __init__(self, **kwargs):
            return None

        def set_fork_bank(self, fork_bank) -> None:
            return None

        def get_stats(self) -> dict[str, int]:
            return executor_stats.copy()

    class EmptyForkBank:
        def __init__(self, **kwargs):
            return None

        def get_stats(self) -> dict[str, int]:
            return {"environment_forks": 4}

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        RecordingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        EmptyForkBank,
    )
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        task_id="task-1",
    )

    assert loop.get_stats() == expected_stats


@pytest.mark.asyncio
async def test_video_agent_loop_uses_configured_rollout_log_directory(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
    tmp_path: Path,
) -> None:
    class RecordingExecutor:
        def __init__(self, **kwargs):
            self.rollout_configuration: tuple[str, str] | None = None

        def set_fork_bank(self, fork_bank) -> None:
            return None

        def set_rollout_id(self, rollout_id: str, rollout_log_dir: str) -> None:
            self.rollout_configuration = (rollout_id, rollout_log_dir)

    class EmptyForkBank:
        def __init__(self, **kwargs):
            return None

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        RecordingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        EmptyForkBank,
    )
    rollout_log_dir = tmp_path / "tvcache-rollouts"
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        task_id="task-1",
        rollout_log_dir=str(rollout_log_dir),
    )

    await loop.start_sandbox("rollout-1")

    assert rollout_log_dir.is_dir()
    assert loop.log_file_path == str(rollout_log_dir / "rollout-1.log")
    assert loop.executor.rollout_configuration == (
        "rollout-1",
        str(rollout_log_dir),
    )


@pytest.mark.asyncio
async def test_video_agent_loop_stop_closes_resources_before_run(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
    tmp_path: Path,
) -> None:
    class RecordingExecutor:
        def __init__(self, **kwargs):
            self.closed = False
            self.close_calls = 0

        def set_fork_bank(self, fork_bank) -> None:
            return None

        def set_rollout_id(
            self,
            rollout_id: str,
            rollout_log_dir: str,
        ) -> None:
            return None

        async def close(self) -> None:
            self.close_calls += 1
            self.closed = True

    class RecordingForkBank:
        def __init__(self, **kwargs):
            self.withdraw_calls: list[str] = []
            self.closed = False
            self.close_calls = 0

        async def withdraw(self, task_name: str) -> None:
            self.withdraw_calls.append(task_name)

        async def close(self) -> None:
            self.close_calls += 1
            self.closed = True

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        RecordingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        RecordingForkBank,
    )
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        task_id="task-1",
        rollout_log_dir=str(tmp_path),
    )

    await loop.start_sandbox("rollout-1")
    await loop.stop_sandbox()
    await loop.stop_sandbox()

    assert loop.fork_generator.withdraw_calls == ["task-1"]
    assert loop.executor.closed is True
    assert loop.executor.close_calls == 1
    assert loop.fork_generator.closed is True
    assert loop.fork_generator.close_calls == 1


@pytest.mark.asyncio
async def test_video_agent_loop_run_and_stop_close_resources_once(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class RecordingExecutor:
        def __init__(self, **kwargs):
            self.close_calls = 0

        def set_fork_bank(self, fork_bank) -> None:
            return None

        async def close(self) -> None:
            self.close_calls += 1

    class RecordingForkBank:
        def __init__(self, **kwargs):
            self.withdraw_calls = 0
            self.close_calls = 0

        async def withdraw(self, task_name: str) -> None:
            self.withdraw_calls += 1

        async def close(self) -> None:
            self.close_calls += 1

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        RecordingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        RecordingForkBank,
    )
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        task_id="task-1",
    )
    expected_result = object()

    async def run_successfully(sampling_params: object) -> object:
        return expected_result

    monkeypatch.setattr(loop, "_run", run_successfully)

    assert await loop.run(object()) is expected_result
    await loop.stop_sandbox()

    assert loop.fork_generator.withdraw_calls == 1
    assert loop.executor.close_calls == 1
    assert loop.fork_generator.close_calls == 1


@pytest.mark.asyncio
async def test_video_agent_loop_stop_preserves_every_cleanup_error(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class FailingExecutor:
        def __init__(self, **kwargs):
            self.close_calls = 0

        def set_fork_bank(self, fork_bank) -> None:
            return None

        async def close(self) -> None:
            self.close_calls += 1
            raise RuntimeError("executor close failed")

    class FailingForkBank:
        def __init__(self, **kwargs):
            self.withdraw_calls = 0
            self.close_calls = 0

        async def withdraw(self, task_name: str) -> None:
            self.withdraw_calls += 1
            raise RuntimeError("withdraw failed")

        async def close(self) -> None:
            self.close_calls += 1
            raise RuntimeError("fork bank close failed")

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        FailingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        FailingForkBank,
    )
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=object(),
        num_turns=1,
        renderer=object(),
        task_id="task-1",
    )

    with pytest.raises(
        tvc_agent_loop_module.RolloutLifecycleError,
        match="3 cleanup operation",
    ) as exc_info:
        await loop.stop_sandbox()

    assert [
        str(error)
        for error in exc_info.value.cleanup_errors
    ] == [
        "withdraw failed",
        "executor close failed",
        "fork bank close failed",
    ]
    assert loop.fork_generator.withdraw_calls == 1
    assert loop.executor.close_calls == 1
    assert loop.fork_generator.close_calls == 1


@pytest.mark.asyncio
async def test_video_agent_loop_propagates_executor_failure(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class FailingExecutor:
        def __init__(self, **kwargs):
            self.closed = False

        def set_fork_bank(self, fork_bank) -> None:
            return None

        async def execute(self, tool_calls) -> str:
            raise RuntimeError("tool backend failed")

        async def close(self) -> None:
            self.closed = True

    class EmptyForkBank:
        def __init__(self, **kwargs):
            self.deposit_cancelled = False
            self.closed = False

        async def deposit(self, task_name: str, rollout_count: int) -> None:
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                self.deposit_cancelled = True
                raise

        async def close(self) -> None:
            self.closed = True

    class OneActionResponse:
        @staticmethod
        def model_validate_json(content: str) -> SimpleNamespace:
            return SimpleNamespace(
                final_answer=None,
                actions=[
                    SimpleNamespace(tool="query", inputs="question-1")
                ],
            )

    class FakePrompt:
        def to_ints(self) -> list[int]:
            return [1, 2]

    class FakeRenderer:
        def build_generation_prompt(self, messages) -> FakePrompt:
            return FakePrompt()

        def parse_response(self, tokens):
            return {"role": "assistant", "content": "one action"}, None

    class FakeSamplingClient:
        async def sample_async(self, **kwargs) -> SimpleNamespace:
            await asyncio.sleep(0)
            return SimpleNamespace(
                sequences=[
                    SimpleNamespace(tokens=[3], logprobs=[-0.25])
                ]
            )

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        FailingExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        EmptyForkBank,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "Response",
        OneActionResponse,
    )
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={
            "question": "q",
            "answer": "a",
            "next_batch": ["next-task"],
            "rollout_count": 1,
        },
        sampling_client=FakeSamplingClient(),
        num_turns=1,
        renderer=FakeRenderer(),
        task_id="task-1",
    )
    loop.log = lambda message: None

    with pytest.raises(RuntimeError, match="tool backend failed"):
        await loop.run(SimpleNamespace(max_tokens=1))

    assert loop.executor.closed is True
    assert loop.fork_generator.deposit_cancelled is True
    assert loop.fork_generator.closed is True


@pytest.mark.asyncio
async def test_video_agent_loop_sampling_failure_is_not_retried(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class NoopExecutor:
        def __init__(self, **kwargs):
            self.closed = False

        def set_fork_bank(self, fork_bank) -> None:
            return None

        async def close(self) -> None:
            self.closed = True

    class NoopForkBank:
        def __init__(self, **kwargs):
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    class FailingSamplingClient:
        def __init__(self):
            self.call_count = 0

        async def sample_async(self, **kwargs):
            self.call_count += 1
            raise RuntimeError("sampling failed")

    async def no_wait(seconds: float) -> None:
        return None

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        NoopExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        NoopForkBank,
    )
    monkeypatch.setattr(tvc_agent_loop_module.asyncio, "sleep", no_wait)
    sampling_client = FailingSamplingClient()
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=sampling_client,
        num_turns=1,
        renderer=SimpleNamespace(
            build_generation_prompt=lambda messages: SimpleNamespace(
                to_ints=lambda: [1, 2]
            )
        ),
        task_id="task-1",
    )
    loop.log = lambda message: None

    with pytest.raises(RuntimeError, match="sampling failed"):
        await loop.run(SimpleNamespace(max_tokens=1))

    assert sampling_client.call_count == 1
    assert loop.executor.closed is True
    assert loop.fork_generator.closed is True


@pytest.mark.asyncio
async def test_video_agent_loop_preserves_non_append_turn_transitions(
    monkeypatch: pytest.MonkeyPatch,
    tvc_agent_loop_module: ModuleType,
) -> None:
    class SuccessfulExecutor:
        def __init__(self, **kwargs):
            self.closed = False

        def set_fork_bank(self, fork_bank) -> None:
            return None

        async def execute(self, tool_calls) -> str:
            return "tool result"

        async def close(self) -> None:
            self.closed = True

    class NoopForkBank:
        def __init__(self, **kwargs):
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    class TwoTurnResponse:
        @staticmethod
        def model_validate_json(content: str) -> SimpleNamespace:
            if content == "action":
                return SimpleNamespace(
                    final_answer=None,
                    actions=[
                        SimpleNamespace(tool="query", inputs="question-1")
                    ],
                )
            return SimpleNamespace(final_answer="done", actions=[])

    class Prompt:
        def __init__(self, tokens: list[int]):
            self.tokens = tokens

        def to_ints(self) -> list[int]:
            return self.tokens

    class NonAppendRenderer:
        def __init__(self):
            self.prompt_index = 0

        def build_generation_prompt(self, messages) -> Prompt:
            prompts = [Prompt([10, 11]), Prompt([90, 91])]
            prompt = prompts[min(self.prompt_index, len(prompts) - 1)]
            self.prompt_index += 1
            return prompt

        def parse_response(self, tokens):
            content = "action" if tokens == [20] else "final"
            return {"role": "assistant", "content": content}, None

    class TwoTurnSamplingClient:
        def __init__(self):
            self.call_count = 0

        async def sample_async(self, **kwargs) -> SimpleNamespace:
            samples = [
                SimpleNamespace(tokens=[20], logprobs=[-0.2]),
                SimpleNamespace(tokens=[30], logprobs=[-0.3]),
            ]
            sample = samples[self.call_count]
            self.call_count += 1
            return SimpleNamespace(sequences=[sample])

    monkeypatch.setattr(
        tvc_agent_loop_module,
        "AsyncSemanticStatefulExecutor",
        SuccessfulExecutor,
    )
    monkeypatch.setattr(
        tvc_agent_loop_module,
        "SimpleDictBank",
        NoopForkBank,
    )
    monkeypatch.setattr(tvc_agent_loop_module, "Response", TwoTurnResponse)
    loop = tvc_agent_loop_module.VideoAgentLoop(
        training_data_point={"question": "q", "answer": "a"},
        sampling_client=TwoTurnSamplingClient(),
        num_turns=2,
        renderer=NonAppendRenderer(),
        task_id="task-1",
    )
    loop.log = lambda message: None

    trajectory = await loop.run(SimpleNamespace(max_tokens=1))

    assert [
        transition.ob.to_ints()
        for transition in trajectory.transitions
    ] == [[10, 11], [90, 91]]
    assert [
        transition.ac.tokens
        for transition in trajectory.transitions
    ] == [[20], [30]]
    assert [
        transition.ac.logprobs
        for transition in trajectory.transitions
    ] == [[-0.2], [-0.3]]
    assert loop.executor.closed is True
    assert loop.fork_generator.closed is True
