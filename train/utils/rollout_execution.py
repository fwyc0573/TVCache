from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class RolloutExecutionResult:
    output: Any
    elapsed_seconds: float


class RolloutLifecycleError(RuntimeError):
    def __init__(
        self,
        primary_error: BaseException | None,
        cleanup_errors: Sequence[BaseException],
    ):
        self.primary_error = primary_error
        self.cleanup_errors = list(cleanup_errors)

        cleanup_summary = "; ".join(str(error) for error in cleanup_errors)
        if primary_error is None:
            message = (
                f"{len(cleanup_errors)} cleanup operation(s) failed: "
                f"{cleanup_summary}"
            )
        else:
            message = (
                f"{primary_error} and {len(cleanup_errors)} cleanup "
                f"operation(s) failed: {cleanup_summary}"
            )
        super().__init__(message)


async def _run_with_timing(
    agent_loop: Any,
    sampling_params: Any,
) -> RolloutExecutionResult:
    start_time = time.perf_counter()
    output = await agent_loop.run(sampling_params=sampling_params)
    return RolloutExecutionResult(
        output=output,
        elapsed_seconds=time.perf_counter() - start_time,
    )


async def _run_provider_with_timing(
    agent_loop: Any,
    provider_client: Any,
) -> RolloutExecutionResult:
    start_time = time.perf_counter()
    output = await agent_loop.run_provider(provider_client)
    return RolloutExecutionResult(
        output=output,
        elapsed_seconds=time.perf_counter() - start_time,
    )


async def run_agent_loops(
    agent_loops: Sequence[Any],
    sandbox_ids: Sequence[str],
    *,
    sampling_params: Any,
) -> list[RolloutExecutionResult]:
    if len(agent_loops) != len(sandbox_ids):
        raise ValueError("agent_loops and sandbox_ids must have equal lengths")

    rollout_tasks = []
    results: list[Any] | None = None
    primary_error: BaseException | None = None

    try:
        for agent_loop, sandbox_id in zip(agent_loops, sandbox_ids):
            await agent_loop.start_sandbox(sandbox_id)

        rollout_tasks = [
            asyncio.create_task(
                _run_with_timing(agent_loop, sampling_params)
            )
            for agent_loop in agent_loops
        ]

        try:
            results = await asyncio.gather(*rollout_tasks)
        except BaseException as error:
            primary_error = error
            for task in rollout_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(
                *rollout_tasks,
                return_exceptions=True,
            )
    except BaseException as error:
        primary_error = error

    cleanup_errors: list[BaseException] = []
    for agent_loop in agent_loops:
        try:
            await agent_loop.stop_sandbox()
        except BaseException as error:
            cleanup_errors.append(error)

    if primary_error is not None:
        if cleanup_errors:
            raise RolloutLifecycleError(
                primary_error,
                cleanup_errors,
            ) from primary_error
        raise primary_error

    if cleanup_errors:
        if len(cleanup_errors) == 1:
            raise cleanup_errors[0]
        raise RolloutLifecycleError(None, cleanup_errors)

    assert results is not None
    return results


async def run_provider_agent_loops(
    agent_loops: Sequence[Any],
    sandbox_ids: Sequence[str],
    *,
    provider_client: Any,
) -> list[RolloutExecutionResult]:
    if len(agent_loops) != len(sandbox_ids):
        raise ValueError("agent_loops and sandbox_ids must have equal lengths")

    rollout_tasks: list[asyncio.Task] = []
    results: list[RolloutExecutionResult] | None = None
    primary_error: BaseException | None = None
    try:
        for agent_loop, sandbox_id in zip(agent_loops, sandbox_ids):
            await agent_loop.start_sandbox(sandbox_id)
        rollout_tasks = [
            asyncio.create_task(
                _run_provider_with_timing(agent_loop, provider_client)
            )
            for agent_loop in agent_loops
        ]
        try:
            results = await asyncio.gather(*rollout_tasks)
        except BaseException as error:
            primary_error = error
            for task in rollout_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*rollout_tasks, return_exceptions=True)
    except BaseException as error:
        primary_error = error

    cleanup_errors: list[BaseException] = []
    for agent_loop in agent_loops:
        try:
            await agent_loop.stop_sandbox()
        except BaseException as error:
            cleanup_errors.append(error)

    if primary_error is not None:
        if cleanup_errors:
            raise RolloutLifecycleError(primary_error, cleanup_errors) from primary_error
        raise primary_error
    if cleanup_errors:
        if len(cleanup_errors) == 1:
            raise cleanup_errors[0]
        raise RolloutLifecycleError(None, cleanup_errors)
    assert results is not None
    return results
