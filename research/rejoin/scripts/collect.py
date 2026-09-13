#!/usr/bin/env python3
"""Run one deterministic local rollout and write TraceEvent JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT / "src"))

from rejoin.schemas import TraceEvent
from rejoin.tools import ScriptedFilesystemExecutor
from rejoin.trace import TraceWriter
from rejoin.workspace import changed_paths, compute_manifest


def run(workspace: Path, output: Path) -> int:
    workspace.mkdir(parents=True, exist_ok=True)
    executor = ScriptedFilesystemExecutor(workspace)
    writer = TraceWriter(output)
    run_id = uuid4().hex
    actions = [
        ("write_file", {"path": "src/input.txt", "content": "rejoin-smoke\n"}, True),
        ("read_file", {"path": "src/input.txt"}, False),
        ("list_dir", {"path": "src"}, False),
    ]
    for seq, (tool_name, arguments, mutates) in enumerate(actions):
        before = compute_manifest(workspace)
        start_ns = time.perf_counter_ns()
        result = executor.execute(tool_name, arguments)
        end_ns = time.perf_counter_ns()
        after = compute_manifest(workspace)
        event = TraceEvent(
            run_id=run_id,
            task_id="p02-smoke",
            rollout_id="scripted-0",
            seq=seq,
            tool_name=tool_name,
            normalized_args=arguments,
            support_class="S0",
            mutates_declared=mutates,
            cwd=str(workspace),
            start_ns=start_ns,
            end_ns=end_ns,
            exit_status=0,
            result_digest=hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
            workspace_before_digest=before.digest,
            workspace_after_digest=after.digest,
            workspace_changed_paths=changed_paths(before, after),
            typed_facts={"manifest_before_ns": before.elapsed_ns, "manifest_after_ns": after.elapsed_ns},
        )
        writer.append(event)
    print(json.dumps({"run_id": run_id, "events": len(actions), "trace": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.workspace, args.output))
