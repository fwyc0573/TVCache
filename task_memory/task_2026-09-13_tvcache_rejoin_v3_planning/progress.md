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

# Status: in-progress

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
| P02 minimal research harness | in-progress | Repository audit found no `research/` package; lightweight Python 3.10 package design is ready for implementation. |

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
