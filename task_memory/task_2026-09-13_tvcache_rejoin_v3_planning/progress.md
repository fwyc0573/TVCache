## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Initialized the planning task and captured source location, repository pin, and early-stage scope. |
| 2026-09-13 | Read all 1,310 lines of v3 and extracted the research story, Phase 1/2 separation, workloads, evidence classes, gates, packets, milestones, and deferred work. |
| 2026-09-13 | Verified repository anchors for the provider client, stateful chain filtering, executor execution hook, existing tests, and the known B01 cursor issue from prior review records. |
| 2026-09-13 | Wrote `findings.md`, `design.md`, and `plan.md`; retained the planning skill's root `task_plan.md` index. |
| 2026-09-13 | Added the exact eight pilot report questions, later throughput comparison, and early execution style from v3; synchronized the task plan copy. |
| 2026-09-13 | Ran read-only document checks: source line count, task file inventory, plan copy equality, forbidden-terminology scan, and source-coverage markers all passed. Wrote the validation report and English summary. |
| 2026-09-13 | Removed the prohibited token names from the validation report while retaining the check description; the final scan returned no matches. |
| 2026-09-13 | Updated the root planning index to the skill's phase format; `check-complete.sh` reported `ALL PHASES COMPLETE (4/4)`. |
| 2026-09-13 | Follow-up execution started. P00 baseline completed with the Basemind mirror after public PyPI `hatchling` resolution timed out; P01 B01 reproducer and evidence commit completed. |
| 2026-09-15 | Completed P03 runtime preparation on H200: built ten final images, captured registry digests, ran all ten verifiers, and confirmed the eight-tool surface. |
| 2026-09-15 | Recorded P04 collection preparation, cloud persistence, and current execution evidence. |

# Status: in-progress (P04 provider smoke is pending)

## Cloud persistence and P04 continuation (2026-09-15)

- User authorized cloud persistence below `ycfeng` and automatic P04 execution if available resources settle the required inputs.
- Read the StepMind worker skill, Python RJobBackend runbook, and Docker handbook. Reuse H200/step_main and personal auth; dynamically resolve local NFS address.
- Existing StepCode configuration and the repository's tested `deepseek-v4-flash` provider route were located. A fresh preflight will settle current access before collecting rollouts.
- Storage execution and acceptance are recorded in `cloud_storage.md`. No new task-memory directory is created locally.
- Local staging completed: 67 files, 132,111,680 bytes, ten selected image digests. Fresh provider preflight returned HTTP 200 and valid JSON at `https://models-proxy.stepfun-inc.com` with `deepseek-v4-flash`; no user input is missing.
- First cloud launcher exited before job creation with `KeyError: 'EXP_ID'`. Added the experiment identifier required by the Python backend and retained the failure log under `/data/ycfeng/tmp/rejoin-p04-control/`.
- Cloud job `exp-0915-135631-557982` reached an H200 node with the correct local mount, then failed before copying files because the task image had no `nvidia-smi`. P03 logs contain the same missing executable; P03 verifier passes remain valid, while its GPU identity is supported by platform placement rather than a successful GPU command. Use the handbook's verified full worker image for storage and request NVIDIA utility support for task workers.
- The CPU kernel is 5.10 and does not provide Landlock. P04 uses a disposable filesystem with `chroot`, an unprivileged tool user, and disabled privilege elevation. Mounted controller data is absent from that filesystem. Verifier packages are prepared on the CPU through the company mirror.

## Steps

| Step | Status | Evidence |
|---|---|---|
| Establish task scope and source path | completed | Read user request, repository listing, `draft-plan/legacy/AGENTS.md`, and the requested source path. |
| Extract complete v3 plan structure and evidence rules | completed | Recorded the two research questions, W1/W2, A/B/C/U/N, trace/manifest rules, gates, P00–P08, M0/M1, and exclusions. |
| Verify repository anchors | completed | Confirmed `ProviderChatClient`, `_get_serialized_stateful_chain()`, `_execute_commands()`, existing provider/prefix tests, and B01 review evidence. |
| Write durable task plan and design records | completed | Created `requirements.md`, `findings.md`, `design.md`, and `plan.md` under the new task directory. |
| Verify documents and close planning phase | completed | Document path, source coverage, forbidden-terminology, plan-copy, validation report, and summary checks are complete. |
| P00 CPU baseline capture | completed | Mirror-backed suite: `184 passed, 2 failed, 1 xfailed, 1 error in 1.64s`; raw logs and environment record under `p00_baseline/`. |
| P01 B01 cursor issue lock | completed | Strict `xfail` reproducer; `--runxfail` observed `M1/M2/M2/M3`; commits `cce8520` and `30ff78f`. |
| P02 minimal research harness | completed | `research/rejoin/` package, direct tests, JSONL trace, and workspace manifest checks passed. |
| P03 cohort/runtime/tool surface | completed | Ten-task manifest, pinned source, final image digests, ten verifier passes, four-task smoke readiness, and eight-tool implementation are complete. |

