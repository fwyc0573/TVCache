"""Deterministic task-root workspace manifests for Phase 1."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import time
from typing import Iterable

from .schemas import WorkspaceEntry, WorkspaceManifest, digest_json


DEFAULT_EXCLUDES = frozenset({".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"})


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_manifest(
    root: str | Path,
    *,
    excludes: Iterable[str] = DEFAULT_EXCLUDES,
    max_file_size: int = 16 * 1024 * 1024,
) -> WorkspaceManifest:
    """Hash regular files below *root* and expose skipped state explicitly."""
    started = time.perf_counter_ns()
    root_path = Path(root).resolve()
    excluded = set(excludes)
    entries: list[WorkspaceEntry] = []
    skipped: list[dict[str, str]] = []
    unsupported: list[dict[str, str]] = []
    if not root_path.is_dir():
        raise ValueError(f"workspace root is not a directory: {root_path}")

    for current, dirs, files in os.walk(root_path, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in excluded)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            relative = path.relative_to(root_path).as_posix()
            try:
                stat = path.lstat()
            except OSError as error:
                unsupported.append({"path": relative, "reason": f"stat failed: {error}"})
                continue
            if path.is_symlink():
                unsupported.append({"path": relative, "reason": "symlink"})
                continue
            if not path.is_file():
                unsupported.append({"path": relative, "reason": "unsupported file type"})
                continue
            if stat.st_size > max_file_size:
                skipped.append({"path": relative, "reason": "oversized", "size": str(stat.st_size)})
                continue
            entries.append(WorkspaceEntry(relative, "file", stat.st_size, _file_digest(path)))

    entries.sort(key=lambda entry: entry.path)
    entry_data = [entry.__dict__ for entry in entries]
    digest = digest_json(entry_data)
    elapsed = time.perf_counter_ns() - started
    return WorkspaceManifest(
        root=str(root_path),
        entries=tuple(entries),
        skipped=tuple(skipped),
        unsupported=tuple(unsupported),
        digest=digest,
        elapsed_ns=elapsed,
    )


def changed_paths(before: WorkspaceManifest, after: WorkspaceManifest) -> tuple[str, ...]:
    before_map = {entry.path: entry for entry in before.entries}
    after_map = {entry.path: entry for entry in after.entries}
    return tuple(sorted(path for path in set(before_map) | set(after_map) if before_map.get(path) != after_map.get(path)))
