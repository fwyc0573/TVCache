## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-15 | Defined the cloud asset layout and verification steps for P03 persistence and P04 collection. |

# ReJoin cloud storage

Root: `/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3`.

| Directory | Contents |
| --- | --- |
| `sources/` | Compressed pinned Terminal-Bench source, including task definitions, solutions, and verifiers; controller access only. |
| `images/oci/` | Final registry manifests, configs, and compressed layers for all ten task images, stored once per digest. |
| `manifests/` | W1 selection, runtime image identities, source revision, and transfer inventory. |
| `code/` | Reusable research and worker scripts without credentials. |
| `evidence/p03/` | Build metadata, final Dockerfiles, solution/verifier logs, and worker records. |
| `rollouts/p04/<run-id>/<task-id>/<rollout-id>/` | Requests/responses, JSONL trace, workspace observations, final workspace archive, verifier logs, and completion records. |
| `rollouts/p05/<run-id>/<task-id>/<rollout-id>/` | Ten-task opportunity-pilot requests/responses, traces, workspace observations, archives, and verifier artifacts. |
| `reports/` | Transfer verification and smoke gate reports. |
| `reports/p05/<run-id>/` | Merged A/B/C/U/N report, JSON totals, and O1/O2/O3 SVG figures. |

Dependency order: local inventory -> compressed source and evidence staging -> worker cloud transfer -> image layer verification -> P04 collection -> smoke gate report. Provider preflight can run alongside transfer preparation.

Use H200 + step_main through local StepMind Python RJobBackend. The worker dynamically mounts the documented JuiceFS volume. Stream image blobs to the cloud directory; do not download image layers onto the CPU master. Finish large files before publishing a completion marker. Verify each image digest and layer size/hash, source revision, file counts, and copied evidence before recording success.

P04 and P05 write durable outputs directly under their phase-specific cloud run directories. Task execution and package/compiler caches use temporary worker storage, with the final workspace compressed into the run directory. Model tool processes receive neither provider credentials nor access to controller-only task solutions and verifiers.

Transfer status: PASS. Job `exp-0915-140553-008483` completed with 67 verified files, ten images, 69 unique blobs, and 1,452,034,837 blob bytes. Worker `nvidia-smi` reported NVIDIA H200, creator was `i-fengyicheng`, and terminal status was `succeeded`. The complete transfer report is preserved in `cloud_evidence/storage_worker_report.json`.

P04 provider preflight: PASS, HTTP 200 with valid JSON, 1.27 seconds. Base URL is `https://models-proxy.stepfun-inc.com`; model is `deepseek-v4-flash`. This preflight is not a completed rollout.

P05 persistence and analysis: PASS. Main run `p05-20260915-v2` produced 40 rollout records; five provider collection errors were replaced by successful v3 retry records under the run map `p05_run_map.json`. Merged checker `p05-merged.aggregate.json` reports 40/40 reload and zero collection errors. Final opportunity report and figures are under `reports/p05/p05-20260915-v2/`; analysis jobs `exp-0915-222550-684805` and `exp-0915-223247-819216` used H200/step_main and the current local NFS source.
