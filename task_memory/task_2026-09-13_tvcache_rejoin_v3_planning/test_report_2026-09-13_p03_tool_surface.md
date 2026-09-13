## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded P03 structured tool declaration and local executor checks. |

# P03 Tool Surface Verification

## Execution

Environment: CPython 3.10.6 on the local checkout. The check used only the standard library and a temporary local workspace. No API, GPU, Docker, or TVCache service was used.

Commands:

```bash
python3.10 -m compileall -q research/rejoin/src research/rejoin/scripts
PYTHONPATH=research/rejoin/src python3.10 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from rejoin.tools import ScriptedFilesystemExecutor, tool_declarations, get_tool_declaration, ToolExecutionError

with TemporaryDirectory() as root:
    ex = ScriptedFilesystemExecutor(Path(root))
    names = [item["name"] for item in tool_declarations()]
    assert names == ["read_file", "write_file", "list_dir", "grep", "stat", "mkdir", "remove", "exec"]
    assert get_tool_declaration("exec").support_class == "S1"
    assert get_tool_declaration("exec").mutates_declared is True
    assert get_tool_declaration("read_file").mutates_declared is False
    ex.execute("mkdir", {"path": "src"})
    ex.execute("write_file", {"path": "src/a.txt", "content": "alpha\nbeta\n"})
    assert ex.execute("read_file", {"path": "src/a.txt"})["content"] == "alpha\nbeta\n"
    assert ex.execute("list_dir", {"path": "src"})["entries"] == ["a.txt"]
    assert ex.execute("grep", {"pattern": "beta", "path": "src"})["matches"][0]["line"] == 2
    assert ex.execute("stat", {"path": "src/a.txt"})["file_type"] == "file"
    assert ex.execute("exec", {"command": "printf exec-output > exec.txt"})["exit_status"] == 0
    assert ex.execute("read_file", {"path": "exec.txt"})["content"] == "exec-output"
    ex.execute("remove", {"path": "src/a.txt"})
    try:
        ex.execute("read_file", {"path": "../outside"})
    except ToolExecutionError:
        pass
    else:
        raise AssertionError("path escape was accepted")
print("tool_surface=PASS declarations=8 S0=7 S1=1")
PY
```

## Criteria

P03 requires seven structured S0 tools and one mutating S1 `exec`. Each declaration must expose its support class and mutation behavior, return JSON-compatible results, keep paths within the task workspace, and allow real shell execution only below that workspace.

## Evidence

PASS — compileall completed with exit status 0.

PASS — local executor assertions completed with:

```text
tool_surface=PASS declarations=8 S0=7 S1=1
```

The check covered all eight tools, a file mutation and readback, directory listing, regular-expression search, metadata lookup, shell output, file removal, and path escape rejection. This establishes local tool behavior and declaration consistency; it does not establish container isolation or provider rollout behavior.
