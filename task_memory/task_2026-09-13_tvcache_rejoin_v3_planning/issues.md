## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the B01 mixed-history cursor reproducer and observed failure. |
| 2026-09-15 | Added the P03 build and verifier failures with their final resolutions. |
| 2026-09-15 | Recorded P04 collection preparation, cloud persistence, and current execution evidence. |
| 2026-09-15 | Closed the v21 P04 collection issues and recorded the recover-task verifier limitation. |
| 2026-09-15 | Recorded P05 staging fixes, provider retries, and the final typed-U redirect recommendation. |
| 2026-09-15 | Added the P05 sampling-count review and marked frequency interpretation as pending a P06 sampling decision. |

# Open Issues

## B01 filtered-prefix cursor mismatch

- **Status:** reproduced; repair deferred by the v3 plan.
- **Test:** `tests/integration/test_executor_cache_reuse.py::test_filtered_prefix_cursor_does_not_replay_prior_mutation`
- **Scenario:** The donor executes `M1 -> R1(read-only) -> M2`; the recipient requests `M1 -> R1 -> M2 -> M3`.
- **Expected:** The cached stateful prefix is `[M1, M2]`, so the recipient resumes at raw history index 3 and executes only `M3`.
- **Observed:** The executor sets `executed_commands = len(prefix_tool_calls) == 2`, then starts raw history at index 2. It executes `M2` again and returns `M1/M2/M2/M3`.
- **Evidence:** Running with `--runxfail` failed at the expected result assertion; the normal strict `xfail` run reports one expected failure. The complete integration file reports `4 passed, 1 xfailed`.
- **Scope:** This reproducer only records B01. It does not change executor behavior or cover B02-B05.

## P03 runtime and image-build issues

### CPU master has no usable container runtime

- **Status:** resolved for P03 by using the approved GPU-worker build route.
- **Observed:** `docker`, `podman`, `nerdctl`, and `buildah` were unavailable on the CPU master; a nested Docker probe failed with `unshare: operation not permitted`.
- **Resolution:** StepBPS built the final images, and the verifier runner used StepMind Python `RJobBackend` on H200 with `step_main`, creator `i-fengyicheng`, and the pinned local NFS source. No CPU-master Docker state was assumed.

### Early image and verifier attempts

- **wasm-pipeline:** the first image omitted task artifacts and the first verifier runner did not copy task tests into `/tests`. Final v3 image plus the corrected runner produced `3 passed`.
- **pandas-etl:** the generated image initially placed input at `/data.csv` while the solution reads `/app/data.csv`. Final v2 image copied the input into `/app/data.csv` and produced `3 passed`.
- **gcode-to-text:** earlier v2/v3/v4/v5/v7 builds lacked a complete OCR runtime or input. Final v8 reused the successful base, added the required OCR libraries and Python packages, restored `/app/text.gcode`, and produced `2 passed`.
- **Runner metadata:** one early worker reached a passing test result but ended with a failed job because the summary script lacked `import os`; runner v5 fixed the summary write and all final jobs reached `succeeded`.

### Current P03 status

All ten selected tasks have successful build metadata, registry manifest digests, solution/verifier exit code 0, and worker status `succeeded`. No P03 blocker remains. P04 v21 completed the four-task smoke sequence with a passing collection gate.

## P04 execution environment

- The first storage launcher omitted `EXP_ID`; the local backend rejected it before job creation. The reusable launcher now supplies it.
- Task images do not set NVIDIA binary/library search paths. The first storage job failed with missing `nvidia-smi`; a full handbook worker image completed cloud persistence. The first P04 job then found the binary but exited 12. The P04 wrapper now supplies `/usr/local/nvidia/bin` and `/usr/local/nvidia/lib64` plus `/usr/local/nvidia/lib`; v21 completed successfully with this correction.
- Platform Python logs for the first P04 job returned zero rows. The runbook-authorized SSH read recovered the exact traceback; future collector logs are written directly to the local mounted task staging directory.
- Job `exp-0915-141415-207218` is queued: `Insufficient GPU quota`, queue `step-main-default`, `H200=0`. Keep the local launcher alive and inspect the existing job. No additional provider or task input is missing.

## P04 native long-action truncation

