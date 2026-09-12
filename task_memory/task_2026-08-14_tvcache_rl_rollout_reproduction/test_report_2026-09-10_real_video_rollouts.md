## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-10 | Recorded real service startup, launcher failure, and fixed-snapshot continuation. |

# Real VideoAgent Services and Provider Cache Rollouts

## Execution

Repository: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction`.

Scripts under that repository:

- `tests/e2e/run_real_video_rollouts.sh`
- `tests/e2e/videoagent_tool_smoke.py`
- `tests/e2e/provider_cache_rollout.py`

Worker: H200 `step_main`, 2 GPUs, 16 CPUs, 131072 MiB RAM. Image: `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`.

Environments:

- VideoAgent: `/data/ycfeng/tmp/tvcache-videoagent-20260909`, Python 3.10.
- Video-LLaVA: `/data/ycfeng/tmp/tvcache-videollava-20260909`, Python 3.10.20, Torch 2.0.1+cu118.
- Controller: `/data/ycfeng/tmp/tvcache-train-py312`, Python 3.12.3.

Exact attempt-b worker command from the repository root:

```bash
export REPO_DIR="$PWD"
timeout --signal=TERM --kill-after=30 12600 \
  bash /data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-b.sh
```

The snapshot was copied from the repository shell script before launch and remains unchanged while Bash executes it. The launcher uses a 14400-second deadline. The shell injects the existing StepCode config key into environment, prints only SET, configures local paths and the verified VQA library path, and records raw logs in `/data/ycfeng/tmp/$JOB_ID`.

## Criteria

1. VQA Unix socket ready; sandbox HTTP service ready; TVCache `/get` returns 200.
2. Real tools: start -> load fixed video -> preprocess -> caption retrieval -> segment localization -> VQA -> stop. Every request succeeds with a nonempty output; VQA has both description and answer; the smoke sandbox disappears after stop.
3. Same EgoSchema question, no-cache x2 then TVCache x2. Require complete answers, local tools, numeric reward/latency/token/tool/cache/fork metrics, and at least one exact cache hit.
4. Associate sampled GPU memory with recorded rollout wall-clock intervals. Check run sandbox teardown and owned service termination.

## Evidence and Current Result

- Fixed video: `0c481667-9303-4f4a-b331-0b412aaafa2d.mp4`, answer index 1, manifest in this task directory.
- Before tool execution: sandbox directory entries 0; shared preprocessing-cache entries 0.
- Attempt a, `tvcache-real-rollout-h200-20260910`: all three services reached ready; VQA logged `ready for connection!`, sandbox listened on 5000, TVCache `/get` returned 200. Captioning construction took 60.449 s. Each H200 reported 143771 MiB total memory. Key presence was SET.
- Attempt a **FAIL** before tool smoke: exit 127, shell `line 67: t: command not found`. Cause: an earlier line was edited while Bash was still reading the file. All four owned processes exited in cleanup (VQA 143, sandbox 143, cache 143, monitor 0).
- Correction: unique shell snapshot and explicit REPO_DIR. Attempt b, `tvcache-real-rollout-h200-20260910-b`, scheduled on gpu-h200-1006.lgcm.sh.istep.fun. Services/tools/rollouts are pending live completion.
- Real rollout records: **0/4**, pending. No reward, cache benefit, latency comparison, or final GPU metric is claimed yet.

Logs: `/data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-launch.log`, `/data/ycfeng/tmp/tvcache-real-rollout-h200-20260910/`, `/data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-b-launch.log`, `/data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-b/`.

## Attempt b: Real Tool Smoke PASS

All seven HTTP requests returned 200 and success=true. Start 0.0229123542 s; load 0.2244450701 s; preprocess 144.4232299067 s; caption 0.6344481488 s; localization 2.1142926929 s; VQA 17.3319152980 s; stop 0.0512400423 s. The 90-segment video produced local captions and visual embeddings. VQA returned: "The person is painting a picture of a field on a wall." Both required VQA fields were present, and the sandbox directory disappeared after stop. Artifact: `tvcache-real-rollout-h200-20260910-b-tool-smoke.json`. This confirms tool execution and teardown; semantic VQA answer accuracy is not separately scored by the smoke.

## Attempt b: First Rollout FAIL

The first no-cache rollout executed local tools, then failed strict JSON parsing: `Invalid JSON: trailing characters at line 16 column 1`, with DSML calls appended after JSON. The original driver did not save the full failing response or partial token metrics. Therefore completed numeric rollout records remain 0/4. The failing sandbox stopped with HTTP 200; all service processes exited in the shell trap (143/143/143/0), launcher exit 1. Provider JSON/native-tool output interaction is under investigation with a separate protocol replay; no malformed-response stripping or fallback has been applied.


## Provider JSON Boundary Repair

- Direct script: `tests/e2e/provider_tool_history_probe.py`, controller Python 3.12.3. It replays the fixed question and actual smoke outputs; it is a protocol test, not a counted rollout.
- Commands from the repository root, with company proxy configured:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/train" \
  /data/ycfeng/tmp/tvcache-train-py312/bin/python tests/e2e/provider_tool_history_probe.py \
  --output /data/ycfeng/tmp/tvcache-provider-history-original-20260910.json
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/train" \
  /data/ycfeng/tmp/tvcache-train-py312/bin/python tests/e2e/provider_tool_history_probe.py \
  --tool-choice-none --output /data/ycfeng/tmp/tvcache-provider-history-none-20260910.json
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  tvcache/client/.venv/bin/python -m pytest -q tests/unit/test_provider_chat_client.py -p no:cacheprovider
```

