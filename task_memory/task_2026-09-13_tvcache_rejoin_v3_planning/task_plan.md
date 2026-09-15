## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Added the planning index for the ReJoin v3 task. |
| 2026-09-13 | Updated the index to reflect execution through P02 and the P03 input audit. |
| 2026-09-15 | Recorded P03 runtime image builds, registry digests, verifier passes, and the four-task smoke readiness result. |
| 2026-09-15 | Recorded P04 collection preparation, cloud persistence, and current execution evidence. |
| 2026-09-15 | Recorded P05 completion and the P06 typed U-family redirect. |

# Task Plan Index

## Goal

Translate `draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md` into durable task records and execute the early research packets with auditable evidence. Enter provider, GPU, or TVCache serving work only after the documented gates pass.

## Current state

| Packet | Status | Record |
|---|---|---|
| P00 CPU baseline | complete | `p00_baseline/` and `test_report_2026-09-13_p00_cpu_baseline.md` |
| P01 B01 cursor reproducer | complete | `issues.md` and `test_report_2026-09-13_b01_cursor_reproducer.md` |
| P02 research harness | complete | `p02_harness/` and `test_report_2026-09-13_p02_harness.md` |
| P03 cohort/tool surface | complete | `rejoin_w1_candidate_manifest.jsonl`, `p03_source_pin.md`, `test_report_2026-09-15_p03_gpu_image_build.md`, and the eight-tool implementation |
| Cloud persistence | complete | `cloud_storage.md` and `test_report_2026-09-15_cloud_persistence.md` |
| P04 | complete | `p04_smoke.md` and `test_report_2026-09-15_p04_smoke_v21.md` |
| P05 | complete | `p05_opportunity_pilot.md`, merged opportunity report, and `test_report_2026-09-15_p05_opportunity.md` |
| P06–P08 | pending | Packet dependencies and M0/M1 gates |

## Dependency map

`source analysis -> P00 -> P01 -> P02 -> {P03, P04 preparation} -> P05 -> P06`

`P06 positive or redirected -> P07 -> P08`

## Records

- `requirements.md`: original request and explicit decisions.
- `findings.md`: source analysis and repository findings.
- `design.md`: research data flow and evidence model.
- `plan.md`: ordered packets, gates, dependencies, and deferred work.
- `progress.md`: commands, observed results, and decisions.
- `summary.md`: English archive and deliverable inventory.
- `rejoin_w1_cohort_selection.md` and `rejoin_w1_candidate_manifest.jsonl`: selected W1 tasks, build identities, runtime digests, and verifier evidence.

## Verification rule

Every execution packet records exact commands, environment, criteria, observed evidence, and unresolved issues in a dated test report. Temporary caches remain outside the repository. Real provider collection requires P03 inputs. P05 requires a passed P04 smoke; serving work requires the later M0/M1 decisions.