- **Status:** resolved for collection in v21.
- **Observed:** nine v18 rollouts ended with `ValueError: Provider native tool arguments are invalid`. The provider response ended in an unterminated JSON string while generating the contents of a long `write_file` call. The short native calls and the same task images completed normally.
- **Evidence:** v18 inspection records show `/app/merge_users.py` and `/app/process.py` ending mid-content at the 1024-token response budget. A direct probe using the same endpoint and native-call settings returned parseable calls for 3.5K, 5.5K, and 7.5K character contents with a 2048-token request; no endpoint or image failure was observed.
- **Resolution:** P04 configs now request 4096 output tokens. Malformed-call retries request 4096 and then 3072 tokens. The assistant native message, including `reasoning_content`, remains in the next request, and `parallel_tool_calls=false` remains enabled.
- **Verification:** v21 produced no malformed native-call collection errors. Long actions completed under the 4096-token budget; remaining verifier failures are task outcomes, not argument parsing failures.

## P04 provider transient HTTP failures

- **Status:** resolved for collection in v21.
- **Observed:** `polyglot-c-py/r1` and `recover-accuracy-log/r3` received HTTP 503 after valid native calls and workspace mutations. The collector wrote complete workspace/verifier artifacts but marked the rollout as `collection_error`.
- **Resolution:** `collect_p04.py` now repeats the identical request up to three times for HTTP 429, 500, 502, 503, and 504, and for URL/timeouts, with 1-second then 2-second backoff. Non-transient HTTP responses still fail immediately. The smoke must be rerun with this collector because its no-collection-error check is strict.
- **Verification:** v21 recorded zero collection errors across all 16 rollouts. The provider retry policy therefore resolved the collection failure mode for this run.

## P04 recover-accuracy-log verifier failures

- **Status:** open as a task-level data-quality limitation; no runtime repair is indicated by the current evidence.
- **Observed:** all four `recover-accuracy-log` v21 rollouts produced complete traces, workspace archives, verifier logs, and verifier XML, but each verifier process exited 1. The task reported the expected seven output files and per-run accuracy values in its final answers, yet the unchanged upstream verifier still reported one failed test in each rollout.
- **Scope:** The failures are isolated to the model-produced task result. Every rollout had real mutations, valid reloaded traces, H200 execution, and no collection error. No image, GPU, provider transport, or cloud persistence failure was observed.
- **Decision:** Keep the artifacts and record verifier pass as 0/4 for this task. The current P04 gate checks artifact completeness and collection health, so v21 remains PASS. P05 must treat this task's verifier result as a data-quality limitation and avoid using it as clean task-success evidence.

## P05 collection and analysis issues

### Missing verifier package in first P05 stage

- **Status:** resolved.
- **Observed:** `p05-20260915-v1` entered the tool loop but ended at verifier setup with `FileNotFoundError: .../public/verifier_packages`.
- **Resolution:** The P05 runner now copies the verified offline package tree from the P04 staging directory before creating configs. v2 and v3 stages contain the package tree.

### Oversized provider context for jsonl-aggregator

- **Status:** resolved for the retained retry records.
- **Observed:** Four v2 `jsonl-aggregator` rollouts received HTTP 413 after a large filesystem result was sent back in the native tool conversation.
- **Resolution:** The complete result remains in the trace, while provider context is capped at 12,000 characters for P05. All four v3 retries completed without collection errors.

### Multiple native calls in one provider response

- **Status:** resolved for the retained retry record.
- **Observed:** `log-summary-date-ranges/r2` in v2 returned multiple native tool calls after the collector's existing retries.
- **Resolution:** The record was rerun with the same P05 policy under v3 and completed with a valid single-call sequence. The original v2 error remains retained as evidence.

### P05 opportunity result

- **Status:** resolved for P05; follow-up selected.
- **Observed:** 667 calls took 66.831 s. Hindsight C+U was 3.60%; C alone was 0.01%; U was 3.59%; eight tasks had post-divergence opportunity; task-scoped top-1 signature share was 7.95%.
- **Decision:** The generic C continuation signal is weak. P06 should study one typed adapter for the repeated `multi-source-data-merger` S1 `exec` family (1.650 s of U time) before any memoizer or serving integration work.

### P05 per-prompt sample count

- **Status:** open for P06 decision; no collection defect was found.
- **Observed:** Each of the ten task instructions has four final rollout trajectories (`r0`–`r3`). Each API turn requests one response because the payload has no `n` field. The five v3 retries replace five failed v2 rollout slots and do not add independent samples.
- **Impact:** Four trajectories provide only six unordered trajectory pairs per task and three possible donor trajectories for each recipient. The 667 tool events improve event coverage but do not make the prompt-level sample size large. Current C/U shares are descriptive pilot results, not stable reuse probabilities.
- **Recommendation:** P06 must choose whether to add 12 trajectories per task (16 total) under the same policy before treating the redirect as the final workload decision, or explicitly retain the four-trajectory result as descriptive evidence only. The detailed audit is in `p05_sampling_review.md`.
