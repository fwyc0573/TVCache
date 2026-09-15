## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Archived the planning result for ReJoin v3. |
| 2026-09-15 | Archived P03 runtime image, digest, verifier, and tool-surface evidence. |
| 2026-09-15 | Added cloud preservation results and the queued P04 execution checkpoint. |

# Task Overview

The v3 Chinese ReJoin plan was read in full and converted into a durable execution record. P00 baseline capture, P01 B01 issue locking, P02 lightweight harness construction, and P03 cohort/runtime preparation are complete. The resulting plan preserves the early-stage research order: measure post-divergence opportunity with real observation traces, then test a small guarded memoizer, and enter TVCache integration only after both evidence gates are positive.

# Deliverables Inventory

- Source analyzed: [`draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md`](../../draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md)
- Requirements and acceptance criteria: [`requirements.md`](requirements.md)
- Source findings and repository anchors: [`findings.md`](findings.md)
- Research design and evidence flow: [`design.md`](design.md)
- Ordered execution packets, dependencies, gates, deferred work, and open decisions: [`plan.md`](plan.md)
- Session progress and decisions: [`progress.md`](progress.md)
- Operational and disk notes: [`notes.md`](notes.md)
- P02 scripted trace: [`p02_harness/trace.jsonl`](p02_harness/trace.jsonl)
- P02 smoke summary: [`p02_harness/smoke_summary.md`](p02_harness/smoke_summary.md)
- P02 validation report: [`test_report_2026-09-13_p02_harness.md`](test_report_2026-09-13_p02_harness.md)
- P03 cohort audit: [`p03_cohort_audit.md`](p03_cohort_audit.md)
- P03 audit report: [`test_report_2026-09-13_p03_cohort_audit.md`](test_report_2026-09-13_p03_cohort_audit.md)
- P03 source pin and runtime status: [`p03_source_pin.md`](p03_source_pin.md)
- P03 tool surface report: [`test_report_2026-09-13_p03_tool_surface.md`](test_report_2026-09-13_p03_tool_surface.md)
- P03 runtime readiness report: [`test_report_2026-09-13_p03_runtime_readiness.md`](test_report_2026-09-13_p03_runtime_readiness.md)
- P03 GPU image and verifier report: [`test_report_2026-09-15_p03_gpu_image_build.md`](test_report_2026-09-15_p03_gpu_image_build.md)
- Final W1 cohort manifest: [`rejoin_w1_candidate_manifest.jsonl`](rejoin_w1_candidate_manifest.jsonl)
- W1 cohort selection and runtime table: [`rejoin_w1_cohort_selection.md`](rejoin_w1_cohort_selection.md)
- Final build Dockerfiles: `/data/ycfeng/tmp/rejoin-p03-stepbps-dockerfiles/`
- Build metadata and registry digest snapshot: `/data/ycfeng/tmp/stepbps_*` and `/data/ycfeng/tmp/rejoin_p03_runtime_digests.json`
- Verifier logs and worker summaries: `/data/ycfeng/tmp/rejoin-verifier-logs/`
- Eight-tool implementation and direct tests: [`research/rejoin/src/rejoin/tools.py`](../../research/rejoin/src/rejoin/tools.py) and [`research/rejoin/tests/test_tools.py`](../../research/rejoin/tests/test_tools.py)
- Read-only document validation: [`test_report_2026-09-13_plan_document_validation.md`](test_report_2026-09-13_plan_document_validation.md)
- Planning skill index: [`task_plan.md`](../../task_2026-09-13_tvcache_rejoin_v3_planning/task_plan.md)

# Validation Status

PASS. The source file was confirmed at 1,310 lines. P00 recorded the CPU baseline, P01 recorded the strict `xfail` cursor reproducer, and P02 produced a three-event JSONL trace with reloadable records and workspace manifest digests. P03 pinned Terminal-Bench at `d28711d0da2675d0bb1d56de45ae5df6082438a3`, built all ten final images through StepBPS, captured ten private-registry `Docker-Content-Digest` values, and ran every solution plus verifier on an H200 worker. All ten jobs have solution and verifier exit code 0 and worker status `succeeded`; the four-task P04 smoke subset is ready. The seven S0 tools and mutating S1 `exec` direct tests also pass.

# Open Items / Future Extensions

P04 provider smoke is the next step. It still requires an authorized API endpoint and model profile, fixed sampling settings, a rollout artifact location, and confirmation that the four-task smoke gate is met. P05 opportunity analysis, two W2-T1 instances, and any TVCache serving work remain deferred until the later gates pass.

## 2026-09-15 cloud and P04 checkpoint

Cloud preservation is complete under `/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3`: 67 verified staged files, ten complete image manifests, 69 unique blobs totaling 1,452,034,837 bytes. Job `exp-0915-140553-008483` reported NVIDIA H200 and succeeded with personal auth and the current local NFS source. See `cloud_storage.md`, `cloud_evidence/`, and `test_report_2026-09-15_cloud_persistence.md`.

P04 implementation now includes `research/rejoin/scripts/collect_p04.py`, `tool_process.py`, and `check_p04.py`, plus the local launcher `tests/e2e/run_rejoin_p04.py` and isolation check `tests/e2e/check_rejoin_tool_process.py`. The provider is `deepseek-v4-flash` at `https://models-proxy.stepfun-inc.com`. The local isolation check, three existing tool tests, verifier-package imports, and live provider preflight passed.

The corrected first worker `exp-0915-141415-207218` is waiting for H200 quota. Its local launcher and automatic 15-rollout continuation remain alive. No completed P04 smoke is claimed. `p04_smoke.md` records the settings; `test_report_2026-09-15_p04_preparation.md` records commands and limits. Future work is to observe actual worker results, address any evidenced collection issue, read the generated smoke report, and enter P05 only when that gate passes.
