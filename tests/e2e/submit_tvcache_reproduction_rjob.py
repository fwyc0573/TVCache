#!/usr/bin/env python3
"""Submit the TVCache real rollout through the local personal RJobBackend."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

from steptron.exp.base_exp import ResourceConfig
from steptron.utils.stepmind import spawn_tasks


REPO_DIR = Path(__file__).resolve().parents[2]
WORKER_SCRIPT = REPO_DIR / "tests/e2e/run_real_video_rollouts_h800.sh"
MOUNT_ROOT = Path("/data/ycfeng")


def main() -> None:
    if os.environ.get("STEPMIND_BACKEND", "").lower() not in {"rjob", "python", "api"}:
        raise RuntimeError("STEPMIND_BACKEND=rjob is required for local GPU submission")
    if not os.environ.get("BRAINPP_ACCESS_KEY") or not os.environ.get("BRAINPP_SECRET_KEY"):
        raise RuntimeError("Personal StepMind credentials are required")
    if not os.environ.get("KUBEBRAIN_WORKSPACE_NAME"):
        raise RuntimeError("KUBEBRAIN_WORKSPACE_NAME is required")
    if not WORKER_SCRIPT.is_file():
        raise FileNotFoundError(WORKER_SCRIPT)
    if not MOUNT_ROOT.is_dir():
        raise FileNotFoundError(MOUNT_ROOT)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_id = f"tvcache-real-rollout-h800-new-machine-{stamp}"
    os.environ.setdefault("EXP_ID", "tvcache-real-rollout-h800-new-machine")

    cfg = ResourceConfig(
        cpu=16,
        gpu=2,
        mem_gb=131,
        replica=1,
        image="hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0",
        positive_tags=["H800"],
        extra_requirements=[],
        mounts=[],
        custom_resources=[],
        envs={
            "JOB_ID": job_id,
            "REPO_DIR": str(REPO_DIR),
            "STEPCODE_CONFIG": "/data/ycfeng/tmp/stepcode-config-i-fengyicheng.json",
        },
        command="{COMMAND}",
        task_specs={"default": {"is_critical": True}},
    )
    cfg.exp_name = "tvcache-real-rollout-h800-new-machine"
    command = f"bash {WORKER_SCRIPT}"
    # Mount the local parent once so the worker can access both the worktree
    # and the copied runtime assets/config while preserving absolute paths.
    os.chdir(MOUNT_ROOT)
    workers = spawn_tasks(
        cfg,
        command=command,
        charged_group="codesign",
        use_image=True,
        code_mount_point=str(MOUNT_ROOT),
    )
    print(f"RJOB_NAME={workers.rjob.meta.name}", flush=True)
    print(f"FINAL_STATUS={workers.poll()}", flush=True)


if __name__ == "__main__":
    main()
