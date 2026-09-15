## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-15 | Recorded completed cloud transfer and actual worker verification. |

# Cloud persistence verification

Result: PASS. The personal cloud task directory contains the pinned source archive, P03 evidence, runtime manifest, and complete data for ten selected images. The worker verified copied files and registry blobs before writing `manifests/ASSETS_COMPLETE.json`.

## Execution

Working directory: `/data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox`.

Launcher environment: `/data/ycfeng/tmp/stepmind-env/bin/python`, Python 3.10.6, no conda activation. Worker image is the handbook-verified StepMind image. Personal Python RJobBackend submitted locally with H200 + step_main and the declared JuiceFS mount.

```bash
STEPMIND_BACKEND=rjob TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
STEPMIND_PYTHON=/data/ycfeng/tmp/stepmind-env/bin/python \
/data/ycfeng/tmp/stepmind-env/bin/python \
  /data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox/tests/e2e/rejoin_worker.py \
  --image hub.i.basemind.com/stepmind/megatron-step:test-optimus-3.24.0-stepccl-0.0.5.post5-vllm-0.11.0.post37-20260817-2733176 \
  --source /data/ycfeng/tmp/rejoin-p04-control \
  --report /data/ycfeng/tmp/rejoin-p04-control/storage_worker.json \
  -- bash -lc 'python3 /data/ycfeng/tmp/rejoin-p04-control/rejoin_cloud.py --config /data/ycfeng/tmp/rejoin-p04-control/storage_config.json --report /data/ycfeng/tmp/rejoin-p04-control/storage_worker_report.json'
```

## Criteria and evidence

| Check | Expected | Observed |
| --- | --- | --- |
| Personal cloud root | All writes under ycfeng | `/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3` |
| Source revision | Matches P03 pin | `d28711d0da2675d0bb1d56de45ae5df6082438a3` |
| Staged file copies | Every size/hash matches | 67/67 passed |
| Complete image data | Ten manifests and every referenced blob | 10/10 images, 69 unique blobs passed |
| Compressed blob size | Inventory equals copied bytes | 1,452,034,837 bytes |
| Creator | i-fengyicheng | i-fengyicheng |
| NFS source | Current local machine | `100.96.128.193:/data/ycfeng/tmp/rejoin-p04-control` |
| Worker GPU command | Reports H200 | NVIDIA H200 |
| Worker terminal status | succeeded | succeeded |

Job: `exp-0915-140553-008483`. Detailed reports are in `cloud_evidence/` and on the cloud under `reports/storage_transfer.json`. This proves preservation and integrity; launching an image directly from the OCI archive has not been tested. Registry images remain available by their recorded digests.

## Corrected failures

- Missing `EXP_ID` stopped the first local launcher before job creation. The launcher now sets the required experiment identifier.
- Task image job `exp-0915-135631-557982` lacked `nvidia-smi` and exited before copying data. Storage now runs in the handbook's verified full worker image. Old P03 GPU-command logs contain the same error; their verifier results remain valid, while successful GPU-command evidence begins with this transfer job.
- Provider preflight returned HTTP 200 with valid JSON in 1.27 seconds. It establishes current provider access, not P04 rollout success.
