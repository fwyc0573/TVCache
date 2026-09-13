"""Small scripted filesystem tools used by the P02 smoke."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class ToolExecutor:
    def execute(self, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        raise NotImplementedError


@dataclass
class ScriptedFilesystemExecutor:
    root: Path

    def _path(self, value: str) -> Path:
        path = (self.root / value).resolve()
        if self.root.resolve() not in path.parents and path != self.root.resolve():
            raise ValueError(f"path escapes workspace: {value}")
        return path

    def execute(self, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        if tool_name == "write_file":
            path = self._path(str(arguments["path"]))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(arguments["content"]), encoding="utf-8")
            return {"path": path.relative_to(self.root).as_posix(), "written": True}
        if tool_name == "read_file":
            path = self._path(str(arguments["path"]))
            return {"path": path.relative_to(self.root).as_posix(), "content": path.read_text(encoding="utf-8")}
        if tool_name == "list_dir":
            path = self._path(str(arguments.get("path", ".")))
            return {"path": path.relative_to(self.root).as_posix() if path != self.root else ".", "entries": sorted(item.name for item in path.iterdir())}
        raise ValueError(f"unsupported P02 scripted tool: {tool_name}")
