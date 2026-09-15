#!/usr/bin/env python3
"""Verify real tool effects and controller-data isolation in a small local filesystem."""

import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("collect_p04", REPO / "research/rejoin/scripts/collect_p04.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


def main() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("Run with sudo to verify the worker's chroot execution")
    root = Path(tempfile.mkdtemp(prefix="rejoin-isolation-check-", dir="/data/ycfeng/tmp"))
    try:
        runtime = Path(sys.base_prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}"
        shutil.copytree(runtime, root / runtime.relative_to("/"),
                        ignore=shutil.ignore_patterns("site-packages", "__pycache__"))
        binaries = [Path(sys.executable), Path("/bin/sh")]
        binaries += list((runtime / "lib-dynload").glob("*.so"))
        libraries = set()
        for binary in binaries:
            result = subprocess.run(["ldd", str(binary)], capture_output=True, text=True, check=True)
            libraries.update(re.findall(r"(/[^\s()]+)", result.stdout))
        for source in [*binaries[:2], *map(Path, libraries)]:
            target = root / source.relative_to("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            target.chmod(0o755)
        shutil.copytree(REPO / "research/rejoin", root / "rejoin")
        (root / "app").mkdir()
        os.chown(root / "app", 65534, 65534)
        (root / "tmp").mkdir(mode=0o1777)
        root.chmod(0o755)
        env = {"PATH": "/usr/bin:/bin", "TMPDIR": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}
        first = collector.run_tool({"tool": "write_file", "arguments": {
            "path": "value.txt", "content": "21"}}, root, env)
        second = collector.run_tool({"tool": "exec", "arguments": {"command":
            "python3 -c 'import os; from pathlib import Path; "
            "assert os.geteuid() == 65534; assert not Path(\"/tests\").exists(); "
            "assert not Path(\"/mnt\").exists(); assert not Path(\"/data\").exists(); "
            "Path(\"answer.txt\").write_text(str(int(Path(\"value.txt\").read_text()) * 2))'"}}, root, env)
        assert first["exit_status"] == second["exit_status"] == 0, (first, second)
        assert (root / "app/answer.txt").read_text() == "42"
        print(json.dumps({"status": "PASS", "python": sys.version,
                          "tools": ["write_file", "exec"], "observed_value": 42,
                          "controller_mounts_visible": False, "tool_uid": 65534}))
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    main()
