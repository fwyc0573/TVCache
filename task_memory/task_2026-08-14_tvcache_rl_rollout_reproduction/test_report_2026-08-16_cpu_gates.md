## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-08-16 | Updated the report after production teardown convergence remediation with the fresh 175-test Python 3.12 gate. |
| 2026-08-16 | Updated the report after I-047 retry-safe teardown remediation with the fresh 173-test Python 3.12 gate. |
| 2026-08-16 | Updated the report after I-046 run-level lifecycle remediation with the fresh 160-test Python 3.12 gate. |
| 2026-08-16 | Updated the report after v5 lifecycle remediation with the fresh 149-test Python 3.12 gate. |
| 2026-08-16 | Updated the report after v4 lifecycle remediation with the fresh 149-test Python 3.12 gate. |
| 2026-08-16 | Updated the report after v3 remediation with the fresh 145-test Python 3.12 gate. |
| 2026-08-16 | Updated the report with the real Tinker preflight and fresh 128-test Python 3.12 gate. |
| 2026-08-16 | Updated the report after review-blocker remediation and the fresh 89-test CPU gate. |
| 2026-08-16 | Created the full CPU unit and integration gate report. |

# Test Report: TVCache RL Reproduction CPU Gates

**Date**: 2026-08-16  
**Environment**: frozen training environment `/data/ycfeng/tmp/tvcache-train-py312`; Python 3.12.3; Tinker 0.24.1; temporary pytest 8.4.2 and pytest-asyncio 1.4.0 for the CPU suite; no conda environment

## 1. Test Script Information

Test scripts:

- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_async_executor_configuration.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_async_executor_lifecycle.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_async_tvcache_client_fail_fast.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_baseline_agent_loop_fail_fast.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_dataset_selection.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_rollout_execution.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_rollout_metrics.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_sandbox_client_fail_fast.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_sandbox_manager_lifecycle.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_simple_dict_bank_configuration.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_training_configuration.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_training_update.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_tvc_agent_loop.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_tvcache_run_lifecycle.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_video_agent_runtime_config.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/integration/test_executor_cache_reuse.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/integration/test_tvcache_server_schema.py`
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/integration/tinker_runtime_preflight.py`

Reproducible commands:

```bash
cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction
export TMPDIR=/data/ycfeng/tmp
export UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache

# The four wheels must first match tvcache/client/uv.lock.
timeout 120s systemd-run --user --scope -p MemoryMax=2G \
  uv pip install \
    --offline \
    --no-index \
    --find-links /data/ycfeng/tmp \
    --no-deps \
    --python /data/ycfeng/tmp/tvcache-train-py312/bin/python \
    'pytest==8.4.2' \
    'pytest-asyncio==1.4.0' \
    'pluggy==1.6.0' \
    'iniconfig==2.3.0'

PYTHONDONTWRITEBYTECODE=1 \
timeout 600s systemd-run --user --scope -p MemoryMax=2G \
  /data/ycfeng/tmp/tvcache-train-py312/bin/python \
    -m pytest -q -p no:cacheprovider tests/unit tests/integration

PYTHONDONTWRITEBYTECODE=1 \
timeout 120s systemd-run --user --scope -p MemoryMax=2G \
  /data/ycfeng/tmp/tvcache-train-py312/bin/python \
    tests/integration/tinker_runtime_preflight.py

UV_PROJECT_ENVIRONMENT=/data/ycfeng/tmp/tvcache-train-py312 \
timeout 600s systemd-run --user --scope -p MemoryMax=2G \
  uv sync --project train --frozen --offline

timeout 120s systemd-run --user --scope -p MemoryMax=2G \
  uv pip check \
    --python /data/ycfeng/tmp/tvcache-train-py312/bin/python

timeout 120s systemd-run --user --scope -p MemoryMax=2G \
  uv lock --check --project train
timeout 120s systemd-run --user --scope -p MemoryMax=2G \
  uv lock --check --project tvcache/client
git diff --check
```

## 2. Validation Criteria

