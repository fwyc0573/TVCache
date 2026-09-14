## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the B01 mixed-history cursor reproducer and observed failure. |
| 2026-09-15 | Added the P03 build and verifier failures with their final resolutions. |

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

All ten selected tasks have successful build metadata, registry manifest digests, solution/verifier exit code 0, and worker status `succeeded`. No P03 blocker remains. P04 still needs a provider endpoint and the four-task smoke rollout.
