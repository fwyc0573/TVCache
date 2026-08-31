## Modification History

| Date       | Summary of Changes                  |
| ---------- | ----------------------------------- |
| 2026-08-31 | Record final direct HTTP smoke run |
| 2026-08-31 | Add completion-gate rerun and save-output evidence |

# TVCache HTTP Smoke Test Report

## 1. Test Script Information

- Test script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tests/integration/tvcache_http_smoke.py`
- Exact command:

  ```bash
  cd /data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache
  set -o pipefail
  task_name="manual-final-$(date +%s)"
  python3 tests/integration/tvcache_http_smoke.py \
    --base-url http://127.0.0.1:18001 \
    --task-name "$task_name" \
    2>&1 | tee "/data/ycfeng/tmp/tvcache_e2e_reproduction/final_smoke_${task_name}.log"
  ```
- Server process: `uv run tvcache_server.py --host 127.0.0.1 --port 18001`.
- Environment: system Python `3.12.3`, `uv 0.11.14`; server virtual environment is Python `3.10.20`.
- Captured log: `/data/ycfeng/tmp/tvcache_e2e_reproduction/final_smoke_manual-final-1788162712.log`.

## 2. Validation Criteria

- `GET /get` must return HTTP `200` with `initial_found=False` for the unique task.
- `PUT /put` must return HTTP `200` and `success=true` using array fields aligned with `history`.
- Exact `GET /get` must return the stored environment, final value, and final tool execution time.
- `POST /prefix_match` must return the full two-item history for a longer query.
- `GET /visualize` must report at least one `cache_hits` and one `prefix_hits` on the terminal node.
- `GET /get_all_envs` must include the environment created by this run.

## 3. Test Results and Evidence

**PASS** — the script exited with status `0` and printed:

```text
base_url=http://127.0.0.1:18001
task_name=manual-final-1788162712
initial_found=False
put_success=True
exact_env_id=env-manual-final-1788162712
exact_value=manual_value_b
exact_tool_exec_time=0.25
prefix_history_len=2
cache_hits=1
prefix_hits=1
all_env_count=1
RESULT=PASS
```

The observed values close the request chain: the first lookup missed, the array payload stored two history entries, exact lookup returned `manual_value_b` with tool time `0.25`, prefix lookup returned both entries, and both hit counters reached `1`. The run used a fresh task name and did not require Tinker, GPU, VideoAgent, or downloaded videos.

## 4. Completion-gate rerun

- Exact command:

  ```bash
  set -o pipefail
  task_name="completion-$(date +%Y%m%d-%H%M%S)"
  python3 tests/integration/tvcache_http_smoke.py \
    --base-url http://127.0.0.1:18001 \
    --task-name "$task_name" \
    2>&1 | tee "/data/ycfeng/tmp/tvcache_e2e_reproduction/final_completion_${task_name}.log"
  ```

- Environment: system Python `3.12.3`; server process Python `3.10.20`; `uv 0.11.14`.
- Observed task: `completion-20260831-160554`; process exit `0`.
- Observed output: `initial_found=False`, `put_success=True`, `exact_env_id=env-completion-20260831-160554`, `exact_value=manual_value_b`, `exact_tool_exec_time=0.25`, `prefix_history_len=2`, `cache_hits=1`, `prefix_hits=1`, `all_env_count=1`, `RESULT=PASS`.

## 5. Run-output persistence check

- Command path: `POST http://127.0.0.1:18001/api/save` with the current `/visualize` JSON, followed by `GET /api/runs`.
- Observed `save_status=200`, `success=true`, and absolute path `/home/i-fengyicheng/susRL/tv-cache/data/runs/completion-final/epoch-0/visualize_20260831_161523.json`.
- `saved_path_exists=True`; `runs_status=200`; response keys were `auto_saved_runs`, `base_dir`, and `manual_runs` (`528` response bytes).

## 6. Final clean-port rerun

- Exact command: `python3 tests/integration/tvcache_http_smoke.py --base-url http://127.0.0.1:18002 --task-name final-clean-20260831-162108`.
- Environment: system Python `3.12.3`; server environment Python `3.10.20`; `uv 0.11.14`.
- Result: exit `0`; `initial_found=False`, `put_success=True`, `exact_env_id=env-final-clean-20260831-162108`, `exact_value=manual_value_b`, `exact_tool_exec_time=0.25`, `prefix_history_len=2`, `cache_hits=1`, `prefix_hits=1`, `all_env_count=1`, `RESULT=PASS`.
- Server access log: `/data/ycfeng/tmp/tvcache_e2e_reproduction/final_server_18002.log`; after the run, the server session was interrupted and the `18002` listener check reported `final_clean_port=FREE`.
