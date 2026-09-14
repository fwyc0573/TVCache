## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Added the planning index for the ReJoin v3 task. |
| 2026-09-13 | Updated the index to reflect execution through P02 and the P03 input audit. |
| 2026-09-15 | Recorded P03 runtime image builds, registry digests, verifier passes, and the four-task smoke readiness result. |

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
| P04–P08 | pending | Blocked by packet dependencies and M0/M1 gates |

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

Every execution packet records exact commands, environment, criteria, observed evidence, and unresolved issues in a dated test report. Temporary caches remain outside the repository. No real provider or serving execution starts before P03 inputs and the P04 smoke gate are ready.
