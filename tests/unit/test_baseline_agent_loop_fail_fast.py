from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


@pytest.fixture(params=["agent_loop", "cached_agent_loop"])
def agent_loop_module(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    tinker_module = ModuleType("tinker")
    tinker_module.SamplingClient = object
    tinker_module.types = ModuleType("tinker.types")

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
    monkeypatch.delitem(sys.modules, request.param, raising=False)

    return importlib.import_module(request.param)


class OneActionResponse:
    @staticmethod
    def model_validate_json(content: str) -> SimpleNamespace:
        return SimpleNamespace(
            final_answer=None,
            actions=[SimpleNamespace(tool="query", inputs="question-1")],
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
        return SimpleNamespace(
            sequences=[SimpleNamespace(tokens=[3], logprobs=[-0.25])]
        )


def _build_loop(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    sandbox_client_class: type,
    **extra_kwargs,
):
    monkeypatch.setattr(module, "SandboxClient", sandbox_client_class)
    monkeypatch.setattr(module, "Response", OneActionResponse)

    constructor_kwargs = {
        "training_data_point": {"question": "q", "answer": "a"},
        "sampling_client": FakeSamplingClient(),
        "num_turns": 1,
        "renderer": FakeRenderer(),
    }
    constructor_kwargs.update(extra_kwargs)
    if hasattr(module, "CachedVideoAgentLoop"):
        constructor_kwargs["shared_cache"] = module.SharedToolCache()
        loop_class = module.CachedVideoAgentLoop
    else:
        loop_class = module.VideoAgentLoop

    loop = loop_class(**constructor_kwargs)
    loop.log = lambda message: None
    return loop


@pytest.mark.asyncio
async def test_baseline_agent_loop_propagates_sandbox_failure(
    monkeypatch: pytest.MonkeyPatch,
    agent_loop_module: ModuleType,
) -> None:
    class FailingSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        async def execute(self, function_name: str, argument: str):
            raise RuntimeError("sandbox backend failed")

    loop = _build_loop(
        agent_loop_module,
        monkeypatch,
        FailingSandboxClient,
    )

    with pytest.raises(RuntimeError, match="sandbox backend failed"):
        await loop.run(SimpleNamespace(max_tokens=1))


@pytest.mark.asyncio
async def test_baseline_agent_loop_raises_on_malformed_sandbox_result(
    monkeypatch: pytest.MonkeyPatch,
    agent_loop_module: ModuleType,
) -> None:
    class MalformedSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        async def execute(self, function_name: str, argument: str):
            return {"error": "missing result"}

    loop = _build_loop(
        agent_loop_module,
        monkeypatch,
        MalformedSandboxClient,
    )

    with pytest.raises(KeyError, match="result"):
        await loop.run(SimpleNamespace(max_tokens=1))


@pytest.mark.asyncio
async def test_baseline_loop_uses_configured_rollout_log_directory(
    monkeypatch: pytest.MonkeyPatch,
    agent_loop_module: ModuleType,
    tmp_path: Path,
) -> None:
    class StartingSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        async def start_sandbox(self, sandbox_id: str):
            return {"sandbox_id": sandbox_id}

    rollout_log_dir = tmp_path / agent_loop_module.__name__
    loop = _build_loop(
        agent_loop_module,
        monkeypatch,
        StartingSandboxClient,
        rollout_log_dir=str(rollout_log_dir),
    )

    await loop.start_sandbox("rollout-1")

    assert rollout_log_dir.is_dir()
    assert loop.log_file_path == str(rollout_log_dir / "rollout-1.log")


@pytest.mark.asyncio
async def test_baseline_loop_reports_numeric_tool_statistics(
    monkeypatch: pytest.MonkeyPatch,
    agent_loop_module: ModuleType,
) -> None:
    class SuccessfulSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        async def execute(self, function_name: str, argument: str):
            return {"result": "tool result"}

    loop = _build_loop(
        agent_loop_module,
        monkeypatch,
        SuccessfulSandboxClient,
    )

    await loop.run(SimpleNamespace(max_tokens=1))
    stats = loop.get_stats()

    expected_cache_puts = int(agent_loop_module.__name__ == "cached_agent_loop")
    assert stats == {
        "total_calls": 1,
        "exact_hits": 0,
        "prefix_hits": 0,
        "cache_misses": 1,
        "tool_executions": 1,
        "environment_forks": 0,
        "cache_puts": expected_cache_puts,
    }


@pytest.mark.asyncio
async def test_agent_loop_preserves_non_append_turn_transitions(
    monkeypatch: pytest.MonkeyPatch,
    agent_loop_module: ModuleType,
) -> None:
    class SuccessfulSandboxClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        async def execute(self, function_name: str, argument: str):
            return {"result": "tool result"}

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
        agent_loop_module,
        "SandboxClient",
        SuccessfulSandboxClient,
    )
    monkeypatch.setattr(agent_loop_module, "Response", TwoTurnResponse)
    constructor_kwargs = {
        "training_data_point": {"question": "q", "answer": "a"},
        "sampling_client": TwoTurnSamplingClient(),
        "num_turns": 2,
        "renderer": NonAppendRenderer(),
    }
    if hasattr(agent_loop_module, "CachedVideoAgentLoop"):
        constructor_kwargs["shared_cache"] = (
            agent_loop_module.SharedToolCache()
        )
        loop_class = agent_loop_module.CachedVideoAgentLoop
    else:
        loop_class = agent_loop_module.VideoAgentLoop
    loop = loop_class(**constructor_kwargs)
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
