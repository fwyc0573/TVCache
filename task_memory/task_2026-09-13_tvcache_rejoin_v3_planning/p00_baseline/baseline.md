## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Captured the P00 CPU baseline on the current checkout. |

# P00 Baseline

## Repository

- Branch: `yc-sandbox`
- HEAD after P01 evidence: `30ff78f` (P00 suite ran after the B01 test commit and before the P02 harness changes).
- Source-plan pin before P01: `43cf9d6a779eb5149e0fae50b9a3a891dcbaed6f`
- P01 commit: `cce8520` adds the strict B01 reproducer and is now part of the execution baseline.

## CPU suite

The first public-index attempt failed while rebuilding `tvcache/client/.venv`: `hatchling` resolution from `https://pypi.org/simple/hatchling/` timed out after three retries. Following the environment handbook, the second attempt used the Basemind mirror and built the client package successfully.

Command used for the successful test run:

```bash
UV_INDEX_URL=http://mirrors.i.basemind.com/pypi/simple/ \
UV_EXTRA_INDEX_URL=http://pypi.i.basemind.com/brain/dev/+simple \
UV_INSECURE_HOST=mirrors.i.basemind.com,pypi.i.basemind.com \
TMPDIR=/data/ycfeng/tmp/rejoin-p00-tmp \
UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
uv run --project tvcache/client --group dev python -m pytest -q tests/unit tests/integration
```

Raw output: [`pytest_mirror.log`](pytest_mirror.log)

Observed result:

```text
2 failed, 184 passed, 1 xfailed, 1 error in 1.64s
```

The suite is a baseline with known red items. It is not a green-test claim.

## Archived video fact

The reviewed archived record [`task_2026-09-11_tvcache_rl_reproduction_new_machine/summary.md`](../../task_2026-09-11_tvcache_rl_reproduction_new_machine/summary.md) reports a completed provider-backed H800 video E2E: four rollouts completed with reward 1.0, six exact hits and twenty prefix hits, and no remaining sandbox. This fact is recorded for context; P00 does not rerun video or Tinker.

## Environment

- Python: CPython 3.10.6 at `/usr/bin/python3.10`
- uv: `0.11.14`
- Temporary directory: `/data/ycfeng/tmp/rejoin-p00-tmp`
- UV cache: `/data/ycfeng/tmp/uv-cache`
- Host baseline: CPU only; no GPU, API, Docker, TVCache server, or research harness was started.
