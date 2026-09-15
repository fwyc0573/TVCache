#!/usr/bin/env python3
"""Prepare and run the fixed ReJoin P04 smoke set through local GPU launchers."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
TASK_MEMORY = REPO / "task_memory/task_2026-09-13_tvcache_rejoin_v3_planning"
SMOKE_TASKS = ("wasm-pipeline", "polyglot-c-py", "multi-source-data-merger", "recover-accuracy-log")


def prepare(stage: Path, run_id: str) -> list[Path]:
    public = stage / "public"
    private = stage / "private"
    public.mkdir(exist_ok=True)
    private.mkdir(exist_ok=True, mode=0o700)
    private.chmod(0o700)
    shutil.copytree(REPO / "research/rejoin", public / "rejoin", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    key = json.loads(Path("/data/ycfeng/tmp/stepcode-config-i-fengyicheng.json").read_text())["apiKey"]
    secret = private / "provider.json"
    secret.touch(mode=0o600, exist_ok=True)
    secret.chmod(0o600)
    secret.write_text(json.dumps({"apiKey": key}))
    del key
    rows = [json.loads(line) for line in (TASK_MEMORY / "rejoin_w1_candidate_manifest.jsonl").read_text().splitlines()]
    configs = []
    for row in rows:
        if row["task_id"] not in SMOKE_TASKS:
            continue
        source = Path("/data/ycfeng/tmp") / ("terminal-bench-1-" + row["source_revision"]) / row["source_task_path"]
        destination = private / "tasks" / row["task_id"]
        shutil.copytree(source / "tests", destination / "tests", dirs_exist_ok=True)
        shutil.copyfile(source / "run-tests.sh", destination / "run-tests.sh")
        for index in range(4):
            config = {
                "cloud_root": "/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3",
                "run_id": run_id, "rollout_id": f"r{index}", "task": row,
                "base_url": "https://models-proxy.stepfun-inc.com", "model": "deepseek-v4-flash",
                "sampling": {"temperature": 0.8, "top_p": 0.95, "seed": 20260915 + index},
                "max_tokens": 512, "max_steps": 96, "thinking": {"type": "disabled"},
                "policy": "p04-v9-disabled-thinking-512-cleanup",
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
                    "launcher_exit_code": 0, "reused_completed_record": True, "config": str(config_path)}
    collector_command = ["python3", str(stage / "public/rejoin/scripts/collect_p04.py"),
                         "--config", str(config_path), "--report", str(stage / (stem + ".rollout.json"))]
    command = [sys.executable, str(REPO / "tests/e2e/rejoin_worker.py"),
               "--image", "hub.i.basemind.com/swe-openhands/runtime@" + row["image_digest"],
               "--source", str(stage), "--report", str(stage / (stem + ".worker.json")),
               "--", "bash", "-lc",
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--await-first", action="store_true")
    parser.add_argument("--task", choices=SMOKE_TASKS)
    parser.add_argument("--rollout", choices=[f"r{i}" for i in range(4)])
    args = parser.parse_args()
    if args.await_first:
        first = args.stage / (args.run_id + ".launches.json")
        print("WAITING_FOR_FIRST_ROLLOUT", str(first), flush=True)
        while not first.exists():
            time.sleep(10)
        if any(row["launcher_exit_code"] for row in json.loads(first.read_text())):
            raise RuntimeError("The first rollout failed; inspect its retained logs before proceeding")
    configs = prepare(args.stage, args.run_id)
    if not args.prepare_only:
        selected = [p for p in configs if (not args.task or args.task in p.name)
                    and (not args.rollout or p.stem.endswith("." + args.rollout))]
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            records = list(pool.map(launch, selected))
        (args.stage / (args.run_id + ".launches.json")).write_text(json.dumps(records, indent=2) + "\n")
        raise SystemExit(any(row["launcher_exit_code"] for row in records))
    print("P04_PREPARED", len(configs), flush=True)
