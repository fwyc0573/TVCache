## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-10 | Recorded pinned asset validation, actual GPU loader failures, and scoped environment repairs. |

# Video-LLaVA Offline Loader

## Test Script Information

- Script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/e2e/videollava_offline_probe.py`.
- Worker image: `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`.
- Environment: `/data/ycfeng/tmp/tvcache-videollava-20260909`, Python 3.10.20, Transformers 4.31.0, bitsandbytes 0.41.0, NumPy 1.26.2. Initial Torch was **2.0.1+cu117**, CUDA build **11.7**.
- Allocation: 1 GPU, 8 CPU cores, 65536 MiB RAM; H200 `step_main` first, authorized H800 `codesign` migration when H200 queued.

Run the following on the allocated worker from the worktree root:

```bash
export TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1
export VIDEO_LLAVA_CACHE_DIR=/data/ycfeng/tmp/tvcache-videollava-hf-cache
export VIDEO_LLAVA_RUNTIME_DIR=/data/ycfeng/tmp/tvcache-real-rollout-20260909/videollava-runtime
export TRANSFORMERS_CACHE="$VIDEO_LLAVA_CACHE_DIR"
export HF_HUB_CACHE="$VIDEO_LLAVA_CACHE_DIR" HUGGINGFACE_HUB_CACHE="$VIDEO_LLAVA_CACHE_DIR"
timeout 1200 /data/ycfeng/tmp/tvcache-videollava-20260909/bin/python -u \
  tests/e2e/videollava_offline_probe.py \
  task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/videollava_offline_h800_20260910.json
```

The script enters the runtime directory. Its `cache_dir` symlink points to the existing HF cache because upstream LanguageBind explicitly uses `./cache_dir`; tokenizer resolution uses the global Transformers cache setting. A launcher must remain alive for the worker command: the observed CLI still attached with `--detach`, and a 60-second launcher deadline interrupted execution. The corrected launcher uses 1800 seconds and worker timeout 1200 seconds.

## Validation Criteria

1. All selected snapshot entries resolve to files with sizes equal to pinned metadata, and all three `refs/main` match pinned revisions.
2. Resolve tokenizer, main checkpoint, image tower, and video tower offline.
3. Execute CUDA zeros/sum with actual value **0.0**, expected **0.0** before loading weights.
4. Load the production model with `load_4bit=True`; require `model.is_loaded_in_4bit`, both towers loaded, both processors present, and positive CUDA allocated memory.
5. Record successful load duration, context length, tokenizer length, allocated bytes, and peak bytes. A platform `Succeeded` phase alone does not establish a pass.

## Test Results and Evidence

| Target | Observed | Expected | Verdict |
| --- | --- | --- | --- |
| Video-LLaVA snapshot files | 8 | 8 | PASS |
| LanguageBind Image snapshot files | 8 | 8 | PASS |
| LanguageBind Video snapshot files | 7 | 7 | PASS |
| Snapshot sizes and refs | 23 files match metadata; 3 refs match | All selected files and refs match | PASS |
| Initial H800 import | Missing `scipy` at bitsandbytes/functional.py:12; command exit 1 | Import succeeds | FAIL, repaired |
| CPU import after SciPy installation | `PASS loader_import 1.15.3 2.0.1+cu117 11.7`; exit 0 | Loader imports | PASS |
| H800 four-bit loading after SciPy fix | `CUDA error: no kernel image is available for execution on the device`; exit 1 | Model and towers load | FAIL |
| Complete GPU loader records | 0 | 1 | PENDING |
| Real rollout records | 0 | 4 | PENDING |

Pinned revisions:

- Video-LLaVA: `aecae02b7dee5c249e096dcb0ce546eb6f811806`.
- Image: `d8c2e37b439f4fc47c649dc8b90cdcd3a4e0c80e`.
- Video: `efc40ec6ba6b2081276c11e7e19b24f08a099e79`.

Main checkpoint/tower sizes and SHA-256 values already verified by the downloader and recorded direct checks:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Main shard 1 | 9,976,576,392 | `0e342ae2c6d40d6ebba3328904310a00a2b82e57c728e0e4f5059fe6f7774a03` |
| Main shard 2 | 4,957,139,888 | `fb5c47457569d61be0d2b2d5739f1e30985acc5a61160406880fee64d2c8e111` |
| Image tower | 1,710,619,975 | `99c9382819ef4021e9b2600f030f267d18cc4d5dad39928fdd83ed48887e94bd` |
| Video tower | 2,114,828,105 | `ef677a2ffe018ff22021dd166bc26ffe9196eb414626cbd9a2ac7231308bd52d` |

Failures and logs:

- `tvcache-videollava-offline-20260910-a`: H200 launcher interrupted at 60 seconds; empty loader log. This is an invalid test attempt, not a model pass.
- `tvcache-videollava-offline-20260910-b`: H200 stayed Pending (`RJob is queuing`), intentionally stopped for the authorized H800 migration before loader execution.
- `tvcache-videollava-offline-h800-20260910`: `/data/ycfeng/tmp/tvcache-videollava-offline-h800-20260910.log`, missing SciPy. Root cause: bitsandbytes source imports SciPy while installed metadata does not declare it. Added SciPy 1.15.3 from Basemind; only this package was installed, download 35.9 MiB. Its Python/NumPy constraints match Python 3.10/NumPy 1.26.2.
- `tvcache-videollava-offline-h800-20260910-b`: `/data/ycfeng/tmp/tvcache-videollava-offline-h800-20260910-b.log`, first shard quantization fails at `torch.zeros`. Torch's architecture warning lists sm_37 through sm_86, while the H800 is sm_90. The isolated venv's cu117 build differs from the working image's Torch build.

The prior inference that empty `find -type f` output proved missing snapshots was incorrect: HF snapshot entries are symlinks. Direct file resolution now verifies the 23 entries. No snapshot-loss root cause is established.

## Active Remediation

The same-version official `torch==2.0.1+cu118` and `torchvision==0.15.2+cu118` wheels were found on the PyTorch CUDA 11.8 index after the Basemind public index lacked these builds and the development Torch index returned HTTP 404. Official-index direct access succeeds; proxied TLS timed out. Installation is pending, with model weights, Transformers and bitsandbytes pins retained. Repeat the direct GPU probe after installation before claiming compatibility or starting real rollouts.


Transfer checkpoint: the initial single-stream uv preparation was stopped before reporting installation. Official 1 MiB Range returned HTTP 206 with total 2,267,321,259 bytes; the existing resumable downloader is now fetching the wheel with 64 workers. The checkpoint has 159,383,552 complete bytes (38 parts, 7.03%). Completed parts are reused; transient partial files are excluded. No cu118 installation or successful GPU loader is claimed. Active log: `/data/ycfeng/tmp/tvcache-cu118-ranged64-20260910.log`.


## CUDA 11.8 Repair Verification

- Both official wheels passed SHA-256 before installation: Torch 2,267,321,259 bytes (`a7a49d459bf4862f64f7bc1a68beccf8881c2fa9f3e0569608e16ba6f85ebf7b`); torchvision 6,070,123 bytes (`19ca4ab5d6179bbe53cff79df1a855ee6533c2861ddc7389f68349d8b9f8302a`).
- Exact installation command, completed with exit 0:

```bash
TMPDIR=/data/ycfeng/tmp UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
  timeout 600s systemd-run --user --scope -p MemoryMax=2G uv pip install \
  --python /data/ycfeng/tmp/tvcache-videollava-20260909/bin/python --no-deps --offline \
  '/data/ycfeng/tmp/tvcache-cu118-wheels-20260910/torch-2.0.1+cu118-cp310-cp310-linux_x86_64.whl' \
  '/data/ycfeng/tmp/tvcache-cu118-wheels-20260910/torchvision-0.15.2+cu118-cp310-cp310-linux_x86_64.whl'
