"""JSONL trace writing and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schemas import TraceEvent


class TraceWriter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: TraceEvent) -> None:
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            stream.write("\n")


def load_jsonl(path: str | Path) -> list[TraceEvent]:
    events: list[TraceEvent] = []
    with Path(path).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                event = TraceEvent.from_dict(json.loads(line))
            except (ValueError, TypeError, json.JSONDecodeError) as error:
                raise ValueError(f"invalid trace line {line_number}: {error}") from error
            if events and event.seq != events[-1].seq + 1:
                raise ValueError(f"trace sequence is not contiguous at line {line_number}")
            events.append(event)
    return events