## Errors and Adjustments

| Issue | Attempt | Resolution |
|---|---|---|
| Initial `find`/`sed` read targeted a legacy path and reported no file | 1 | Located the requested file directly under `draft-plan/`; recorded legacy path as reference-only. |
| Public PyPI dependency resolution timed out on `hatchling` | 1 | Read `task_memory/env_handbook.md`, verified the Basemind mirror with HTTP 200, reran successfully through the mirror. |
| Mirror run changed `tvcache/client/uv.lock` URLs | 1 | Restored the lock file to HEAD after the test run; mirror evidence is retained in the P00 logs. |

| P02 trace field and direct execution import needed alignment | 1 | Standardized the field as `normalized_args`, added source checkout import setup, reran compile, rollout, reload, and assertions successfully. |

## P02 evidence

- Implemented the lightweight package under `research/rejoin/` with schemas, JSONL trace IO, task-root workspace manifests, scripted filesystem tools, and a provider interface reserved for P04.
- Direct Python 3.10 syntax/import check passed.
- Scripted rollout produced three events: `write_file`, `read_file`, and `list_dir`.
- Reload and assertions passed: three contiguous events, `src/input.txt` changed on the first event, before/after digests were present, and read/list events kept the same manifest digest.
- Raw trace and smoke summary are under `p02_harness/`; detailed evidence is in `test_report_2026-09-13_p02_harness.md`.

## Next decision

P02 is complete. P03 may now freeze the W1 cohort and S0/S1 tool surface. P04 collector preparation may proceed in parallel, but real provider execution remains gated by P03 inputs and the documented smoke gate.

## P03 audit (2026-09-13 checkpoint)

- Read-only inventory found no approved W1 manifest containing task IDs, source revisions, image digests, task roots, and verifiers.
- The existing EgoSchema manifest is a video asset record and cannot serve as the W1 filesystem cohort.
- At that checkpoint P03 remained pending for runtime image and verifier completion; no provider, GPU, Docker, or serving execution had started yet.

## P03 continuation: source and runtime readiness (2026-09-13 checkpoint)

- Read and accepted the ten-task W1 candidate manifest and four-task smoke subset supplied by the user.
- Checked out `harbor-framework/terminal-bench-1` at `d28711d0da2675d0bb1d56de45ae5df6082438a3` under `/data/ycfeng/tmp/terminal-bench-1-d28711d0da2675d0bb1d56de45ae5df6082438a3`; detached checkout has no local edits.
- Verified every selected task has a Dockerfile and `run-tests.sh`; all ten verifier scripts pass `bash -n`.
- Image digests were still null at that checkpoint. The host had no Docker-compatible executable or `/var/run/docker.sock`, so image build and in-container verifier execution could not proceed there.
- Deleted only task-generated Python caches and old P00/P02 temporary directories that are not needed for later evidence. Pinned Terminal-Bench source and required task memory records were retained.
- Implemented seven structured S0 tools (`read_file`, `write_file`, `list_dir`, `grep`, `stat`, `mkdir`, `remove`) and one mutating S1 `exec`, with serializable declarations and workspace path checks. Direct local checks passed for all eight tools.
- P03 runtime readiness report records the exact source revision, ten verifier syntax passes, and the Docker runtime blocker.

## Next decision at the 2026-09-13 checkpoint

P03 source pinning and local tool surface were complete. The recorded next step was to obtain a supported container runtime, then build images and run verifiers before starting P04 smoke.

## P03 runtime/verifier completion (2026-09-15)

### Change

Completed the runtime portion of P03 using the supplied ten-task W1 cohort. The CPU master had no usable Docker runtime, so StepBPS built the images and StepMind Python `RJobBackend` ran the solution and verifier on an H200 worker. The final runner was `/data/ycfeng/tmp/run_rejoin_verifier_worker_v5.py`.

### Commands and evidence

```bash
python3 /data/ycfeng/tmp/rejoin_query_digests.py
python3 /data/ycfeng/tmp/update_rejoin_manifest.py
```

The digest query returned HTTP 200 and a `Docker-Content-Digest` for all ten final tags. The manifest update checked every selected row for a non-empty `sha256:` digest, the pinned source revision, a successful build record, and a passing verifier record. Build Dockerfiles and metadata are under `/data/ycfeng/tmp/rejoin-p03-stepbps-dockerfiles/` and `/data/ycfeng/tmp/stepbps_*`.

### Observed result

All ten tasks have `solution_exit_code=0`, `verifier_exit_code=0`, and worker status `succeeded`:

