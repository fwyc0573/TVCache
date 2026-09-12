from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from utils.rollout_execution import RolloutExecutionResult


def build_rollout_record(
    *,
    variant: str,
    batch_index: int,
    dataset_index: int,
    rollout_index: int,
    sandbox_id: str,
    video_id: str,
    agent_loop: Any,
    execution_result: RolloutExecutionResult,
) -> dict[str, Any]:
    trajectory = execution_result.output
    total_tokens = sum(
        len(transition.ob.to_ints()) + len(transition.ac.tokens)
        for transition in trajectory.transitions
    )
    sampled_tokens = sum(
        len(transition.ac.tokens)
        for transition in trajectory.transitions
    )
    stats = agent_loop.get_stats()

    return {
        "variant": variant,
        "batch_index": batch_index,
        "dataset_index": dataset_index,
        "rollout_index": rollout_index,
        "sandbox_id": sandbox_id,
        "video_id": video_id,
        "reward": float(agent_loop.get_reward()),
        "total_tokens": total_tokens,
        "sampled_tokens": sampled_tokens,
        "elapsed_seconds": execution_result.elapsed_seconds,
        "total_calls": stats["total_calls"],
        "exact_hits": stats["exact_hits"],
        "prefix_hits": stats["prefix_hits"],
        "cache_misses": stats["cache_misses"],
        "tool_executions": stats["tool_executions"],
        "environment_forks": stats["environment_forks"],
        "cache_puts": stats["cache_puts"],
    }


def write_rollout_records(
    log_path: str | Path,
    records: Iterable[dict[str, Any]],
) -> Path:
    output_directory = Path(log_path)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "rollout_metrics.jsonl"

    with output_path.open("a", encoding="utf-8") as output_file:
        for record in records:
            output_file.write(json.dumps(record, sort_keys=True))
            output_file.write("\n")

    return output_path
