"""Structured filesystem tools for the ReJoin observation harness."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Mapping


class ToolExecutor:
    """Interface implemented by a local tool runner."""

    def execute(self, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class ToolDeclaration:
    """Serializable declaration used by the collector and trace reviewer."""

    name: str
    support_class: str
    mutates_declared: bool
    description: str
    input_schema: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "support_class": self.support_class,
            "mutates_declared": self.mutates_declared,
            "description": self.description,
            "input_schema": dict(self.input_schema),
        }


def _schema(*, properties: Mapping[str, Any], required: tuple[str, ...] = ()) -> dict[str, Any]:
    """Create a small JSON-compatible input schema."""
    return {
        "type": "object",
        "properties": dict(properties),
        "required": list(required),
        "additionalProperties": False,
    }


S0_TOOL_DECLARATIONS: tuple[ToolDeclaration, ...] = (
    ToolDeclaration(
        "read_file", "S0", False, "Read one UTF-8 text file.",
        _schema(properties={"path": {"type": "string"}}, required=("path",)),
    ),
    ToolDeclaration(
        "write_file", "S0", True, "Write one UTF-8 text file, creating parent directories.",
        _schema(properties={"path": {"type": "string"}, "content": {"type": "string"}}, required=("path", "content")),
    ),
    ToolDeclaration(
        "list_dir", "S0", False, "List entries in one workspace directory.",
        _schema(properties={"path": {"type": "string", "default": "."}}),
    ),
    ToolDeclaration(
        "grep", "S0", False, "Search UTF-8 text files with a regular expression.",
        _schema(properties={
            "pattern": {"type": "string"},
            "path": {"type": "string", "default": "."},
            "max_results": {"type": "integer", "minimum": 1, "default": 1000},
        }, required=("pattern",)),
    ),
    ToolDeclaration(
        "stat", "S0", False, "Return metadata for one workspace path.",
        _schema(properties={"path": {"type": "string"}}, required=("path",)),
    ),
    ToolDeclaration(
        "mkdir", "S0", True, "Create one workspace directory.",
        _schema(properties={
            "path": {"type": "string"},
            "parents": {"type": "boolean", "default": True},
            "exist_ok": {"type": "boolean", "default": True},
        }, required=("path",)),
    ),
    ToolDeclaration(
        "remove", "S0", True, "Remove one workspace file or directory.",
        _schema(properties={
            "path": {"type": "string"},
            "recursive": {"type": "boolean", "default": False},
        }, required=("path",)),
    ),
)

S1_TOOL_DECLARATIONS: tuple[ToolDeclaration, ...] = (
    ToolDeclaration(
        "exec", "S1", True, "Run a shell command with a workspace directory as its working directory.",
        _schema(properties={
            "command": {"type": "string"},
            "cwd": {"type": "string", "default": "."},
            "timeout": {"type": "number", "exclusiveMinimum": 0, "default": 120},
        }, required=("command",)),
    ),
)

TOOL_DECLARATIONS: tuple[ToolDeclaration, ...] = S0_TOOL_DECLARATIONS + S1_TOOL_DECLARATIONS
_DECLARATIONS_BY_NAME = {declaration.name: declaration for declaration in TOOL_DECLARATIONS}


def tool_declarations() -> tuple[dict[str, Any], ...]:
    """Return JSON-compatible declarations for all supported tools."""
    return tuple(declaration.to_dict() for declaration in TOOL_DECLARATIONS)


def get_tool_declaration(tool_name: str) -> ToolDeclaration:
    """Return the fixed declaration for a tool name."""
    try:
        return _DECLARATIONS_BY_NAME[tool_name]
    except KeyError as error:
        raise ValueError(f"unsupported tool: {tool_name}") from error


class ToolExecutionError(ValueError):
    """Raised when a tool input or filesystem operation is invalid."""


@dataclass
class ScriptedFilesystemExecutor(ToolExecutor):
    """Run the declared tools below one task workspace root."""

    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root).expanduser().resolve()
        if not self.root.is_dir():
            raise ToolExecutionError(f"workspace root is not a directory: {self.root}")

    def _safe_path(self, value: Any, *, field: str = "path") -> tuple[Path, Path]:
        if not isinstance(value, str) or not value:
            raise ToolExecutionError(f"{field} must be a non-empty string")
        if "\x00" in value:
            raise ToolExecutionError(f"{field} contains a NUL byte")
        candidate = Path(value)
        lexical_input = candidate if candidate.is_absolute() else self.root / candidate
        # Check the path text before resolving symlinks so an external link
        # cannot be removed merely because its target is inside the workspace.
        lexical = Path(os.path.abspath(os.fspath(lexical_input)))
        if lexical != self.root and self.root not in lexical.parents:
            raise ToolExecutionError(f"path escapes workspace: {value}")
        try:
            resolved = lexical.resolve(strict=False)
        except (OSError, RuntimeError) as error:
            raise ToolExecutionError(f"invalid {field} {value!r}: {error}") from error
        if resolved != self.root and self.root not in resolved.parents:
            raise ToolExecutionError(f"path escapes workspace: {value}")
        return lexical, resolved

    def _relative(self, path: Path) -> str:
        relative = path.relative_to(self.root)
        return relative.as_posix() or "."

    @staticmethod
    def _require_mapping(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(arguments, Mapping):
            raise ToolExecutionError("tool arguments must be an object")
        return arguments

    def _read_file(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        _, path = self._safe_path(arguments.get("path"))
        if not path.is_file():
            raise ToolExecutionError(f"read_file path is not a regular file: {self._relative(path)}")
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ToolExecutionError(f"read_file failed for {self._relative(path)}: {error}") from error
        return {"path": self._relative(path), "content": content}

    def _write_file(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        _, path = self._safe_path(arguments.get("path"))
        if "content" not in arguments:
            raise ToolExecutionError("write_file requires content")
        content = arguments["content"]
        if not isinstance(content, str):
            content = str(content)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as error:
            raise ToolExecutionError(f"write_file failed for {self._relative(path)}: {error}") from error
        return {"path": self._relative(path), "written": True}

    def _list_dir(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        _, path = self._safe_path(arguments.get("path", "."))
        if not path.is_dir():
            raise ToolExecutionError(f"list_dir path is not a directory: {self._relative(path)}")
        try:
            entries = sorted(item.name for item in path.iterdir())
        except OSError as error:
            raise ToolExecutionError(f"list_dir failed for {self._relative(path)}: {error}") from error
        return {"path": self._relative(path), "entries": entries}

    def _grep(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        pattern = arguments.get("pattern")
        if not isinstance(pattern, str):
            raise ToolExecutionError("grep pattern must be a string")
        try:
            matcher = re.compile(pattern)
        except re.error as error:
            raise ToolExecutionError(f"grep pattern is invalid: {error}") from error
        _, target = self._safe_path(arguments.get("path", "."))
        if not target.exists():
            raise ToolExecutionError(f"grep path does not exist: {self._relative(target)}")
        max_results = arguments.get("max_results", 1000)
        if isinstance(max_results, bool) or not isinstance(max_results, int) or max_results < 1:
            raise ToolExecutionError("grep max_results must be a positive integer")

        if target.is_file():
            files = [target]
        elif target.is_dir():
            files = []
            for current, dirs, names in os.walk(target, followlinks=False):
                dirs[:] = sorted(dirs)
                files.extend(Path(current) / name for name in sorted(names))
        else:
            raise ToolExecutionError(f"grep path is not a regular file or directory: {self._relative(target)}")

        matches: list[dict[str, Any]] = []
        for path in sorted(files, key=lambda item: self._relative(item)):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                with path.open("r", encoding="utf-8", errors="replace") as stream:
                    for line_number, line in enumerate(stream, start=1):
                        if matcher.search(line):
                            matches.append({
                                "path": self._relative(path),
                                "line": line_number,
                                "text": line.rstrip("\n"),
                            })
                            if len(matches) >= max_results:
                                return {
                                    "path": self._relative(target),
                                    "pattern": pattern,
                                    "matches": matches,
                                    "truncated": True,
                                }
            except OSError as error:
                raise ToolExecutionError(f"grep failed for {self._relative(path)}: {error}") from error
        return {
            "path": self._relative(target),
            "pattern": pattern,
            "matches": matches,
            "truncated": False,
        }

    def _stat(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        _, path = self._safe_path(arguments.get("path"))
        try:
            info = path.stat()
        except OSError as error:
            raise ToolExecutionError(f"stat failed for {self._relative(path)}: {error}") from error
        if path.is_file():
            file_type = "file"
        elif path.is_dir():
            file_type = "directory"
        else:
            file_type = "other"
        return {
            "path": self._relative(path),
            "file_type": file_type,
            "size": info.st_size,
            "mode": info.st_mode,
        }

    def _mkdir(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        _, path = self._safe_path(arguments.get("path"))
        parents = arguments.get("parents", True)
        exist_ok = arguments.get("exist_ok", True)
        if not isinstance(parents, bool) or not isinstance(exist_ok, bool):
            raise ToolExecutionError("mkdir parents and exist_ok must be booleans")
        existed = path.exists()
        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
        except OSError as error:
            raise ToolExecutionError(f"mkdir failed for {self._relative(path)}: {error}") from error
        return {"path": self._relative(path), "created": not existed}

    def _remove(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        lexical, path = self._safe_path(arguments.get("path"))
        if path == self.root:
            raise ToolExecutionError("remove refuses to delete the workspace root")
        recursive = arguments.get("recursive", False)
        if not isinstance(recursive, bool):
            raise ToolExecutionError("remove recursive must be a boolean")
        if not lexical.exists() and not lexical.is_symlink():
            raise ToolExecutionError(f"remove path does not exist: {self._relative(lexical)}")
        try:
            if lexical.is_symlink() or lexical.is_file():
                lexical.unlink()
            elif lexical.is_dir():
                if recursive:
                    shutil.rmtree(lexical)
                else:
                    lexical.rmdir()
            else:
                raise ToolExecutionError(f"remove path has unsupported type: {self._relative(lexical)}")
        except OSError as error:
            raise ToolExecutionError(f"remove failed for {self._relative(lexical)}: {error}") from error
        return {"path": self._relative(lexical), "removed": True}

    def _exec(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        command = arguments.get("command")
        if not isinstance(command, str) or not command.strip():
            raise ToolExecutionError("exec command must be a non-empty string")
        _, cwd = self._safe_path(arguments.get("cwd", "."), field="cwd")
        if not cwd.is_dir():
            raise ToolExecutionError(f"exec cwd is not a directory: {self._relative(cwd)}")
        timeout = arguments.get("timeout", 120)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ToolExecutionError("exec timeout must be a positive number")
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            return {
                "command": command,
                "cwd": self._relative(cwd),
                "stdout": stdout,
                "stderr": stderr,
                "exit_status": -1,
                "timed_out": True,
            }
        except OSError as error:
            raise ToolExecutionError(f"exec failed to start: {error}") from error
        return {
            "command": command,
            "cwd": self._relative(cwd),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "exit_status": completed.returncode,
            "timed_out": False,
        }

    def execute(self, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        """Execute one declared tool and return JSON-compatible data."""
        get_tool_declaration(tool_name)
        arguments = self._require_mapping(arguments)
        handlers = {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_dir": self._list_dir,
            "grep": self._grep,
            "stat": self._stat,
            "mkdir": self._mkdir,
            "remove": self._remove,
            "exec": self._exec,
        }
        try:
            return handlers[tool_name](arguments)
        except ToolExecutionError:
            raise
        except (KeyError, OSError, ValueError, TypeError) as error:
            raise ToolExecutionError(f"{tool_name} failed: {error}") from error
