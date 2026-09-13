## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the B01 mixed-history cursor reproducer and observed failure. |

# Open Issues

## B01 filtered-prefix cursor mismatch

- **Status:** reproduced; repair deferred by the v3 plan.
- **Test:** `tests/integration/test_executor_cache_reuse.py::test_filtered_prefix_cursor_does_not_replay_prior_mutation`
- **Scenario:** The donor executes `M1 -> R1(read-only) -> M2`; the recipient requests `M1 -> R1 -> M2 -> M3`.
- **Expected:** The cached stateful prefix is `[M1, M2]`, so the recipient resumes at raw history index 3 and executes only `M3`.
- **Observed:** The executor sets `executed_commands = len(prefix_tool_calls) == 2`, then starts raw history at index 2. It executes `M2` again and returns `M1/M2/M2/M3`.
- **Evidence:** Running with `--runxfail` failed at the expected result assertion; the normal strict `xfail` run reports one expected failure. The complete integration file reports `4 passed, 1 xfailed`.
- **Scope:** This reproducer only records B01. It does not change executor behavior or cover B02-B05.

