## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-09 | Recorded fresh H200 capacity and the failed direct mirror network probe. |

# H200 Download Route Probe

## Test Script Information

- Script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/e2e/worker_download_probe.py`.
- Worker image: `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`.
- Environment: H200 step_main, Python 3.12 (traceback); exact patch version was not collected in the failed probe; no conda environment.
- Resources: 1 GPU, 8 CPU, 65,536 MiB memory, 1 replica.
- Job: `tvcache-h200-network-20260909-1706`.
- Node: `gpu-h200-0301.lgcm.sh.istep.fun`.
- Logs: `/data/ycfeng/tmp/tvcache-h200-network-20260909-launch.log` and `/data/ycfeng/tmp/tvcache-h200-predict-20260909-continuation.log`.

Exact worker payload (reproduce within the specified image and mounted worktree):

```bash
set -e
eval "$(curl -fsS http://deploy.i.shaipower.com/httpproxy)"
export HTTP_PROXY="$http_proxy" HTTPS_PROXY="$https_proxy" ALL_PROXY="$all_proxy"
export NO_PROXY="$no_proxy,hf-mirror.com,.cdn.hf.co,.xethub.hf.co"
export no_proxy="$NO_PROXY" TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1
nvidia-smi -L
timeout 60s python3 tests/e2e/worker_download_probe.py \
  /data/ycfeng/tmp/tvcache-h200-network-20260909.json
```

Launch flags:

```bash
brainctl rjob launch --detach --name=tvcache-h200-network-<fresh-suffix> \
  --namespace=shai-core --charged-group=step_main --private-machine=group \
  --positive-tags=h200 --gpu=1 --cpu=8 --memory=65536 \
  --backoff-limit=1 --max-wait-duration=30m --enable-sshd=false \
  --image=hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0 \
  --entrypoint=/bin/bash --volume=/data:/data --workdir="$PWD" \
  -- -lc '<exact worker payload above>'
```

## Validation Criteria

- Establish current scheduling capacity independently from download throughput.
- Request exactly 8,388,608 bytes with HTTP 206 and the corresponding Content-Range.
- Record sustained received bytes and elapsed time within the bounded probe.
- Move downloads to the worker only if an operational route and improved throughput are observed.

## Test Results and Evidence

| Check | Observed | Expected | Verdict |
| --- | --- | --- | --- |
| Predict-only | 1 candidate, 7 GPUs, 166 CPUs, 1,865.1 GiB memory | Capacity for 1 GPU/8 CPU/64 GiB | PASS |
| Scheduling | Created 17:05:55, scheduled 17:05:58, Ready 17:06:19 (+08:00) | Worker reaches runnable state | PASS |
| Direct mirror connection | requests.exceptions.ConnectTimeout; connect timeout configured as 10 s | Successful HTTPS connection | FAIL |
| Downloaded response bytes | 0; response connection never established | 8,388,608 B | FAIL |
| Launcher exit / final RJob phase | 1 / Failed | 0 / Succeeded | FAIL |
| Throughput JSON | Not created because the request raised first | Completed numeric artifact | NOT AVAILABLE |

Failure excerpt: `Connection to hf-mirror.com timed out. (connect timeout=10)`.

The failed branch is the direct external mirror route on this worker. GPU allocation succeeded; this is not evidence of H200 capacity exhaustion and does not trigger the user's H800 capacity fallback. The CPU master remains the download host. Its mirror range download is in progress and each final blob must match the official Hugging Face LFS SHA-256 before use. No real rollout was executed by this diagnostic.
