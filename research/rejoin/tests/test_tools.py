from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rejoin.tools import (  # noqa: E402
    ScriptedFilesystemExecutor,
    ToolExecutionError,
    tool_declarations,
)


class ToolSurfaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="rejoin-tools-")
        self.root = Path(self.temp_dir.name)
        self.executor = ScriptedFilesystemExecutor(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_declarations_are_complete_and_json_compatible(self) -> None:
        declarations = tool_declarations()
        self.assertEqual(
            [declaration["name"] for declaration in declarations],
            ["read_file", "write_file", "list_dir", "grep", "stat", "mkdir", "remove", "exec"],
        )
        self.assertEqual({declaration["support_class"] for declaration in declarations[:7]}, {"S0"})
        self.assertEqual(declarations[-1]["support_class"], "S1")
        self.assertTrue(all(json.dumps(declaration) for declaration in declarations))
        self.assertEqual(
            {declaration["name"] for declaration in declarations if declaration["mutates_declared"]},
            {"write_file", "mkdir", "remove", "exec"},
        )

    def test_filesystem_tools_and_exec(self) -> None:
        self.assertEqual(
            self.executor.execute("write_file", {"path": "src/input.txt", "content": "alpha\nbeta\n"}),
            {"path": "src/input.txt", "written": True},
        )
        self.assertEqual(self.executor.execute("read_file", {"path": "src/input.txt"})["content"], "alpha\nbeta\n")
        self.assertEqual(self.executor.execute("list_dir", {"path": "src"})["entries"], ["input.txt"])
        matches = self.executor.execute("grep", {"path": ".", "pattern": "beta"})
        self.assertEqual(matches["matches"][0]["path"], "src/input.txt")
        self.assertEqual(self.executor.execute("stat", {"path": "src/input.txt"})["file_type"], "file")
        self.assertTrue(self.executor.execute("mkdir", {"path": "nested"})["created"])
        result = self.executor.execute("exec", {"command": "printf output > nested/output.txt"})
        self.assertEqual(result["exit_status"], 0)
        self.assertEqual((self.root / "nested/output.txt").read_text(), "output")
        self.assertTrue(self.executor.execute("remove", {"path": "nested", "recursive": True})["removed"])

    def test_paths_cannot_escape_and_root_cannot_be_removed(self) -> None:
        for tool_name, arguments in (
            ("read_file", {"path": "../outside"}),
            ("write_file", {"path": "../outside", "content": "x"}),
            ("exec", {"command": "true", "cwd": "../"}),
        ):
            with self.subTest(tool_name=tool_name):
                with self.assertRaisesRegex(ToolExecutionError, "escapes workspace"):
                    self.executor.execute(tool_name, arguments)
        with self.assertRaisesRegex(ToolExecutionError, "workspace root"):
            self.executor.execute("remove", {"path": ".", "recursive": True})


if __name__ == "__main__":
    unittest.main()