- All collected tests pass on Python 3.12: expected 175 passed, 0 failed.
- Real Tinker converter emits exactly 2 datums for the 2 non-prefix observations, with 2 sampled tokens and aligned targets.
- All 3 training drivers import, expose async `main`, and emit native chz help without stderr.
- Cache exact hit performs 0 additional backend tool executions after the first call.
- Cache partial-prefix reuse performs exactly 1 backend tool execution for the one-call suffix.
- Current `/put` and `/get` server schema returns HTTP 200 and preserves the stored value and `tool_exec_time`.
- Empty optimizer input performs 0 forward/backward calls and 0 optimizer calls while recording a skip metric.
- One nonempty training datum performs exactly 1 forward/backward call and 1 optimizer call.
- Infrastructure, malformed response, and teardown failures propagate instead of becoming cache misses or tool-result strings.
- Rollout failure cancels the sibling task and attempts cleanup for every started loop.
- Startup failure attempts cleanup for all 3 constructed loops, including the failed and not-yet-started loops.
- Repeated stop and run-then-stop close the TVCache executor and fork-bank client exactly once each.
- TVCache stop attempts withdraw and both resource closes and preserves all 3 injected cleanup errors.
- Fork-bank partial failure stops every created parent/fork and closes its HTTP client.
- Failed fork-bank withdrawal retains exactly the failed fork and the next withdrawal retries only that fork.
- Partial-prefix setup, `unref`, and suffix failures retain a fork whose stop fails, and `close()` retries each retained fork.
- Failed unpublished publication children and failed removed environments retain one pending owner and are retried by `close()`.
- Task drain rejects active cache references without modifying the task tree.
- After parallel cache reuse, run-level teardown changes cached environment count from 1 to 0 and active cached sandbox count from 1 to 0.
- Failed task drains and sandbox stops retain only failed owners; a later close retries only those owners.
- A committed drain replays the same detached IDs under the same `drain_id` until ACK and rejects a competing drain ID.
- A committed sandbox stop replays success under the same operation ID with no second filesystem removal.
- ACK response loss retries only ACK; successful environment stops are not repeated.
- Production context exit recovers one lost drain, stop, and ACK response using the same lifecycle and operation IDs, with pending counts ending at zero.
- HTTP status and other semantic teardown failures are not automatically retried.
- A simultaneous training error and cleanup error remain separately inspectable.
- Each persisted rollout record contains stable dataset/video identity and seven numeric cache/tool fields.
- Each cache call is classified exactly once as exact hit, prefix hit, or miss.
- A failed TVCache sample invokes the remote sampler exactly once.
- The training lock contains 139 packages, uses CPU-only Torch, and contains zero CUDA/NVIDIA/Triton runtime packages.
- The restored training environment contains 138 compatible distributions and no test-only packages.
- Both lock checks and `git diff --check` exit 0.

## 3. Test Results and Evidence

**Overall outcome: PASS**

