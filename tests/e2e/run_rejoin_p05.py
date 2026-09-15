#!/usr/bin/env python3
"""Prepare and run the ten-task ReJoin P05 opportunity pilot."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
TASK_MEMORY = REPO / "task_memory/task_2026-09-13_tvcache_rejoin_v3_planning"
MANIFEST = TASK_MEMORY / "rejoin_w1_candidate_manifest.jsonl"
TASKS = tuple(json.loads(line)["task_id"] for line in MANIFEST.read_text().splitlines()
              if line.strip() and json.loads(line).get("include"))


def prepare(stage: Path, run_id: str) -> list[Path]:
    public = stage / "public"
    private = stage / "private"
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    private.chmod(0o700)
    shutil.copytree(REPO / "research/rejoin", public / "rejoin", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copyfile(MANIFEST, public / "manifest.jsonl")
    run_map = TASK_MEMORY / "p05_run_map.json"
    if run_map.exists():
        shutil.copyfile(run_map, public / "run_map.json")
    shutil.copytree(REPO / "tests/e2e", public / "e2e", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    verifier_packages = Path("/data/ycfeng/tmp/rejoin-p04-control/public/verifier_packages")
    if not verifier_packages.is_dir():
        raise FileNotFoundError(f"Reusable verifier package tree is missing: {verifier_packages}")
    shutil.copytree(verifier_packages, public / "verifier_packages", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    key = json.loads(Path("/data/ycfeng/tmp/stepcode-config-i-fengyicheng.json").read_text())["apiKey"]
    secret = private / "provider.json"
    secret.touch(mode=0o600, exist_ok=True)
    secret.chmod(0o600)
    secret.write_text(json.dumps({"apiKey": key}))
    del key
    rows = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]
    configs = []
    for row in rows:
        if not row.get("include"):
            continue
        source = Path("/data/ycfeng/tmp") / ("terminal-bench-1-" + row["source_revision"]) / row["source_task_path"]
        destination = private / "tasks" / row["task_id"]
        shutil.copytree(source / "tests", destination / "tests", dirs_exist_ok=True)
        shutil.copyfile(source / "run-tests.sh", destination / "run-tests.sh")
        for index in range(4):
            config = {
                "phase": "p05", "cloud_root": "/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3",
                "run_id": run_id, "rollout_id": f"r{index}", "task": row,
                "base_url": "https://models-proxy.stepfun-inc.com", "model": "deepseek-v4-flash",
                "sampling": {"temperature": 0.8, "top_p": 0.95, "seed": 20260915 + index},
                "max_tokens": 4096, "max_steps": 96, "thinking": {"type": "disabled"},
                "max_tool_result_chars": 12000,
                "native_tools": True, "policy": "p05-native-tools-4k",
                "expected_rollouts": len(TASKS) * 4, "check_script": "check_p05.py",
                "manifest_path": str(public / "manifest.jsonl"),
            }
            path = stage / f"{run_id}.{row['task_id']}.r{index}.json"
            path.write_text(json.dumps(config, indent=2) + "\n")
            configs.append(path)
    return configs


def launch(config_path: Path) -> dict:
    config = json.loads(config_path.read_text())
    stage = config_path.parent
    stem = config_path.stem
    row = config["task"]
    completed = stage / (stem + ".rollout.json")
    worker_report = stage / (stem + ".worker.json")
    if completed.exists() and worker_report.exists():
        summary = json.loads(completed.read_text())
        worker = json.loads(worker_report.read_text())
        if summary["termination"] != "collection_error" and worker["worker_status"] == "succeeded":
            return {"task": row["task_id"], "rollout": config["rollout_id"],
                    "launcher_exit_code": 0, "reused_completed_record": True,
                    "config": str(config_path)}
    collector_command = ["python3", str(stage / "public/rejoin/scripts/collect_p04.py"),
                         "--config", str(config_path), "--report", str(stage / (stem + ".rollout.json"))]
    command = [sys.executable, str(REPO / "tests/e2e/rejoin_worker.py"),
               "--image", "hub.i.basemind.com/swe-openhands/runtime@" + row["image_digest"],
               "--source", str(stage), "--report", str(stage / (stem + ".worker.json")),
               "--exp-id", "rejoin-p05", "--",
               "bash", "-lc",
               "export PATH=/usr/local/nvidia/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin; "
               "export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:/usr/local/nvidia/lib:${LD_LIBRARY_PATH:-}; "
               "eval \"$(curl -s http://deploy.i.shaipower.com/httpproxy)\"; "
               + shlex.join(collector_command) + " > " + shlex.quote(str(stage / (stem + ".collector.log"))) + " 2>&1"]
    with (stage / (stem + ".launcher.log")).open("w") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    record = {"task": row["task_id"], "rollout": config["rollout_id"],
              "launcher_exit_code": result.returncode, "config": str(config_path)}
    print(json.dumps(record), flush=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--task", choices=TASKS)
    parser.add_argument("--rollout", choices=[f"r{i}" for i in range(4)])
    args = parser.parse_args()
    configs = prepare(args.stage, args.run_id)
    if args.prepare_only:
        print("P05_PREPARED", len(configs), flush=True)
        return 0
    selected = [p for p in configs if (not args.task or args.task in p.name)
                and (not args.rollout or p.stem.endswith("." + args.rollout))]
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        records = list(pool.map(launch, selected))
    (args.stage / (args.run_id + ".launches.json")).write_text(json.dumps(records, indent=2) + "\n")
    return int(any(row["launcher_exit_code"] for row in records))


if __name__ == "__main__":
    raise SystemExit(main())
