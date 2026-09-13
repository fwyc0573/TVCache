"""Stable JSON records used by the Phase 1 observation harness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping


def digest_json(value: Any) -> str:
    """Return a deterministic SHA-256 digest for a JSON-compatible value."""
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    source: str
    image_digest: str
    instruction: str
    verifier: str


@dataclass(frozen=True)
class WorkspaceEntry:
    path: str
    file_type: str
    size: int
    content_digest: str | None


@dataclass(frozen=True)
class WorkspaceManifest:
    root: str
    entries: tuple[WorkspaceEntry, ...]
    skipped: tuple[Mapping[str, str], ...] = ()
    unsupported: tuple[Mapping[str, str], ...] = ()
    digest: str = ""
    elapsed_ns: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolResult:
    value: Any
    exit_status: int = 0


@dataclass(frozen=True)
class TraceEvent:
    run_id: str
    task_id: str
    rollout_id: str
    seq: int
    tool_name: str
    normalized_args: Mapping[str, Any]
    support_class: str
    mutates_declared: bool
    cwd: str
    start_ns: int
    end_ns: int
    exit_status: int
    result_digest: str
    workspace_before_digest: str
    workspace_after_digest: str
    workspace_changed_paths: tuple[str, ...] = ()
    typed_facts: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TraceEvent":
        required = {
            "run_id", "task_id", "rollout_id", "seq", "tool_name",
            "normalized_args", "support_class", "mutates_declared", "cwd",
            "start_ns", "end_ns", "exit_status", "result_digest",
            "workspace_before_digest", "workspace_after_digest",
        }
        missing = sorted(required.difference(data))
        if missing:
            raise ValueError(f"trace event missing fields: {missing}")
        raw_args = data["normalized_args"]
        raw_changed_paths = data.get("workspace_changed_paths", ())
        if not isinstance(raw_args, Mapping):
            raise ValueError("normalized_args must be an object")
        if not isinstance(raw_changed_paths, (list, tuple)):
            raise ValueError("workspace_changed_paths must be a list")
        event = cls(
            run_id=str(data["run_id"]),
            task_id=str(data["task_id"]),
            rollout_id=str(data["rollout_id"]),
            seq=int(data["seq"]),
            tool_name=str(data["tool_name"]),
            normalized_args=dict(raw_args),
            support_class=str(data["support_class"]),
            mutates_declared=bool(data["mutates_declared"]),
            cwd=str(data["cwd"]),
            start_ns=int(data["start_ns"]),
            end_ns=int(data["end_ns"]),
            exit_status=int(data["exit_status"]),
            result_digest=str(data["result_digest"]),
            workspace_before_digest=str(data["workspace_before_digest"]),
            workspace_after_digest=str(data["workspace_after_digest"]),
            workspace_changed_paths=tuple(str(path) for path in raw_changed_paths),
            typed_facts=data.get("typed_facts"),
        )
        if event.end_ns < event.start_ns:
            raise ValueError("trace event end_ns must be >= start_ns")
        if event.support_class not in {"S0", "S1"}:
            raise ValueError("support_class must be S0 or S1")
        return event