```

- CPU import reports `torch 2.0.1+cu118 cuda 11.8 torchvision 0.15.2+cu118`.
- H200 job `tvcache-videollava-cu118-h200-20260910` failed during bitsandbytes import with `libcusparse.so.11: cannot open shared object file`. Torch's CUDA version/architecture detection alone was not a CUDA kernel pass.
- The libraries already exist in the venv. `ldd` resolves every dependency after the following process-local setting:

```bash
VIDEOLLAVA_SITE=/data/ycfeng/tmp/tvcache-videollava-20260909/lib/python3.10/site-packages
export LD_LIBRARY_PATH="$VIDEOLLAVA_SITE/torch/lib:$VIDEOLLAVA_SITE/nvidia/cuda_runtime/lib:$VIDEOLLAVA_SITE/nvidia/cusparse/lib:${LD_LIBRARY_PATH:-}"
```

- H200 job `tvcache-videollava-cu118-h200-20260910-b` uses that setting and the same loader command above, with output `videollava_offline_cu118_h200_20260910_b.json`. Actual CUDA zeros/sum is **0.0**, expected **0.0**, and bitsandbytes import passes. Full loader is still running. Log: `/data/ycfeng/tmp/tvcache-videollava-cu118-h200-20260910-b.log`.

Final H200 b result: **PASS**. Full loader 382.0911647360772 s; allocated and peak 5,408,568,320 bytes; context length 2048; tokenizer length 32000; four_bit=true; image_tower_loaded=true; video_tower_loaded=true; both processor assertions passed. Numeric artifact: `videollava_offline_cu118_h200_20260910_b.json`. This completes the offline loader gate; real tools and rollout remain separate pending gates.
