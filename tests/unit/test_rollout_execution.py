from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from utils.rollout_execution import run_agent_loops


class RecordingAgentLoop:
    def __init__(
        self,
        run_behavior: str,
        stop_error: str | None = None,
        start_error: str | None = None,
    ):
        self.run_behavior = run_behavior
        self.stop_error = stop_error
        self.start_error = start_error
        self.started_with: str | None = None
        self.stop_calls = 0
        self.cancelled = False

    async def start_sandbox(self, sandbox_id: str) -> None:
        self.started_with = sandbox_id
        if self.start_error is not None:
            raise RuntimeError(self.start_error)

    async def run(self, sampling_params: Any) -> str:
        if self.run_behavior == "fail":
            raise RuntimeError("rollout failed")
        if self.run_behavior == "wait":
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                self.cancelled = True
                raise
        return "ok"

    async def stop_sandbox(self) -> None:
        self.stop_calls += 1
        if self.stop_error is not None:
            raise RuntimeError(self.stop_error)


@pytest.mark.asyncio
async def test_run_agent_loops_cancels_siblings_and_cleans_all_started_loops() -> None:
    failing_loop = RecordingAgentLoop("fail")
    waiting_loop = RecordingAgentLoop("wait")

    with pytest.raises(RuntimeError, match="rollout failed"):
        await run_agent_loops(
            [failing_loop, waiting_loop],
            ["rollout-0", "rollout-1"],
            sampling_params=SimpleNamespace(),
        )

    assert failing_loop.stop_calls == 1
    assert waiting_loop.stop_calls == 1
    assert waiting_loop.cancelled is True


@pytest.mark.asyncio
async def test_run_agent_loops_attempts_all_cleanup_and_reports_both_errors() -> None:
    failing_loop = RecordingAgentLoop("fail", stop_error="cleanup failed")
    waiting_loop = RecordingAgentLoop("wait")

    with pytest.raises(
        RuntimeError,
        match="rollout failed and 1 cleanup operation",
    ) as exc_info:
        await run_agent_loops(
            [failing_loop, waiting_loop],
            ["rollout-0", "rollout-1"],
            sampling_params=SimpleNamespace(),
        )

    assert str(exc_info.value.__cause__) == "rollout failed"
    assert failing_loop.stop_calls == 1
    assert waiting_loop.stop_calls == 1


@pytest.mark.asyncio
async def test_run_agent_loops_cleans_every_loop_after_startup_failure() -> None:
    started_loop = RecordingAgentLoop("ok")
    failing_loop = RecordingAgentLoop(
        "ok",
        start_error="startup failed",
    )
    unstarted_loop = RecordingAgentLoop("ok")

    with pytest.raises(RuntimeError, match="startup failed"):
        await run_agent_loops(
            [started_loop, failing_loop, unstarted_loop],
            ["rollout-0", "rollout-1", "rollout-2"],
            sampling_params=SimpleNamespace(),
        )

    assert started_loop.stop_calls == 1
    assert failing_loop.stop_calls == 1
    assert unstarted_loop.stop_calls == 1


@pytest.mark.asyncio
async def test_run_agent_loops_returns_ordered_output_and_elapsed_time() -> None:
    first_loop = RecordingAgentLoop("ok")
    second_loop = RecordingAgentLoop("ok")

    results = await run_agent_loops(
        [first_loop, second_loop],
        ["rollout-0", "rollout-1"],
        sampling_params=SimpleNamespace(),
    )

    assert [result.output for result in results] == ["ok", "ok"]
    assert all(result.elapsed_seconds >= 0.0 for result in results)
    assert first_loop.stop_calls == 1
    assert second_loop.stop_calls == 1
