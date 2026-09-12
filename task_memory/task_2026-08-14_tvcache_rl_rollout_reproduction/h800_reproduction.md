## Modification History

| Date | Summary of Changes |
|------|--------------------|
| 2026-09-11 | Added the durable H800 reproduction recipe, cache assembly command, launch command, and post-run checks. |

# H800 reproduction recipe

This document reproduces the accepted single-video experiment from a CPU master. It uses one H800 worker with two GPUs: GPU 0 runs VideoAgent and TVCache, and GPU 1 runs Video-LLaVA. The provider performs model inference only. The local agent loop parses JSON `actions`, executes tools, writes tool results back as ordinary messages, and records TVCache metrics. No Tinker or RL optimizer update is used.

## Fixed inputs and persistent assets

Use the existing worktree and fixed EgoSchema manifest:

```bash
export REPO_DIR=/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction
export TASK_DIR="$REPO_DIR/task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction"
export MANIFEST="$TASK_DIR/egoschema_manifest_2026-09-08.json"
```

The manifest points to the fixed video under:

```text
/data/ycfeng/tvcache_assets/egoschema/run-20260908/videos/0c481667-9303-4f4a-b331-0b412aaafa2d.mp4
```

Required persistent runtime assets:

| Asset | Path |
|---|---|
| VideoAgent small models | `/data/ycfeng/tmp/videoagent_small` |
| VideoAgent Python | `/data/ycfeng/tmp/tvcache-videoagent-20260909` |
| Video-LLaVA Python | `/data/ycfeng/tmp/tvcache-videollava-20260909` |
| Training/provider Python | `/data/ycfeng/tmp/tvcache-train-py312` |
| HF cache | `/data/ycfeng/tmp/tvcache-videollava-hf-cache-h800` |
| HF inventory | `/data/ycfeng/tmp/tvcache-asset-inventory-20260909` |

The HF cache must contain these pinned revisions:

```text
LanguageBind/Video-LLaVA-7B       aecae02b7dee5c249e096dcb0ce546eb6f811806
LanguageBind/LanguageBind_Image    d8c2e37b439f4fc47c649dc8b90cdcd3a4e0c80e
LanguageBind/LanguageBind_Video_merge efc40ec6ba6b2081276c11e7e19b24f08a099e79
```

## Prepare or repair the HF cache

The company Hugging Face mirror is preferred. The durable assembly script links already verified blobs, downloads missing metadata, skips the duplicate Video-LLaVA PyTorch checkpoint shards, and writes newline-free `refs/main` entries required by `huggingface_hub==0.20.3`:

```bash
cd "$REPO_DIR"
python3 tests/performance/complete_hf_cache_h800.py \
  --cache-dir /data/ycfeng/tmp/tvcache-videollava-hf-cache-h800 \
  --inventory-dir /data/ycfeng/tmp/tvcache-asset-inventory-20260909 \
  --endpoint https://artifactory.stepfun-inc.com/artifactory/api/huggingfaceml/huggingface-mirror
```

Do not download `pytorch_model-00001-of-00002.bin` or `pytorch_model-00002-of-00002.bin` for Video-LLaVA when the pinned safetensors shards are present; they duplicate approximately 15 GB of weights.

## Verify the H800 loader before a long run

Create a runtime directory and point its `cache_dir` symlink at the H800 cache. In the worker, set:

```bash
export HF_HOME=/data/ycfeng/tmp/tvcache-videollava-hf-cache-h800
export HF_HUB_CACHE="$HF_HOME" HUGGINGFACE_HUB_CACHE="$HF_HOME" TRANSFORMERS_CACHE="$HF_HOME"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export VIDEO_LLAVA_CACHE_DIR="$HF_HOME"
export VIDEO_LLAVA_RUNTIME_DIR=/data/ycfeng/tmp/videollava-runtime-h800-probe
mkdir -p "$VIDEO_LLAVA_RUNTIME_DIR"
ln -sfn "$HF_HOME" "$VIDEO_LLAVA_RUNTIME_DIR/cache_dir"
```

Run the production loader probe on a two-GPU H800 worker with the Video-LLaVA Python environment and the process-local CUDA library path:

```bash
VIDEOLLAVA_SITE=/data/ycfeng/tmp/tvcache-videollava-20260909/lib/python3.10/site-packages
LD_LIBRARY_PATH="$VIDEOLLAVA_SITE/torch/lib:$VIDEOLLAVA_SITE/nvidia/cuda_runtime/lib:$VIDEOLLAVA_SITE/nvidia/cusparse/lib:${LD_LIBRARY_PATH:-}" \
PYTHONPATH="$REPO_DIR/video-agent-tools/Video-LLaVA" \
/data/ycfeng/tmp/tvcache-videollava-20260909/bin/python \
  "$REPO_DIR/tests/e2e/videollava_offline_probe.py" \
  /data/ycfeng/tmp/videollava-offline-probe-h800.json
```

