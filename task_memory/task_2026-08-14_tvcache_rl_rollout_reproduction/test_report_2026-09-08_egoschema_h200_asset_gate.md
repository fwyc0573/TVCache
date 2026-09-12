## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-08 | Recorded the fixed EgoSchema video validation and H200 `step_main` VideoAgent asset gate. |

# Test Report: EgoSchema H200 Asset Gate

## 1. Test Script Information

- Test script: direct `ffprobe`/SHA-256 checks and the H200 `rlaunch` preflight command recorded in `progress.md`.
- Persistent input: `/data/ycfeng/tvcache_assets/egoschema/run-20260908/videos/0c481667-9303-4f4a-b331-0b412aaafa2d.mp4`.
- Reproducible local metadata command:

  ```bash
  ffprobe -v error -show_entries format=duration,size -of default=nw=1 \
    /data/ycfeng/tvcache_assets/egoschema/run-20260908/videos/0c481667-9303-4f4a-b331-0b412aaafa2d.mp4
  sha256sum /data/ycfeng/tvcache_assets/egoschema/run-20260908/videos/0c481667-9303-4f4a-b331-0b412aaafa2d.mp4
  ```

- Worker command: H200 `step_main`, `--gpu=1 --cpu=8 --memory=32768`, image `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`, `--enable-sshd=false`, `--entrypoint=/bin/bash`, `/data:/data`, and controlled `STEPCODE_API_KEY` injection. The secret value is intentionally omitted from this report.
- Environment: H200 worker `gpu-h200-0482.lgcm.sh.istep.fun`, container Python `3.12.13`, NVIDIA H200, `STEPCODE_BASE_URL=https://models-proxy.stepfun-inc.com`.

## 2. Validation Criteria

- Video exists on the persistent NFS path, is decodable, and matches the selected `processed_videos.json` row.
- The worker sees exactly one H200 GPU and the provider credential is present without exposing its value.
- The worker exposes a VideoAgent model directory, Video-LLaVA runtime directory, or matching preprocessing cache sufficient for `SandboxManager` startup.
- Acceptance requires the last condition before a real visual tool-chain or rollout is started.

## 3. Test Results and Evidence

| Check | Observed value | Result |
| ----- | -------------- | ------ |
| Video bytes | `5,732,750` | PASS |
| Video duration | `180.000000 s` | PASS |
| Video codec / geometry | H.264, `480x360`, `30/1` fps | PASS |
| Video SHA-256 | `db2bb94ff43ccb040fe5fd117e19e6f907e9065d74ec7276596a9c8ba4d554af` | PASS |
| Worker GPU | `GPU 0: NVIDIA H200` | PASS |
| Provider credential presence | `STEPCODE_API_KEY=SET` | PASS |
| `/models` and `/data/models` | absent | FAIL for runtime readiness |
| VideoAgent weights/runtime/cache | absent on mounted `/data` | FAIL for runtime readiness |

`SandboxManager.__init__` constructs `Captioning`, `SegmentFeature`, and `Tracking`; those constructors load LaViLa, viCLIP, CLIP, DINOv2, and RT-DETR assets. `ToolKit` additionally requires viCLIP and a Video-LLaVA socket/runtime. Therefore an empty model directory cannot satisfy the service contract. The real visual tool-chain and the no-cache/TVCache rollout comparison are **BLOCKED** at the asset gate. No synthetic tool result was accepted as evidence.
