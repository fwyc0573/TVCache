## Test Report: H200 StepCode Provider Protocol Gate

**Date**: 2026-09-08
**Environment**: CPU master in the TVCache worktree; namespace `shai-core`; quota group `step_main`; requested GPU `h200`; specified image `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`; `brainctl`/`rlaunch` platform runtime.

### 1. Test Script Information

- Smoke script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/e2e/provider_protocol_smoke.py`
- Local syntax check:

```bash
python3 -m py_compile tests/e2e/provider_protocol_smoke.py
```

- Predict-only command:

```bash
timeout 180s /kubebrain/rlaunch --predict-only --name=tvcache-step-main --namespace=shai-core --charged-group=step_main --private-machine=group --positive-tags=h200 --gpu=1 --cpu=8 --memory=32768 --predict-node-num=10 -- bash -lc 'true'
```

- Final live protocol command (the command reached the worker and then stopped at the value-free credential gate):

```bash
timeout 900s /kubebrain/rlaunch --name=tvcache-step-main-smoke-entrypoint --namespace=shai-core --charged-group=step_main --private-machine=group --positive-tags=h200 --gpu=1 --cpu=8 --memory=32768 --backoff-limit=1 --max-wait-duration=10m --enable-sshd=false --image=hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0 --entrypoint=/bin/bash --volume=/data:/data --workdir=/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction -- -lc 'set -euo pipefail; echo WORKER_HOST=$(hostname); echo GPU_LINES=$(nvidia-smi -L | tr "\n" ";"); if [ -n "${STEPCODE_API_KEY:-}" ]; then echo STEPCODE_API_KEY=SET; else echo STEPCODE_API_KEY=UNSET; exit 20; fi; if [ -n "${STEPCODE_BASE_URL:-}" ]; then echo STEPCODE_BASE_URL=$STEPCODE_BASE_URL; else echo STEPCODE_BASE_URL=UNSET; exit 21; fi; python3 tests/e2e/provider_protocol_smoke.py'
```

- Python version for the local syntax check: system `python3`; the worker smoke did not reach the Python protocol script because the credential gate failed first.
- Credentials: no secret values were printed or stored. The worker command checks only `SET`/`UNSET`.
- Final protocol command additionally sets `STEPCODE_RESPONSE_FORMAT=json_object`.

### 2. Validation Criteria

- Predict-only accepts the `step_main`/H200 resource shape and returns at least one candidate node.
- The live worker reaches `Ready`, reports an H200 GPU, and starts the specified image.
- `STEPCODE_API_KEY` is present on the worker and `STEPCODE_BASE_URL` is non-empty.
- The protocol script checks `/v1/models` for `deepseek-v4-flash`, one provider-supported JSON-object completion, and one follow-up completion containing a standard `tool_calls`/`tool_call_id` message chain.
- The protocol script must report HTTP success and JSON content for both completions. It must not observe provider-side tool execution; local tool execution remains owned by the TVCache agent loop.

### 3. Test Results and Evidence

| Check | Result | Observed evidence |
| --- | --- | --- |
| Local smoke syntax | PASS | `python3 -m py_compile` exited `0`. |
| H200 `step_main` predict-only | PASS | Exit `0`; candidates: `gpu-h200-0761` (8 GPUs), `gpu-h200-0019` (7 free GPUs), `gpu-h200-0844` (8 GPUs). |
| Specified image pull | PASS | `Successfully pulled image` for all live attempts. |
| H200 worker startup | PASS | Final worker reached `Ready` on `gpu-h200-0019`; `GPU_TYPE=H200`; `NODE_COUNT=1`; `PROC_PER_NODE=1`; `nvidia-smi -L` reported `GPU 0: NVIDIA H200`. |
| Image startup contract | PASS after correction | Default entrypoint failed with `vllm: error: unrecognized arguments: -lc` (exit `2`). `--entrypoint=/bin/bash` and `--enable-sshd=false` reached the user command. |
| Worker credential injection | PASS | Final worker output: `STEPCODE_API_KEY=SET`; only presence was logged. |
| `/v1/models` | PASS | HTTP `200`; `deepseek-v4-flash` present. |
| `json_schema` probe | FAIL as expected/unsupported | HTTP `400`; provider message: `response_format type is unavailable now`. |
| `json_object` completion | PASS | HTTP `200`; returned non-empty JSON object content. |
| `role=tool` round-trip | PASS | HTTP `200` after standard assistant `tool_calls` plus matching `tool_call_id`; no provider-side tool execution observed. |
| Provider rollout direct check | PASS | One local tool execution, one generated `tool_call_id`, final answer `2`, reward `1.0`. |
| Async provider unit suite | NOT EXECUTED | System Python and the client virtualenv both lacked an installed pytest async plugin; pytest reported `async def functions are not natively supported`. Production modules compiled successfully. |
| Real agent rollout | NOT RUN | Provider credential gate is a prerequisite. |

The first live attempt exposed the image's missing SSH server: `/usr/sbin/sshd: no such file or directory` (exit `255`) with default `rlaunch` settings. The second attempt reached `Ready` but retained the image's `vllm` entrypoint and exited `2`. The third attempt reached `Ready` and exposed the missing credential (exit `20`). The final command uses `--enable-sshd=false`, `--entrypoint=/bin/bash`, and `--env` injection and passed with exit code `0`.

### 4. Next Gate

The provider protocol gate is complete. The next gate is to prepare the fixed EgoSchema video, start VideoAgent and TVCache services, then run the no-cache and TVCache two-rollout comparison. The production adapter uses `json_object` plus local `Response.model_validate_json()` because the live provider rejects `json_schema`.
