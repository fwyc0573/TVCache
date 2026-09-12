## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-09 | Recorded the real H200 CUDA check, dependency inventory, and restored disk capacity. |

# H200 Runtime Verification

## Test Script Information

- Script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/e2e/videoagent_runtime_probe.py`.
- Environment: H200 `step_main`, specified `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0` image, Python **3.12.13**, Torch **2.10.0+cu129**, no conda environment.
- Worker node: `gpu-h200-0301.lgcm.sh.istep.fun`.
- Raw result: `/data/ycfeng/tmp/tvcache-runtime-direct-20260909.json`.
- Launch log: `/data/ycfeng/tmp/tvcache-runtime-direct-20260909-launch.log`.

Reproduce from the worktree (use a fresh job name on subsequent runs):

```bash
eval "$(curl -fsS http://deploy.i.shaipower.com/httpproxy)"
export HTTP_PROXY="$http_proxy" HTTPS_PROXY="$https_proxy" NO_PROXY="$no_proxy"
brainctl rjob launch --detach --name=tvcache-runtime-direct-20260909 \
  --namespace=shai-core --charged-group=step_main --private-machine=group \
  --positive-tags=h200 --gpu=1 --cpu=8 --memory=65536 \
  --backoff-limit=1 --max-wait-duration=10m --enable-sshd=false \
  --image=hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0 \
  --entrypoint=/bin/bash --volume=/data:/data \
  --workdir=/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction \
  -- -lc 'export TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1; python3 tests/e2e/videoagent_runtime_probe.py /data/ycfeng/tmp/tvcache-runtime-direct-20260909.json'
```

## Validation Criteria

- CUDA is available and identifies an H200 GPU.
- Allocate four ones on CUDA; the computed sum must equal **4.0**.
- Persist the exact dependency versions and missing distributions for runtime preparation.
- Evaluate model/tool readiness independently from a passing CUDA operation.

## Test Results and Evidence

| Check | Actual | Expected | Verdict |
| --- | --- | --- | --- |
| CUDA availability | `true` | `true` | PASS |
| GPU identity | `NVIDIA H200` | H200 | PASS |
| CUDA sum | **4.0** | **4.0**, absolute difference **0.0** | PASS |
| Python | **3.12.13** | Record actual version | PASS |
| Torch / torchvision | **2.10.0+cu129 / 0.25.0+cu129** | Record actual versions | PASS |
| Transformers / NumPy | **4.57.6 / 2.2.6** | Compare with repository requirements | Different from legacy tool requirements |
| Missing runtime distributions | **11** of the **20** inspected names | All active tool dependencies available before rollout | NOT READY |
| Real rollout | **0 baseline / 0 TVCache** | **2 baseline / 2 TVCache** | PENDING |

Missing distribution names: `ultralytics`, `openai-clip`, `decord`, `moviepy`, `langchain`, `langchain-openai`, `sentence-transformers`, `pytorchvideo`, `peft`, `ftfy`, `opencv-python`. A missing distribution name is an inventory result; constructor imports are the subsequent gate (for example, headless OpenCV can provide `cv2`).

Disk availability after user cleanup was **122,784,391,168 B**, resolving I-055. CLIP completed at **353,976,522 B** with official SHA-256 `40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af`.

The earlier `tvcache-runtime-20260909` launcher hit its **60 s** local timeout before persisting Python results. Its platform `Succeeded` status is not runtime evidence. The subsequent job above produced the complete JSON and launcher exit **0**.

Runtime preparation follows the repository's separate VideoAgent and Video-LLaVA dependencies in new Python **3.10.20** environments under `/data/ycfeng/tmp`; the image's installed Torch remains intact. This report proves the GPU runtime only; constructor, preprocessing, VQA, cache comparison, and teardown verification remain pending.
