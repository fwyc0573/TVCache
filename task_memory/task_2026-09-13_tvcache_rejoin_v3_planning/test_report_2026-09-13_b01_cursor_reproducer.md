## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded focused B01 reproducer validation. |

# B01 Cursor Reproducer Test Report

## Execution

- Working directory: `/data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox`
- Python: `/data/ycfeng/step-sandbox/TVCache/tvcache/client/.venv/bin/python` (Python 3.10.6)
- Pytest: `/data/ycfeng/step-sandbox/TVCache/tvcache/client/.venv/bin/pytest` (pytest 8.4.2)
- Expected-failure check:
  `/data/ycfeng/step-sandbox/TVCache/tvcache/client/.venv/bin/pytest -q tests/integration/test_executor_cache_reuse.py::test_filtered_prefix_cursor_does_not_replay_prior_mutation -o addopts=''`
- Failure proof:
  `/data/ycfeng/step-sandbox/TVCache/tvcache/client/.venv/bin/pytest -q tests/integration/test_executor_cache_reuse.py::test_filtered_prefix_cursor_does_not_replay_prior_mutation --runxfail -o addopts=''`
- File regression check:
  `/data/ycfeng/step-sandbox/TVCache/tvcache/client/.venv/bin/pytest -q tests/integration/test_executor_cache_reuse.py -o addopts=''`

## Criteria

The donor sequence is `M1 -> R1(read-only) -> M2`; the recipient sequence is `M1 -> R1 -> M2 -> M3`. A correct filtered-prefix cursor resumes after raw index 3, returns `M1/M2/M3`, and executes only `M3` in the recipient.

## Evidence

- **PASS (reproducer is active):** normal strict `xfail` run: `1 xfailed in 0.19s`.
- **PASS (failure is proven):** `--runxfail` run: `1 failed in 0.19s`; actual result was `M1/M2/M2/M3`, expected `M1/M2/M3`.
- **PASS (existing integration coverage):** full file run: `4 passed, 1 xfailed in 0.21s`.

The observed duplicate `M2` establishes that `len(prefix_tool_calls)` was used as a raw command cursor after the read-only `R1` was removed from the cached stateful chain. The test does not repair the executor and does not cover B02-B05.