- Original: HTTP 200, 2.7503469851 s, 2513 prompt / 135 completion / 2648 total tokens; JSON followed by DSML invoke, schema validation FAIL.
- Explicit `tool_choice=none`: HTTP 200, 1.8190864681 s, 2513 prompt / 231 completion / 2744 total tokens; pure JSON actions, schema validation PASS.
- Production client now requests content-only JSON while preserving native tool history and local JSON action execution. It continues strict parsing of every response. Focused regression: **8/8 PASS in 1.02 s**, existing Python 3.10 client test environment.
- Driver now persists each response and usage before schema parsing, preserving future failure evidence. Full rollout validation remains pending.

Protocol evidence is also persisted in this task directory as `provider_history_original_20260910.json` and `provider_history_none_20260910.json`; neither records Authorization headers. Attempt c uses `/data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-c.sh`, a fixed snapshot of the same service entrypoint with the already-passed smoke invocation omitted. The four-rollout command and acceptance checks are unchanged apart from the validated provider output setting and per-response logging.


## Attempt c and Exact-History Protocol Diagnosis

**Actual rollout FAIL.** The first no-cache rollout executed five local tools, then its third provider response contained trailing DSML. Partial provider usage is 6786 prompt / 802 completion / 7588 total tokens. Completed numeric rollout records remain 0/4; reward and performance comparison are pending. The failing sandbox stopped with HTTP 200; service exits were 143/143/143/0, launcher exit 1. Full exchanges are preserved in `tvcache-real-rollout-h200-20260910-c-rollouts/no-cache-0-provider.jsonl`.

The prior `tool_choice=none` conclusion is superseded: one successful protocol sample and payload unit tests did not prove real protocol reliability. No malformed-response stripping is used.

Run the same direct script with the actual failing history:

```bash
export TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/train"
HISTORY=task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/tvcache-real-rollout-h200-20260910-c-rollouts/no-cache-0-provider.jsonl
/data/ycfeng/tmp/tvcache-train-py312/bin/python tests/e2e/provider_tool_history_probe.py \
  --history "$HISTORY" --tool-choice-none --json-arguments \
  --output /data/ycfeng/tmp/tvcache-provider-json-arguments-20260910.json
/data/ycfeng/tmp/tvcache-train-py312/bin/python tests/e2e/provider_tool_history_probe.py \
  --history "$HISTORY" --tool-choice-none --disable-thinking \
  --output /data/ycfeng/tmp/tvcache-provider-disable-thinking-20260910.json
/data/ycfeng/tmp/tvcache-train-py312/bin/python tests/e2e/provider_tool_history_probe.py \
  --history "$HISTORY" --text-history \
  --output /data/ycfeng/tmp/tvcache-provider-text-history-20260910.json
/data/ycfeng/tmp/tvcache-train-py312/bin/python tests/e2e/provider_tool_history_probe.py \
  --history "$HISTORY" --native-tools --json-arguments \
  --output /data/ycfeng/tmp/tvcache-provider-native-tools-20260910.json
```

These are protocol probes using recorded results, not counted real rollouts. Raw request/response evidence is also persisted under `provider_protocol_*_20260910*.json` in this task directory.

| Protocol probe | HTTP | Seconds | Prompt / completion / total tokens | Observed verdict |
| --- | ---: | ---: | --- | --- |
| JSON native arguments + none | 200 | 2.591786147 | 2673 / 456 / 3129 | FAIL: DSML tail |
| Disabled thinking + none | 200 | 2.475934667 | 2649 / 235 / 2884 | FAIL: DSML tail; reasoning tokens 0 |
| Text result history, sample 1 | 200 | 2.201208508 | 2512 / 315 / 2827 | PASS: Response schema |
| Text result history, sample 2 | 200 | 2.470019207 | 2512 / 283 / 2795 | PASS: Response schema |
| Text result history, sample 3 | 200 | 1.754977859 | 2512 / 155 / 2667 | PASS: Response schema |
| Declared native video tools | 200 | 2.097947476 | 2506 / 300 / 2806 | PASS: 3 native caption_retrieval calls with valid inputs |

A forced `agent_response` function was also investigated: thinking mode returned HTTP 400; disabling thinking returned other function names, failing the requested-function assertion. This route is not recommended.

Text history requires removing synthetic assistant.tool_calls and returning tool outputs as ordinary messages while preserving local JSON actions, tool execution and cache accounting. Native tools require aligning declared functions, provider decoding, history and final-answer handling. Both depart from the current recorded wire protocol; implementation is awaiting the user's decision. Three replay passes support the text-history candidate but do not establish four-rollout success.
