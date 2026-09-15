#!/usr/bin/env python3
"""Collect one real provider rollout in a fresh task image on a GPU worker."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import shutil
import shlex
import signal
import stat
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
from uuid import uuid4

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT / "src"))
from rejoin.schemas import TraceEvent, digest_json
from rejoin.tools import get_tool_declaration, tool_declarations
from rejoin.trace import load_jsonl
from rejoin.workspace import changed_paths, compute_manifest


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    part.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    part.replace(path)


def append_json(path: Path, value: object) -> None:
    with path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def prepare_filesystem(path: Path) -> Path:
    """Copy the image runtime into disposable worker storage without mounted data."""
    path.mkdir(parents=True, exist_ok=False)
    for name in ("usr", "bin", "sbin", "lib", "lib64", "etc", "app"):
        source = Path("/") / name
        if source.exists():
            subprocess.run(["cp", "-a", "--reflink=auto", str(source), str(path / name)], check=True)
    (path / "app").mkdir(exist_ok=True)
    for name in ("source_a", "source_b", "source_c"):
        source = Path("/data") / name
        if source.exists():
            (path / "data").mkdir(exist_ok=True)
            shutil.copytree(source, path / "data" / name)
    shutil.copytree(SCRIPT_ROOT, path / "rejoin")
    (path / "tmp").mkdir(mode=0o1777)
    (path / "tmp").chmod(0o1777)
    (path / "dev").mkdir()
    for name, minor in (("null", 3), ("zero", 5), ("random", 8), ("urandom", 9)):
        os.mknod(path / "dev" / name, stat.S_IFCHR | 0o666, os.makedev(1, minor))
        (path / "dev" / name).chmod(0o666)
    return path / "app"


def run_tool(action: dict, rootfs: Path, env: dict) -> dict:
    def enter() -> None:
        os.chroot(rootfs)
        os.chdir("/app")
        os.setgroups([])
        os.setgid(65534)
        os.setuid(65534)
        if ctypes.CDLL(None).prctl(38, 1, 0, 0, 0):
            raise RuntimeError("Cannot disable privilege elevation")

    process = subprocess.Popen(
        [sys.executable, "/rejoin/scripts/tool_process.py"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env, preexec_fn=enter, start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(json.dumps(action), timeout=135)
        if process.returncode:
            raise RuntimeError(f"Tool process failed ({process.returncode}): {stderr[-4000:]}")
        return json.loads(stdout)
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def complete(config: dict, key: str, messages: list, output: Path, index: int) -> tuple[dict, dict]:
    request_id = uuid4().hex
    payload = {"model": config["model"], "messages": messages,
               **config["sampling"], "max_tokens": config["max_tokens"],
               "response_format": {"type": "json_object"}, "tool_choice": "none",
               "thinking": config.get("thinking", {"type": "disabled"})}
    started = time.time_ns()
    request = urllib.request.Request(
        config["base_url"].rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
    )
    write_json(output / "provider" / f"{index:03d}.request.json",
               {"request_id": request_id, "start_epoch_ns": started, "payload": payload})
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.load(response)
        status = response.status
    ended = time.time_ns()
    write_json(output / "provider" / f"{index:03d}.response.json", body)
    choice = body["choices"][0]
    meta = {"request_id": request_id, "response_id": body.get("id"),
            "model": body.get("model"), "requested_model": config["model"],
            "base_url": config["base_url"], "sampling": config["sampling"],
            "seed_support": "accepted; deterministic behavior not established",
            "usage": body.get("usage"), "finish_reason": choice.get("finish_reason"),
            "start_epoch_ns": started, "end_epoch_ns": ended, "http_status": status}
    if choice.get("finish_reason") != "stop":
        raise ValueError(f"Provider finish reason: {choice.get('finish_reason')}")
    content = choice["message"].get("content")
    if not isinstance(content, str):
        raise ValueError("Provider message content must be a string")
    parsed = json.loads(content)
    content_shape = "object"
    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
        # Some compatible endpoints wrap a single requested action in an array.
        # Preserve the wire-shape evidence while accepting the unambiguous action.
        parsed = parsed[0]
        content_shape = "singleton_array_unwrapped"
    meta["content_shape"] = content_shape
    append_json(output / "provider.jsonl", meta)
    action = parsed
    if not isinstance(action, dict):
        raise ValueError("Provider action must be a JSON object")
    return action, meta


def collect(config: dict, config_dir: Path, report_path: Path) -> None:
    root = Path(config["cloud_root"]).resolve()
    if not root.is_relative_to("/mnt/codesign-exp/ycfeng"):
        raise ValueError("Cloud output must be inside the personal directory")
    row = config["task"]
    output = root / "rollouts/p04" / config["run_id"] / row["task_id"] / config["rollout_id"]
    output.mkdir(parents=True, exist_ok=False)
    (output / "provider").mkdir()
    write_json(output / "config.json", config)
    if row["task_id"] == "polyglot-c-py" and config["rollout_id"] == "r0":
        code_output = root / "code" / config["run_id"]
        code_output.mkdir(parents=True, exist_ok=True)
        for name, source in (("rejoin", SCRIPT_ROOT),
                             ("verifier_packages", config_dir / "public/verifier_packages")):
            part = code_output / (name + ".tar.gz.part")
            with tarfile.open(part, "w:gz") as bundle:
                bundle.add(source, arcname=name)
            part.replace(code_output / (name + ".tar.gz"))
    rootfs = Path("/data/ycfeng/tmp/rejoin-worker") / config["rollout_id"]
    workspace = prepare_filesystem(rootfs)
    for path in [workspace, *workspace.rglob("*")]:
        if not path.is_symlink():
            os.chown(path, 65534, 65534)
    actor_env = {"PATH": os.environ["PATH"], "TMPDIR": "/tmp",
                 "XDG_CACHE_HOME": "/tmp/cache", "UV_CACHE_DIR": "/tmp/uv",
                 "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8",
                 "PIP_INDEX_URL": "https://artifactory.stepfun-inc.com/artifactory/api/pypi/pypi-public/simple"}
    actor_env["UV_INDEX_URL"] = actor_env["PIP_INDEX_URL"]
    for name in ("LD_LIBRARY_PATH",):
        if name in os.environ:
            actor_env[name] = os.environ[name]
    initial = compute_manifest(workspace)
    write_json(output / "workspace.initial.json", initial.to_dict())
    for name in ("source_a", "source_b", "source_c"):
        path = Path("/data") / name
        if path.is_dir():
            write_json(output / f"input.{name}.json", compute_manifest(path).to_dict())
    instruction = (
        "Complete the task by inspecting the available files, making the necessary edits, "
        "and checking your result. All actions execute for real. Return exactly one JSON object "
        "per turn: {\"tool\":\"tool_name\",\"arguments\":{...},\"final_answer\":null}, "
        "or {\"tool\":null,\"arguments\":{},\"final_answer\":\"brief result\"} when done. "
        "The structured filesystem tools operate under /app. Use exec for compilation, "
        "program execution, binary data, or input files outside /app. Use structured tools "
        "for ordinary text reads and edits. exec uses /bin/sh; explicitly invoke bash if needed. "
        "Your writable workspace is /app; TMPDIR is available for temporary files. "
        "System packages are read-only; create a virtual environment under /app if needed. "
        "Keep each exec timeout at or below 120 seconds. Do not search for hidden tests or "
        "reference solutions. Before final_answer, remove temporary helper files and binaries "
        "unless the task explicitly requires them, and leave exactly the requested deliverables. "
        "The evaluator runs after your final answer. Available tools:\n"
        + json.dumps(tool_declarations())
    )
    messages = [{"role": "system", "content": instruction},
                {"role": "user", "content": row["instruction"]}]
    credential = json.loads((config_dir / "private/provider.json").read_text())
    key = credential["apiKey"]
    del credential
    summary = {"run_id": config["run_id"], "task_id": row["task_id"],
               "rollout_id": config["rollout_id"], "cloud_path": str(output),
               "image_digest": row["image_digest"], "source_revision": row["source_revision"],
               "started_epoch_ns": time.time_ns(), "python": sys.version,
               "gpu": subprocess.check_output(["nvidia-smi", "-L"], text=True).strip(),
               "termination": "step_limit", "tool_calls": 0, "errors": []}
    (output / "trace.jsonl").touch()
    try:
        for seq in range(config["max_steps"]):
            action, provider = complete(config, key, messages, output, seq)
            if action.get("tool") is None:
                if not isinstance(action.get("final_answer"), str) or not action["final_answer"].strip():
                    raise ValueError("Final answer is missing")
                summary.update(termination="final_answer", final_answer=action["final_answer"])
                break
            declaration = get_tool_declaration(action["tool"])
            arguments = action.get("arguments")
            if not isinstance(arguments, dict) or action.get("final_answer") is not None:
                raise ValueError("Invalid tool action")
            if declaration.name == "exec" and arguments.get("timeout", 120) > 120:
                raise ValueError("Tool timeout exceeds the recorded policy")
            before = compute_manifest(workspace)
            result = run_tool(action, rootfs, actor_env)
            after = compute_manifest(workspace)
            event = TraceEvent(
                config["run_id"], row["task_id"], config["rollout_id"], seq,
                declaration.name, arguments, declaration.support_class, declaration.mutates_declared,
                str(Path("/app") / arguments.get("cwd", ".")), result["start_ns"], result["end_ns"],
                result["exit_status"], digest_json(result["result"]), before.digest, after.digest,
                changed_paths(before, after),
                {"manifest_before_ns": before.elapsed_ns, "manifest_after_ns": after.elapsed_ns},
            )
            record = {**event.to_dict(), "provider": provider, "tool_result": result["result"]}
            append_json(output / "trace.jsonl", record)
            write_json(output / "workspaces" / f"{seq:03d}.json",
                       {"before": before.to_dict(), "after": after.to_dict()})
            summary["tool_calls"] += 1
            messages += [{"role": "assistant", "content": json.dumps(action)},
                         {"role": "user", "content": "Tool result:\n" + json.dumps(result["result"])}]
            write_json(output / "progress.json", summary)
            print("TOOL", row["task_id"], config["rollout_id"], seq, declaration.name,
                  result["exit_status"], flush=True)
    except Exception as error:
        summary["termination"] = "collection_error"
        summary["errors"].append(f"{type(error).__name__}: {error}")
        print("COLLECTION_ERROR", summary["errors"][-1], flush=True)
    del key
    write_json(output / "workspace.final.json", compute_manifest(workspace).to_dict())
    archive = output / "workspace.tar.gz.part"
    with tarfile.open(archive, "w:gz", dereference=False) as bundle:
        bundle.add(workspace, arcname="app", recursive=True)
    archive.replace(output / "workspace.tar.gz")
    tests = config_dir / "private/tasks" / row["task_id"] / "tests"
    shutil.copytree(tests, rootfs / "tests")
    verifier_env = {**actor_env, "TEST_DIR": "/tests",
                    "UV_INDEX_URL": actor_env["PIP_INDEX_URL"]}
    verifier_env.update({k: v for k, v in os.environ.items() if k.lower() in (
        "http_proxy", "https_proxy", "all_proxy", "no_proxy")})
    # P03 already proved the upstream shell setup. Execute its unchanged pytest target
    # with an offline wheel environment, leaving the actor workspace intact for archiving.
    pytest_command = [sys.executable, "-m", "pytest", "/tests/test_outputs.py",
                      "-rA", "--junitxml=/tmp/verifier.xml"]
    verifier_command = ["chroot", str(rootfs), "/bin/sh", "-c",
                        "cd /app && exec " + shlex.join(pytest_command)]
    verifier_packages = config_dir / "public/verifier_packages"
    shutil.copytree(verifier_packages, rootfs / "verifier_packages")
    verifier_env["PYTHONPATH"] = "/verifier_packages"
    try:
        with (output / "verifier.log").open("w") as log:
            verified = subprocess.run(verifier_command, cwd=workspace, env=verifier_env,
                                      stdout=log, stderr=subprocess.STDOUT, timeout=300)
        summary["verifier_exit_code"] = verified.returncode
    except subprocess.TimeoutExpired:
        summary["verifier_exit_code"] = 124
    if (rootfs / "tmp/verifier.xml").exists():
        shutil.copyfile(rootfs / "tmp/verifier.xml", output / "verifier.xml")
    events = load_jsonl(output / "trace.jsonl")
    summary.update(finished_epoch_ns=time.time_ns(), trace_reload_count=len(events),
                   verifier_command=verifier_command,
                   has_mutation=any(e.workspace_changed_paths for e in events),
                   support_classes=sorted({e.support_class for e in events}),
                   tools=[e.tool_name for e in events],
                   trajectory=digest_json([[e.tool_name, e.normalized_args] for e in events]))
    write_json(output / "COMPLETE.json", summary)
    write_json(report_path, summary)
    report_path.chmod(0o666)
    print("ROLLOUT_COMPLETE", json.dumps(summary), flush=True)
    completed = list((root / "rollouts/p04" / config["run_id"]).glob("*/r*/COMPLETE.json"))
    if len(completed) == 16:
        subprocess.run([sys.executable, str(SCRIPT_ROOT / "scripts/check_p04.py"),
                        "--cloud-root", str(root), "--run-id", config["run_id"],
                        "--report", str(config_dir / (config["run_id"] + ".smoke.json"))], check=True)
    if summary["termination"] == "collection_error":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    collect(json.loads(args.config.read_text()), args.config.parent, args.report)
