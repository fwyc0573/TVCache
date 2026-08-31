## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-08-31 | Record the fresh isolated-port smoke and completion-gate checks |

# Final Verification Report

## 1. Test Script Information

- Repository: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache`
- Integration script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tests/integration/tvcache_http_smoke.py`
- Temporary evidence directory: `/data/ycfeng/tmp/tvcache_e2e_reproduction`
- Environment: system Python `3.12.3`, server virtual environment Python `3.10.20`, `uv 0.11.14`; the fresh smoke used the server process launched with `uv run` from `tvcache/server`.

Fresh runtime commands:

```bash
cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tvcache/server
uv run tvcache_server.py --host 127.0.0.1 --port 18003
```

```bash
cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache
python3 tests/integration/tvcache_http_smoke.py \
  --base-url http://127.0.0.1:18003 \
  --task-name final-verify-20260831-162642 \
  | tee /data/ycfeng/tmp/tvcache_e2e_reproduction/final_verify_18003.log
```

The server was interrupted after the smoke. Health output was saved at `/data/ycfeng/tmp/tvcache_e2e_reproduction/health_18003.json`; the listener check reported `port_18003_free=True` after shutdown.

Static verification commands:

```bash
python3 -m compileall -q train tvcache video-agent-tools/VideoAgent video-agent-tools/Video-LLaVA/videollava tests/integration
python3 -m py_compile tests/integration/tvcache_http_smoke.py
```

```bash
cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tvcache/server && uv lock --check
cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tvcache/client && uv lock --check
cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/train && uv lock --check
```

`git diff --check` was run from the repository root. The Markdown probe counted headings, fences, bash blocks, relative entrypoint links, and report paths; each extracted bash block was checked with `bash -n`.

## 2. Validation Criteria

- The health request must return HTTP `200` with `found:false` for a new task.
- The HTTP smoke must exit `0` and print `RESULT=PASS`.
- Exact lookup must preserve the final value `manual_value_b` and execution time `0.25`.
- Prefix lookup must return a two-item history; the terminal node must report `cache_hits >= 1` and `prefix_hits >= 1`.
- `get_all_envs` must contain exactly one environment for the unique task.
- Python compilation, all three lock checks, shell syntax, Markdown fences, links, and `git diff --check` must report zero errors.
- The server started for this report must leave port `18003` free after interruption.

## 3. Test Results and Evidence

### Runtime smoke: PASS

The fresh command exited `0` and printed:

```text
base_url=http://127.0.0.1:18003
task_name=final-verify-20260831-162642
initial_found=False
put_success=True
exact_env_id=env-final-verify-20260831-162642
exact_value=manual_value_b
exact_tool_exec_time=0.25
prefix_history_len=2
cache_hits=1
prefix_hits=1
all_env_count=1
RESULT=PASS
```

The preceding health request returned:

```json
{"env_id":null,"found":false,"tool_exec_time":null,"value":null}
```

The server access log showed HTTP `200` for health, exact GET, PUT, prefix match, visualize, and get-all-envs. The captured client output is `/data/ycfeng/tmp/tvcache_e2e_reproduction/final_verify_18003.log`.

### Static and dependency checks: PASS

- `compileall`: exit `0`.
- `py_compile`: exit `0`.
- `tvcache/server && uv lock --check`: exit `0`, resolved `15` packages.
- `tvcache/client && uv lock --check`: exit `0`, resolved `22` packages.
- `train && uv lock --check`: exit `0`, resolved `39` packages.
- `git diff --check`: exit `0`.
- Manual: `756` lines; `84` fences (balanced); `30` bash blocks, each accepted by `bash -n`; each top-level heading `## 1` through `## 13` occurred once; both stable-entrypoint links resolved to an existing file; all five test-report paths listed in section 13 existed.

### Cleanup: PASS

After sending Ctrl-C to the server session, the listener probe printed `port_18003_free=True`. The process scan found no task-owned `tvcache_server.py`, `sandbox_server.py`, `train_with_tvcache.py`, or Video-LLaVA process.

### Executor rerun: PASS

The independent fake-environment probe was rerun from `train/` against a fresh server on port `18001` with task `executor-final-20260831-162642`. It exited `0` and returned:

```text
r1=mutate:a:state=1
r2=mutate:a:state=1
r3=read:b:state=1
envs=[executor-final-20260831-162642-env-1dc31466]
```

The captured log `/data/ycfeng/tmp/tvcache_e2e_reproduction/final_executor_18001.log` contains the expected miss -> PUT -> exact hit -> prefix/fork -> unref -> suffix -> PUT sequence, with HTTP `200` for every expected request.

### Full VideoAgent/Tinker E2E: BLOCKED

This report does not relabel the previously failed full workflow as a pass. The staged preflight still records sandbox exit `1` with `RuntimeError: operator torchvision::nms does not exist`, train import exit `1` with `ModuleNotFoundError: No module named 'pydantic'`, missing model/video assets, the hard-coded sandbox video path, and unavailable Tinker credentials. Details remain in `test_report_2026-08-31_train_sandbox_preflight.md` and the manual's sections 1, 5-8, and 12.
