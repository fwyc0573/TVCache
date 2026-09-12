from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "train"
    / "utils"
    / "provider_rollout.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "provider_rollout_under_test",
        MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_provider_rollout_executes_local_tools_and_replays_text_history() -> None:
    module = load_module()
    responses = iter(
        [
            '{"thought":"load","actions":[{"tool":"load_video_into_sandbox","inputs":"video.mp4"}],"final_answer":null}',
            '{"thought":"answer","actions":[],"final_answer":2}',
        ]
    )
    requests: list[list[dict]] = []
    executed: list[tuple[str, str]] = []

    async def complete(messages, schema):
        requests.append(list(messages))
        return next(responses)

    async def execute(name: str, argument: str):
        executed.append((name, argument))
        return "loaded"

    async def run():
        return await module.run_provider_turns(
            messages=[{"role": "user", "content": "question"}],
            num_turns=2,
            complete=complete,
            execute=execute,
            answer=2,
            stats={"total_calls": 0},
        )

    result = asyncio.run(run())
    assert result.final_answer == 2
    assert result.reward == 1.0
    assert executed == [("load_video_into_sandbox", "video.mp4")]
    assert requests[1][-1] == {
        "role": "user",
        "content": "Local tool result for load_video_into_sandbox: loaded",
    }
    assert result.tool_calls == [
        {"tool": "load_video_into_sandbox", "inputs": "video.mp4"}
    ]