| Task | Verifier result | GPU worker job |
|---|---:|---|
| `wasm-pipeline` | 3 passed | `exp-0915-042621-073453` |
| `polyglot-c-py` | 1 passed | `exp-0915-042702-548718` |
| `extract-elf` | 2 passed | `exp-0915-042738-970432` |
| `multi-source-data-merger` | 3 passed | `exp-0915-041241-577015` |
| `recover-accuracy-log` | 3 passed | `exp-0915-041324-275817` |
| `log-summary-date-ranges` | 2 passed | `exp-0915-042820-109873` |
| `jq-data-processing` | 14 passed | `exp-0915-041357-298827` |
| `pandas-etl` | 3 passed | `exp-0915-041425-871357` |
| `jsonl-aggregator` | 1 passed | `exp-0915-042901-387245` |
| `gcode-to-text` | 2 passed | `exp-0915-042450-505362` |

The complete solution logs, verifier logs, `nvidia-smi` logs, and JSON summaries are in `/data/ycfeng/tmp/rejoin-verifier-logs/`. The seven S0 tools and mutating S1 `exec` direct checks pass in `research/rejoin/tests/test_tools.py`.

### Decision

P03 is complete. P04 may start with the four verified smoke tasks. A provider endpoint, model profile, and rollout artifact location are still required before real API collection.

## P03 disk cleanup (2026-09-15)

- Retained the 312 MB pinned Terminal-Bench checkout because P04 reuses its task source.
- Retained the final context-free Dockerfiles, build snapshots, registry digest snapshot, verifier logs, and runner v5 because they support review or P04 preparation.
- Removed 28 archived P03 intermediates: failed gcode/wasm result snapshots, superseded build and worker probe scripts/logs, and generated Python cache directories. Their causes and final fixes are recorded in `issues.md` and the P03 GPU report.
- No large P03 artifact was safe to compress while keeping the source checkout directly reusable. Unrelated large files in `/data/ycfeng/tmp` were not changed because their reuse status is outside this task.

## Cloud transfer completion (2026-09-15)

- Job `exp-0915-140553-008483` passed: 67 verified staged files; 10 image manifests; 69 unique config/layer blobs; 1,452,034,837 blob bytes. Source revision and hashes match the P03 manifest.
- Actual `nvidia-smi` reported NVIDIA H200. Python backend verified personal creator, local NFS source, and `succeeded` terminal state. Reports and the completion marker were written under the personal cloud root.
- First P04 job `exp-0915-140853-974340` failed during startup. The first platform log query returned zero rows; the cause is under inspection. No successful provider rollout is claimed.

## P04 preparation verification (2026-09-15)

- CPU isolation check passed on Python 3.10.6: real S0 write plus S1 execution produced 42 from input 21, UID was 65534, and controller mounts were absent. All three existing tool-surface tests passed.
- Pytest 8.4.1 and seven pinned support packages were installed on the CPU through the company mirror, and import checks passed. These packages are reused by task workers without verifier-time installation.
- Read-only fallback recovered the first P04 traceback: `nvidia-smi` exited 12 because task images need the mounted NVIDIA library path. Added standard `/usr/local/nvidia` binary/library paths and direct NFS collector logs. A fresh run uses `p04-20260915-v2`; the incomplete first attempt is preserved.

## P04 queue checkpoint and automatic continuation (2026-09-15)

- Current worker: `exp-0915-141415-207218`; run `p04-20260915-v2`; first task `polyglot-c-py/r0`. The exact-job API reports Pending with queue `step-main-default`, insufficient H200 quota, remaining H200=0.
- The first local launcher remains alive. A second local controller runs `run_rejoin_p04.py --concurrency 4 --await-first`; it waits for the first launcher result, then reuses that completed rollout and runs the remaining 15. No duplicate first job is submitted.
- The final completing worker runs `check_p04.py`, checks all 16 cloud traces, and writes `<run-id>.smoke.json` plus Markdown under cloud `reports/` and local staging. A collection or smoke failure remains visible; no automatic model change occurs.
- Waiting commands/logs are under `/data/ycfeng/tmp/rejoin-p04-control/`: `p04-second-launch.log`, `p04-continuation.log`, and per-rollout launcher/collector logs. Detailed commands and the passing CPU checks are in `test_report_2026-09-15_p04_preparation.md`.
- No completed real rollout or smoke PASS is claimed at this checkpoint. Required user data and unresolved user design decisions: none. Open execution issue: H200 quota; the task-image NVIDIA library correction awaits this worker.
- User clarified platform behavior: `predict-only` quota=0 is not a submission gate. The queued job must remain submitted through StepMind Python `RJobBackend` so the platform can run it FIFO after quota release. Added this rule to the worker skill and authoritative StepMind runbook; current P04 job remains queued and is being inspected by exact name.
