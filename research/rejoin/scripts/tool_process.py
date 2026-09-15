#!/usr/bin/env python3
"""Run one declared tool inside the collector temporary filesystem."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rejoin.tools import ScriptedFilesystemExecutor


def main() -> None:
    action = json.load(sys.stdin)
    executor = ScriptedFilesystemExecutor(Path("/app"))
    started = time.perf_counter_ns()
    try:
        result = executor.execute(action["tool"], action["arguments"])
        status = result.get("exit_status", 0)
    except (ValueError, OSError) as error:
        result = {"error": str(error)}
        status = 1
    finished = time.perf_counter_ns()
    print(json.dumps({"result": result, "exit_status": status,
                      "start_ns": started, "end_ns": finished}))


if __name__ == "__main__":
    main()
