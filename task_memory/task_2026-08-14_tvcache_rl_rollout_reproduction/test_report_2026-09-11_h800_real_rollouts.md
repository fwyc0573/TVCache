## Modification History

| Date | Summary of Changes |
|------|--------------------|
| 2026-09-11 | Recorded H800 asset, tool-chain, and four-rollout acceptance evidence. |

# H800 real inference-driven agent rollout report

## Execution

The H200 route was disabled for this run. The worker was submitted to H800 `codesign` with the company image:

```text
hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0
```

The durable rerun instructions and scripts are recorded in [h800_reproduction.md](h800_reproduction.md), [run_real_video_rollouts_h800.sh](../../tests/e2e/run_real_video_rollouts_h800.sh), and [complete_hf_cache_h800.py](../../tests/performance/complete_hf_cache_h800.py).

The reproducible launch used:

```bash
/kubebrain/rlaunch --detach \
  --name=tvcache-real-rollout-h800-20260911-b \
  --namespace=shai-core \
  --charged-group=codesign --private-machine=group --positive-tags=h800 \
  --gpu=2 --cpu=16 --memory=131072 --max-wait-duration=20m \
  --backoff-limit=1 --enable-sshd=false \
  --image=hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0 \
  --entrypoint=/bin/bash --volume=/data:/data \
  --workdir=/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction \
  --env=JOB_ID=tvcache-real-rollout-h800-20260911-b \
  -- -lc 'bash /data/ycfeng/tmp/tvcache-real-rollout-h800-20260911-b.sh'
```

The worker script used Python 3.10.20 environments for VideoAgent and Video-LLaVA, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, the pinned cache at `/data/ycfeng/tmp/tvcache-videollava-hf-cache-h800`, and absolute sandbox/runtime/cache directories under `/data/ycfeng/tmp/tvcache-real-rollout-h800-20260911-b`. `STEPCODE_API_KEY` was read in memory from the controlled StepCode config and only the redacted presence marker was logged.

## Criteria

- Video-LLaVA four-bit loader must initialize on H800 with both image and video towers.
- Captioning, SegmentFeature, Tracking, sandbox start, and `load_video_into_sandbox` must pass.
- Produce exactly two no-cache and two TVCache rollouts for the fixed EgoSchema video.
- Each rollout must return a valid answer, execute local JSON actions, and record provider token usage and tool/cache metrics.
- TVCache must report hits/forks and converge all drain/stop/ACK lifecycle state to zero.
- No run sandbox may remain after teardown.
- RL optimizer update is outside this acceptance scope.

## Evidence

### Asset and tool gates

The H800 offline probe produced `/data/ycfeng/tmp/videollava-offline-probe-h800.json` with `status=PASS`, GPU `NVIDIA H800`, Torch `2.0.1+cu118`, four-bit loading, tokenizer vocabulary `32000`, image/video towers loaded, and `allocated_bytes=3525137920`. The independent cache probe also loaded LanguageBind image/video towers locally.

The tool smoke artifact is [tvcache-real-rollout-h800-20260911-b-tool-smoke.json](tvcache-real-rollout-h800-20260911-b-tool-smoke.json). `/start` and `load_video_into_sandbox` returned HTTP 200. Sandbox logs show successful Captioning, viCLIP SegmentFeature, and object Tracking construction and preprocessing.

### Rollout metrics

Artifacts are in [tvcache-real-rollout-h800-20260911-b-rollouts](tvcache-real-rollout-h800-20260911-b-rollouts).

| Variant | Index | Reward | Answer | Elapsed (s) | Calls | Executions | Exact | Prefix | Misses | Forks | Puts | Prompt / Completion / Total tokens |
|---------|------:|-------:|-------:|------------:|------:|-----------:|------:|-------:|-------:|------:|-----:|-----------------------------------:|
| no-cache | 0 | 1.0 | 1 | 235.0006 | 26 | 26 | 0 | 0 | 26 | 0 | 0 | 31971 / 4419 / 36390 |
| no-cache | 1 | 1.0 | 1 | 168.4909 | 15 | 15 | 0 | 0 | 15 | 0 | 0 | 14804 / 1990 / 16794 |
| tvcache | 0 | 1.0 | 1 | 195.1357 | 20 | 20 | 0 | 19 | 1 | 2 | 20 | 20331 / 2122 / 22453 |
| tvcache | 1 | 1.0 | 1 | 65.5046 | 18 | 13 | 5 | 13 | 0 | 1 | 13 | 21577 / 2258 / 23835 |

`summary.json` reports `completed_rollouts=4`, `no_cache_rollouts=2`, `tvcache_rollouts=2`, `tvcache_exact_hits=5`, and `remaining_run_sandboxes=[]`. The TVCache log contains real environment fork, cache store, and cached-environment lookup events. The reduced execution count in `tvcache-1` is explained by five exact cache hits.

### GPU and teardown

The retained GPU monitor is [gpu-memory.csv](/data/ycfeng/tmp/tvcache-real-rollout-h800-20260911-b/gpu-memory.csv). Across 1,016 samples per GPU, observed memory used ranged from 1 MiB to 6,350 MiB on GPU 0 and 1 MiB to 9,756 MiB on GPU 1; each H800 reports 81,559 MiB total. `brainctl get rjob tvcache-real-rollout-h800-20260911-b -n shai-core` returned `Succeeded`. The rollout log records sandbox stop operations and successful lifecycle completion; the summary confirms no residual run sandbox.

## Result

**PASS for the fixed single-video, four-rollout real rollout acceptance scope.** Provider inference, local JSON action parsing, ordinary-message tool-result history, local tool execution, sandbox lifecycle, and TVCache statistics were exercised. No RL optimizer update was executed. The benign absent-warmed-environment withdrawal warning is retained in logs as an operational watch item; it did not prevent lifecycle convergence or artifact completion.
