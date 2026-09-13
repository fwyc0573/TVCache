#!/usr/bin/env python3
"""Reload a P02 JSONL trace and print manifest summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT / "src"))

from rejoin.trace import load_jsonl


def main(path: Path) -> int:
    events = load_jsonl(path)
    print(json.dumps({
        "events": len(events),
        "tools": [event.tool_name for event in events],
        "changed_paths": sorted({path for event in events for path in event.workspace_changed_paths}),
        "manifest_pairs": [[event.workspace_before_digest, event.workspace_after_digest] for event in events],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.trace))
