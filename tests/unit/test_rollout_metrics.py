from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from utils.rollout_execution import RolloutExecutionResult
from utils.rollout_metrics import build_rollout_record, write_rollout_records


class RecordingAgentLoop:
    def get_reward(self) -> float:
        return 0.5

    def get_stats(self) -> dict[str, int]:
        return {
            "total_calls": 3,
            "exact_hits": 1,
            "prefix_hits": 1,
            "cache_misses": 1,
            "tool_executions": 2,
            "environment_forks": 2,
            "cache_puts": 2,
        }


@dataclass
class Prompt:
    tokens: list[int]

    def to_ints(self) -> list[int]:
        return self.tokens


@dataclass
class Action:
    tokens: list[int]


@dataclass
class Transition:
    ob: Prompt
    ac: Action


@dataclass
class Trajectory:
    transitions: list[Transition]


def test_build_rollout_record_contains_required_numeric_evidence() -> None:
    execution_result = RolloutExecutionResult(
        output=Trajectory(
            transitions=[
                Transition(ob=Prompt([10, 11]), ac=Action([20])),
                Transition(ob=Prompt([90, 91]), ac=Action([30])),
            ]
        ),
        elapsed_seconds=1.25,
    )

    record = build_rollout_record(
        variant="tvcache",
        batch_index=2,
        dataset_index=7,
        rollout_index=1,
        sandbox_id="rollout-1",
        video_id="video-7",
        agent_loop=RecordingAgentLoop(),
        execution_result=execution_result,
    )

    assert record == {
        "variant": "tvcache",
        "batch_index": 2,
        "dataset_index": 7,
        "rollout_index": 1,
        "sandbox_id": "rollout-1",
        "video_id": "video-7",
        "reward": 0.5,
        "total_tokens": 6,
        "sampled_tokens": 2,
        "elapsed_seconds": 1.25,
        "total_calls": 3,
        "exact_hits": 1,
        "prefix_hits": 1,
        "cache_misses": 1,
        "tool_executions": 2,
        "environment_forks": 2,
        "cache_puts": 2,
    }


def test_write_rollout_records_persists_json_lines(
    tmp_path: Path,
) -> None:
    records = [{"rollout_index": 0}, {"rollout_index": 1}]

    output_path = write_rollout_records(tmp_path, records)

    assert output_path == tmp_path / "rollout_metrics.jsonl"
    assert [
        json.loads(line)
        for line in output_path.read_text().splitlines()
    ] == records