| Metric | Expected | Observed | Result |
|--------|----------|----------|--------|
| Python version | 3.12.x | 3.12.3 | PASS |
| Tinker version | 0.24.1 | 0.24.1 | PASS |
| Tests passed | 175 | 175 | PASS |
| Tests failed | 0 | 0 | PASS |
| Full suite duration | Informational | 1.80 s | PASS |
| Converter datums | 2 | 2 | PASS |
| Converter inputs | `[[10,11],[90,91]]` | `[[10,11],[90,91]]` | PASS |
| Converter targets | `[[11,20],[91,30]]` | `[[11,20],[91,30]]` | PASS |
| Converter sampled tokens | 2 | 2 | PASS |
| Driver imports | 3 | 3 | PASS |
| Async driver `main` functions | 3 | 3 | PASS |
| Native chz help exit code | 1 per driver | 1, 1, 1 | PASS |
| Driver help stderr lines | 0 per driver | 0, 0, 0 | PASS |
| Driver help output lines | Informational | 19, 19, 20 | PASS |
| Backend executions after first call | 1 | 1 | PASS |
| Backend executions after exact hit | 1 | 1; delta 0 | PASS |
| Exact-hit executor tool executions | 0 | 0 | PASS |
| Exact-hit count | 1 | 1 | PASS |
| Backend executions after prefix extension | 2 | 2; suffix delta 1 | PASS |
| Prefix-hit executor tool executions | 1 | 1 | PASS |
| Prefix-hit count | 1 | 1 | PASS |
| Prefix classification `(total, exact, prefix, miss)` | `(1,0,1,0)` | `(1,0,1,0)` | PASS |
| Failed-sample backend calls | 1 | 1 | PASS |
| `/put` HTTP status | 200 | 200 | PASS |
| `/get` HTTP status | 200 | 200 | PASS |
| Stored tool execution time | 0.25 s | 0.25 s | PASS |
| Empty-batch forward/backward calls | 0 | 0 | PASS |
| Empty-batch optimizer calls | 0 | 0 | PASS |
| `optim/training_datums` for empty batch | 0.0 | 0.0 | PASS |
| `optim/skipped_empty_batch` | 1.0 | 1.0 | PASS |
| One-datum forward/backward calls | 1 | 1 | PASS |
| One-datum optimizer calls | 1 | 1 | PASS |
| Rollout sibling cancellations | 1 | 1 | PASS |
| Started-loop stop attempts after rollout failure | 2 | 2 | PASS |
| Constructed-loop stop attempts after startup failure | 3 | 3 | PASS |
| Repeated-stop executor close calls | 1 | 1 | PASS |
| Repeated-stop fork-bank close calls | 1 | 1 | PASS |
| Run-then-stop executor close calls | 1 | 1 | PASS |
| Run-then-stop fork-bank close calls | 1 | 1 | PASS |
| Preserved injected cleanup errors | 3 | 3 | PASS |
| Partial-deposit parents stopped | 2 | 2 | PASS |
| Partial-deposit forks stopped | 1 | 1 | PASS |
| Failed-withdraw first-pass fork stops | 2 | 2 | PASS |
| Failed-withdraw retained fork IDs | 1 | 1 | PASS |
| Successful fork IDs retained | 0 | 0 | PASS |
| Failed-withdraw second-pass fork stops | 1 | 1 | PASS |
| Partial-prefix failed-cleanup paths | 3 | 3 | PASS |
| Stop attempts per failed prefix fork before `close()` | 1 | 1 | PASS |
| Stop attempts per recovered prefix fork after `close()` | 2 | 2 | PASS |
| Unpublished-child stops before/after recovered `close()` | `1 / 2` | `1 / 2` | PASS |
| Removed-environment stops before/after recovered `close()` | `1 / 2` | `1 / 2` | PASS |
| I-046 focused RED failures | 11 | 11 | PASS |
| I-046 focused GREEN passes | 11 | 11 | PASS |
| I-046 affected-module passes | 106 | 106 | PASS |
| I-047 original RED failures | 19 | 19 | PASS |
| I-047 existing-caller RED failures | 1 | 1 | PASS |
| I-047 affected-module passes | 68 | 68 | PASS |
| Production-context RED failures | 1 | 1 | PASS |
| Production-context GREEN passes | 2 | 2 | PASS |
| Context drain/stop/ACK attempts | `2 / 2 / 2` | `2 / 2 / 2` | PASS |
| Context unique drain/stop IDs | `1 / 1` | `1 / 1` | PASS |
| Context transport retry delays | 3 | 3 | PASS |
| Context final pending drain/stop/ACK | `0 / 0 / 0` | `0 / 0 / 0` | PASS |
| Semantic HTTP rejection drain attempts | 1 | 1 | PASS |
| Detached environment IDs on first/replayed drain | `2 / 2` | `2 / 2` | PASS |
| Competing drain IDs rejected while pending | 1 | 1 | PASS |
| Same-ID drain ACK attempts accepted | 2 | 2 | PASS |
| Drain response-loss attempts using identical ID | 2 | 2 | PASS |
| Stop response-loss attempts using identical ID | 2 | 2 | PASS |
| ACK response-loss attempts | 2 | 2 | PASS |
| Stop attempts repeated during ACK retry | 0 | 0 | PASS |
| Same-ID sandbox stop calls / filesystem removals | `2 / 1` | `2 / 1` | PASS |
| Generated client stop IDs across two attempts | 1 unique | 1 unique | PASS |
| Cached environments before/after run-level close | `1 / 0` | `1 / 0` | PASS |
| Active cached sandboxes before/after run-level close | `1 / 0` | `1 / 0` | PASS |
| Failed environment stop attempts before/after retry | `1 / 2` | `1 / 2` | PASS |
| Successful environment stops retried | 0 | 0 | PASS |
| Failed task drain calls before/after retry | `1 / 2` | `1 / 2` | PASS |
| Preserved simultaneous training/cleanup errors | `1 / 1` | `1 / 1` | PASS |
| Numeric fields per rollout record | 7 | 7 | PASS |
| Non-prefix sample total tokens | 6 | 6 | PASS |
| Non-prefix sampled tokens | 2 | 2 | PASS |
| Sample rollout elapsed time | 1.25 s | 1.25 s | PASS |
| Training lock packages | Informational | 139 | PASS |
| Client lock packages | Informational | 28 | PASS |
| Training lock CUDA/NVIDIA/Triton packages | 0 | 0 | PASS |
| Temporary test-only packages added | 4 | 4 | PASS |
| Temporary test-only packages removed | 4 | 4 | PASS |
| Restored training distributions | 138 | 138 | PASS |
| Restored incompatible packages | 0 | 0 | PASS |
| Registry-package direct URL records | 0 | 0 | PASS |
| Expected local-project direct URL records | 2 | 2 | PASS |
| Train lock-check duration | Informational | 2 ms | PASS |
| Client lock-check duration | Informational | 1 ms | PASS |
| `git diff --check` findings | 0 | 0 | PASS |

Key command output:

```text
........................................................................ [ 41%]
........................................................................ [ 83%]
.............................                                            [100%]
175 passed in 1.80s
```

```text
python_version=3.12.3
tinker_version=0.24.1
datum_count=2
sampled_token_count=2
help_exit_code=1,1,1
help_output_lines=19,19,20
```

The initial real preflight failed only because it expected help exit code 0.
Source inspection and the official cookbook confirmed that chz 0.4.0
intentionally prints help to stdout and exits 1. The test-only expectation was
corrected; production entrypoints were unchanged.