Expected result is `status=PASS`, `gpu=NVIDIA H800`, `four_bit=true`, and both `image_tower_loaded` and `video_tower_loaded` set to `true`.

## Check capacity and launch the complete experiment

Read the authoritative worker handbook before allocation:

```text
/data/ycfeng/stepfun-env-handbook/guidence.md
```

Run predict-only first:

```bash
/kubebrain/rlaunch --predict-only \
  --name=tvcache-real-rollout-h800-repro-predict \
  --namespace=shai-core \
  --charged-group=codesign --private-machine=group --positive-tags=h800 \
  --gpu=2 --cpu=16 --memory=131072 --predict-node-num=10 \
  -- bash -lc 'true'
```

Submit the durable worker script. Set a unique `JOB_ID` for every run; its value namespaces logs, runtime directories, sandbox directories, and output artifacts:

```bash
export JOB_ID=tvcache-real-rollout-h800-repro-$(date +%Y%m%d-%H%M%S)
/kubebrain/rlaunch --detach \
  --name="$JOB_ID" --namespace=shai-core \
  --charged-group=codesign --private-machine=group --positive-tags=h800 \
  --gpu=2 --cpu=16 --memory=131072 --max-wait-duration=20m \
  --backoff-limit=1 --enable-sshd=false \
  --image=hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0 \
  --entrypoint=/bin/bash --volume=/data:/data \
  --workdir="$REPO_DIR" --env=JOB_ID="$JOB_ID" \
  -- -lc "bash $REPO_DIR/tests/e2e/run_real_video_rollouts_h800.sh"
```

The worker script reads `STEPCODE_API_KEY` in memory from `STEPCODE_CONFIG` (default `/data/ycfeng/home_offload/i-fengyicheng/.stepcode/config.json`). To use a different controlled secret path, pass only the path:

```bash
--env=STEPCODE_CONFIG=/data/<controlled-secret-path>/.stepcode/config.json
```

The key value must never be placed in `rlaunch` arguments, shell history, logs, task records, or provider traces. The script logs only `STEPCODE_API_KEY=SET`.

## Monitor and inspect outputs

Check the RJob without unbounded API output:

```bash
timeout 60s systemd-run --user --scope -p MemoryMax=2G \
  brainctl get rjob "$JOB_ID" -n shai-core
```

The worker writes:

```text
/data/ycfeng/tmp/$JOB_ID/vqa.log
/data/ycfeng/tmp/$JOB_ID/sandbox.log
/data/ycfeng/tmp/$JOB_ID/cache.log
/data/ycfeng/tmp/$JOB_ID/rollouts.log
/data/ycfeng/tmp/$JOB_ID/gpu-memory.csv
$TASK_DIR/$JOB_ID-tool-smoke.json
$TASK_DIR/$JOB_ID-rollouts/no-cache-0.json
$TASK_DIR/$JOB_ID-rollouts/no-cache-1.json
$TASK_DIR/$JOB_ID-rollouts/tvcache-0.json
$TASK_DIR/$JOB_ID-rollouts/tvcache-1.json
$TASK_DIR/$JOB_ID-rollouts/summary.json
```

Acceptance requires all four rollout JSON files, reward `1.0`, correct final answer index `1`, non-empty `tool_calls`, provider token totals, cache hit/miss counters, and `summary.json` with:

```text
completed_rollouts=4
no_cache_rollouts=2
tvcache_rollouts=2
remaining_run_sandboxes=[]
tvcache_exact_hits > 0
```

The TVCache lifecycle must finish with zero pending drain, environment-stop, and drain-ACK operations. The worker must reach `Succeeded`. Retain `gpu-memory.csv` and all provider/sandbox/cache logs with the task artifacts.

## Known runtime requirements

- Use `--enable-sshd=false`; the StepCast image does not provide `/usr/sbin/sshd` for the default sidecar path.
- Keep `REPO_DIR` explicit when invoking a script from `/data/ycfeng/tmp`; otherwise relative path derivation can resolve to `/data`.
- Set both `HF_HUB_CACHE` and `HUGGINGFACE_HUB_CACHE`; the legacy `huggingface_hub` used by Video-LLaVA consults the latter.
- Keep the Video-LLaVA CUDA library path process-local. The VideoAgent process uses its own Python environment and GPU.
- Use the company worker proxy recipe before service startup. The HF mirror is used only for cache preparation; the accepted rollout itself runs in offline mode.
- Do not reuse a prior run's sandbox, runtime, or rollout output directory. Use a fresh `JOB_ID`.
