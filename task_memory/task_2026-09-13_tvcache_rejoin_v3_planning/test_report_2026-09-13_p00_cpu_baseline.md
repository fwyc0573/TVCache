## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the P00 CPU baseline execution and dependency recovery. |

# Test Report: P00 CPU Baseline

## Execution

- Working directory: `/data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox`
- Python: CPython 3.10.6 at `/usr/bin/python3.10`
- uv: `0.11.14`
- Temporary paths: `/data/ycfeng/tmp/rejoin-p00-tmp`, `/data/ycfeng/tmp/uv-cache`
- First command: `TMPDIR=/data/ycfeng/tmp/rejoin-p00-tmp UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache timeout 60s uv run --project tvcache/client --group dev python -m pytest -q tests/unit tests/integration`
- First result: dependency setup failed while fetching `hatchling` from public PyPI after three retries and about 50.6 seconds.
- Successful command: see [`p00_baseline/baseline.md`](p00_baseline/baseline.md); it uses the handbook's Basemind primary and extra indexes.
- Raw outputs: [`pytest.log`](p00_baseline/pytest.log) and [`pytest_mirror.log`](p00_baseline/pytest_mirror.log)

## Criteria

- The client environment must build far enough to start the suite.
- The complete `tests/unit` and `tests/integration` selection must run to completion.
- The observed counts and every failure must be saved for later comparison.
- No failure may be repaired as part of P00.

## Evidence

| Result | Evidence |
|---|---|
| PASS: environment startup via mirror | `tvclient` built and 27 packages installed. |
| PASS: suite completed | `2 failed, 184 passed, 1 xfailed, 1 error in 1.64s`. |
| Known environment error | `tests/unit/test_provider_rollout.py::test_provider_rollout_executes_local_tools_and_replays_text_history` lacks `pydantic`. |
| Known environment error | `tests/unit/test_video_agent_provider_migration.py::test_on_demand_captioning_uses_local_lavila_and_zero_api_tokens` lacks `numpy`. |
| Known code/test drift | `tests/unit/test_sandbox_manager_lifecycle.py::test_object_query_uses_deepseek_v4_flash_without_thinking` observes `/v1` appended to the provider base URL. |

## Limits

This is a CPU baseline for comparison. It does not establish the M0 opportunity signal, does not test the research harness, and does not authorize serving changes.
