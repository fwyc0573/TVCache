## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-08-17 | Recorded the rotated DeepSeek environment confirmation and remaining Tinker/GPU-asset gate. |
| 2026-08-16 | Recorded the blocked Phase 4 credential gate and confirmed no GPU worker was requested. |
| 2026-08-16 | Refreshed the authoritative Python 3.12 environment state after the 175-test CPU gate. |
| 2026-08-16 | Refreshed the post-v5-CPU-gate GPU and credential readiness state. |
| 2026-08-16 | Added the explicit-interpreter requirement for temporary Python 3.12 client syncs. |
| 2026-08-14 | Created operational and environment notes. |

# Operational Notes

- Baseline commit: `3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02`.
- Working branch: `task/tvcache-rl-reproduction`.
- Worktree: `.worktrees/tvcache-rl-reproduction`.
- Current master workspace has no visible GPU and no `conda`; GPU work must run through `rlaunch`.
- GPU commands must follow `/data/ycfeng/stepfun-env-handbook/guidence.md`.
- Do not write temporary files, logs, sockets, or caches to `/tmp`; use `/data/ycfeng/tmp` or `/data/ycfeng/tvcache_runtime`.
- Do not place credentials in scripts, tracked files, logs, or reports.
- Do not modify any `README.md`; update the existing `train/integration.md` when documentation changes are needed.
- The TVCache server must remain a single process and single worker for this task.
- `TMPDIR` must be set to a directory under `/data/ycfeng/tmp` for test commands.
- Environment or dependency failures must be reported as blockers after root-cause analysis; do not invent alternate package versions or registries.
- Every temporary client `uv sync` must pass `--python /usr/bin/python3`; otherwise uv may select its managed Python 3.10 and replace an incompatible target environment.
- After the fresh 149-test gate, the CPU master still exposes 0 GPUs and both `TINKER_API_KEY` and `OPENAI_API_KEY` are unset.
- After the fresh 175-test gate, the authoritative Python 3.12 environment is restored to 138 compatible distributions with pytest and pytest-asyncio absent.
- At Phase 4 entry, `TINKER_API_KEY`, `OPENAI_API_KEY`, and optional `HF_TOKEN` are unset; the CPU master exposes 0 GPUs, `/kubebrain/rlaunch` is available, and no predict-only or live worker request has been made.
- The verified two-H800 request must use `--charged-group=codesign --private-machine=group --positive-tags=h800 --backoff-limit=1`, with a `--predict-only` check before live allocation.
- The user confirmed on 2026-08-17 that the disclosed DeepSeek key was revoked and a replacement was written to `~/.zshrc`; only presence/mode checks are permitted, never value reads.
- After the approved provider migration, `OPENAI_API_KEY` is no longer part of the active reproduction gate. `TINKER_API_KEY` and external GPU assets remain required before worker allocation.
- The fixed EgoSchema video is persisted at `/data/ycfeng/tvcache_assets/egoschema/run-20260908/videos/0c481667-9303-4f4a-b331-0b412aaafa2d.mp4`; use the task manifest for its checksum and question metadata.
- The H200 StepCast image does not mount a generic `/models` directory. `SandboxManager` eagerly loads local VideoAgent assets, so an empty directory is not a valid runtime substitution and would produce an invalid measurement.
