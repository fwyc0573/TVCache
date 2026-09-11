## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-11 | Initialized the new-machine reproduction record. |

# Progress

### 2026-09-11

- Status: `in-progress`.
- Completed: read canonical task recipe and mandatory StepMind runbook; confirmed current host and local disk capacity; identified all required persistent assets as missing locally.
- Completed: copied the fixed video, VideoAgent model bundle, three Python environments, HF inventory, HF cache, and a restricted StepCode config from `shai-ycfeng`; verified the video SHA-256 (`db2bb94ff43ccb040fe5fd117e19e6f907e9065d74ec7276596a9c8ba4d554af`) matches the source, and matched runtime/cache file counts except for one benign local metadata file.
- Completed: verified `tests/e2e/submit_tvcache_reproduction_rjob.py` with `py_compile`, verified the worker shell script with `bash -n`, and queried personal-auth capacity showing available H800 nodes in `codesign`.
- Pending: submit and monitor the real worker, validate artifacts, and write the final report.

### 2026-09-11 E2E completion

- Completed fresh RJob `exp-0911-180851-903367` on H800 node `gpu-h800-0443` (replica `...-cfcd2084`), creator `i-fengyicheng`; terminal phase `Succeeded`.
- Copied two previously missing remote assets from `shai-ycfeng`: `/data/ycfeng/tmp/h800-range.part` (9,976,576,392 bytes) and `/data/ycfeng/tmp/video-tower-mirror.bin` (2,114,828,105 bytes), plus the symlink target directory `/data/ycfeng/tmp/videoagent_small_clean` (6,781,002,101 bytes).
- Tool smoke passed all six operations with HTTP 200; four rollouts completed and produced the expected JSON/JSONL artifacts.
- Acceptance evidence: all rewards `1.0`, final answers `1`, non-empty tool calls, provider token totals, no-cache stats `18/13` misses, TVCache stats `tvcache-0` `10` prefix hits + `1` miss and `tvcache-1` `6` exact + `10` prefix hits, `remaining_run_sandboxes=[]`.

### Transfer and preflight evidence

- Local persistent asset sizes: `videoagent_small` 2.9G; VideoAgent runtime 5.5G; Video-LLaVA runtime 7.6G; training/provider Python 1.5G; H800 HF cache 6.3G; inventory 24K; fixed video 5.5M.
- The current worktree `.git` file references an old host path. No history mutation is required for the reproduction; the StepMind NFS mount is generated from the current host and current worktree path.
- An unauthenticated platform payload probe was rejected before creation because the default workspace principal lacks `codesign` quota; no GPU job was created. All real submission commands will use the verified personal credential files.
- First authenticated submission attempt was rejected before job creation by `typeguard`: `mem_gb=131.072` produced a float `memory_in_mb`, while `brainpp` requires an integer. Corrected the launcher to `mem_gb=131`; no GPU was allocated.
- The first created worker (`exp-0911-152816-318201`, creator `i-fengyicheng`, H800 node) reached `Failed` before business startup because the worktree-only NFS mount did not contain the copied StepCode config. The bounded replica log records `Missing STEPCODE_CONFIG=/data/ycfeng/tmp/stepcode-config-i-fengyicheng.json` and exit code 2. Root cause is confirmed; no rollout ran.
- Corrective change: the submission launcher now changes to `/data/ycfeng` before `spawn_tasks()` and mounts that local parent to the same worker path, while retaining absolute `REPO_DIR` and worker script paths. This exposes the required local assets/config through one NFS mount and keeps the source local to this machine.
- The second worker (`exp-0911-154019-913779`, creator `i-fengyicheng`, H800 node) reached the command and read the StepCode config, but exited before service readiness because the copied Python environments still referenced the missing `tvcache-runtime-py310`; its logs also showed `nvidia-smi` absent from `PATH`. Both causes are now addressed: the 88 MB runtime was copied and the worker script explicitly discovers an executable `nvidia-smi` under standard image paths, failing with a clear message if none exists.
- The third worker (`exp-0911-155436-967470`, creator `i-fengyicheng`, H800 node) confirmed the config and visual Python runtimes, then exited when the TVCache server returned exit 1. The service log was not exposed by the platform tail, so the worker script now validates the training Python before launch and prints each service log tail when a PID exits before readiness.
