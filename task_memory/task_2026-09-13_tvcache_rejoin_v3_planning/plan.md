## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Landed the v3 execution plan as ordered packets with gates, artifacts, and verification rules. |
| 2026-09-15 | Closed P03 after GPU-worker image builds, registry digest capture, verifier execution, and tool-surface checks. |
| 2026-09-15 | Recorded P04 collection preparation, cloud persistence, and current execution evidence. |
| 2026-09-15 | Closed P04 v21 smoke and started P05 opportunity-pilot preparation. |
| 2026-09-15 | Completed P05 merged opportunity analysis; P06 is ready for a typed U-family redirect decision. |
| 2026-09-15 | Synchronized the packet status indexes after the P05 merge and push. |

# ReJoin v3 Execution Plan

## Current status

The user has authorized execution. P00, P01, P02, P03, P04, and P05 are complete; P06 is pending as the sampling-adequacy and typed U-family route decision. The source of truth remains `draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md`, originally pinned at `43cf9d6a779eb5149e0fae50b9a3a891dcbaed6f`; the current checkout includes the execution evidence commits.

## Execution status

| Packet | Status | Evidence |
|---|---|---|
| P00 baseline capture | complete | `p00_baseline/baseline.md`, `environment.md`, and raw pytest logs. |
| P01 cursor issue lock | complete | B01 strict `xfail`, forced failure evidence, and `issues.md`; commits `cce8520`, `30ff78f`. |
| P02 minimal research harness | complete | `research/rejoin/` package, direct execution support, JSONL trace, manifest analysis, and smoke evidence are complete. |
| P03 cohort/tool surface | complete | Ten W1 images were built through StepBPS, registry digests were captured, all ten verifiers passed on H200, and the eight-tool surface passed direct checks. |
| P04 API rollout collector | complete | `p04-20260915-v21`: 16/16 traces reload, 412 calls, zero collection errors, smoke gate PASS. |
| P05 opportunity pilot | complete | Merged v2/v3 collection: 40/40 reload, 667 calls, 0 collection errors; A/B/C/U/N report and O1–O3 figures are in cloud `reports/p05/p05-20260915-v2/`. |
| P06 decision | pending | Depends on P05 analysis. |

## Dependency map

`source analysis -> P00 baseline -> P01 issue lock`

`P02 harness -> {P03 cohort/tool surface, P04 collector} -> P05 pilot -> P06 decision`

`P06 positive or redirected -> P07 memoizer -> P08 Phase-2 decision`

P03 must finish before the collector can execute real tools. P04 can prepare its provider loop in parallel with P03 after P02. P05 needs both. P07 is allowed only after P06 says C is meaningful or selects a typed operation family from U.

## Packets

### P00 — Baseline capture

**Purpose:** record the checkout and environment before research work.

**Work:** verify commit and branch; run the existing CPU unit/integration suite; save raw output; classify known failures; cite the archived provider-backed video E2E record; create the task directory.

**Deliverables:** `baseline.md`, `pytest.log`, `issues.md`, and an environment record with Python/uv/cache paths.

**Acceptance:** the baseline states observed pass/fail counts and known red items. It does not claim a green suite or repair video/Tinker issues.

### P01 — Lock the known cursor issue

**Purpose:** preserve the B01 correctness blocker without pulling it into Phase 1.

**Work:** add one minimal failing or strict `xfail` reproducer with a mutating, read-only, mutating, and prefix-restore sequence. Record why filtered-prefix length and original command position differ.

**Deliverable:** one regression test plus an issue note. Do not fix the executor or add the full B02–B05 set at this stage.

**Acceptance:** the reproducer demonstrates the mismatch and is tied to the P00 baseline. If the existing review already supplies the evidence, future execution may use that record instead of repeating broad investigation.

### P02 — Minimal research harness

**Purpose:** make one scripted rollout traceable with the smallest durable package.

**Planned layout:**

```text
research/rejoin/
  pyproject.toml
  src/rejoin/{schemas.py, trace.py, workspace.py, tools.py, provider.py}
  scripts/{collect.py, analyze.py}
```

**Acceptance:** a scripted rollout writes JSONL, the JSONL reloads, and before/after workspace manifests are computed. Do not add a large CLI or Phase 2 state types.

### P03 — Pilot cohort and tool surface

**Purpose:** freeze the input list for M0-PILOT without freezing a later holdout.

**Work:** choose 8–12 W1 tasks; record task ID, source revision, image digest, include/exclude reason, verifier, and task root. Implement seven S0 tools plus mutating S1 `exec`.

**Acceptance:** each tool declares its mutation behavior; S0 facts are serializable; S1 has no dependency classifier; task selection is reviewable.

**Current execution:** the ten-task manifest and four-task smoke subset are recorded in `rejoin_w1_candidate_manifest.jsonl` and `rejoin_w1_cohort_selection.md`. The source checkout is pinned in `p03_source_pin.md`. StepBPS built all ten final images, the private registry returned a `Docker-Content-Digest` for each tag, and each image passed its in-container `solution.sh` plus `run-tests.sh` check on an H200 worker. The eight-tool surface is implemented under `research/rejoin/src/rejoin/tools.py` and covered by direct tests. P03 is complete; P04 may begin with the four-task smoke rollout.

### P04 — API rollout collector

**Purpose:** run the same policy/tool surface across four rollouts per task while recording every call.

**Work:** adapt the existing provider client pattern; keep endpoint/model/sampling configurable; execute all tools for real; record model request/return identity, provider profile, temperature/top-p/seed support, verifier outcome, invalid termination, timings, and trace events.

**Smoke first:** 4 tasks × 4 rollouts.

**Smoke gate:** most rollouts have at least four calls, real workspace mutations occur, same-task trajectories diverge, S0 and S1 are both naturally used, and analysis can reload all traces. If the gate fails, change the cohort or policy and record the reason; do not build cache logic to force a pass.

### P05 — Opportunity pilot

**Purpose:** produce the first opportunity evidence.

**Work:** run 8–12 tasks × 4 rollouts; preserve raw JSONL and collection concurrency; analyze A/B/C/U/N; apply the post-divergence filter; produce hindsight and completed-donor views; re-run only small serial references for the top ten repeated expensive signatures.

**Deliverables:** `opportunity_pilot.md`, per-task tables, and three figures: class time share, opportunity by divergent-mutation depth, and top-signature concentration.

**Report questions:**

1. How many calls and how much time belong to A?
2. How many calls and how much time belong to B?
3. How many calls and how much time belong to post-divergence C?
4. How many calls and how much time belong to U?
5. What share of real tool time is C+U?
6. Is C/U opportunity concentrated in one or two signatures?
7. At what trajectory and prior-mutation depth does it appear?
8. Does expensive repeated work mainly occur in S0 or raw S1?

### P06 — Decision point

**Go signal:** roughly `C+U >= 10%` of observed tool time, post-divergence evidence in at least three tasks, and top-1 signature below roughly 60%. These are soft continuation rules, not statistical claims.

**Cases:**

| Result | Next action |
|---|---|
| C is meaningful | Start P07 on W2-T1. |
| U is large and C is small | Select one high-value U family and design one typed adapter before P07. |
| C+U is weak | Stop or redirect ReJoin; record workload and evidence reasons. |

**Deliverable:** `decision.md` with data, class definitions, and the selected case.

### P07 — Minimal guarded memoizer probe

**Purpose:** prove or reject mechanism feasibility without TVCache integration.

**Work:** implement record, lookup, guard, and apply for two W2-T1 instances. Keep unrelated recipient mutation. For each hit, run paired fresh execution and compare observation, manifest, output files, and verifier. Record real and reuse timing components.

**Acceptance:** at least one supported C scenario has exact differential equivalence, recipient state is preserved, unsupported effects miss visibly, and timing evidence is present. No random-scale, fault, crash, or distributed tests are required.

### P08 — Phase-2 design decision

**Purpose:** decide whether implementation work is justified.

**Required answers:** is the opportunity real; which operation family is valuable; where generic memoizer time is spent; whether lineage would reduce a measured cost; and whether TVCache integration should begin.

**Deliverable:** a new Phase-2 design record. Only then may M1.1–M1.4 start.

## Milestones

### M0 — Opportunity signal

P00–P06 must deliver real rollout traces, A/B/C/U/N breakdown, post-divergence and online views, expensive signatures, and a data-backed Go/Redirect/Stop choice.

### M1 — Mechanism feasibility

P07–P08 must deliver one supported C reuse, recipient-state-preserving effects, fresh-versus-reuse differential equality, timing components, and an integration choice. A negative result closes this research path for the current scope.

## Phase 2 entry only after M1

The later implementation order is: fix only serving baseline issues needed for measurement (including B01 and any confirmed B02–B05 blockers); add a narrow hook before real environment execution; type only operation families exposed by the pilot; then compare generic validation cost before designing lineage or versioned state.

## Later throughput comparison

If M1 remains positive, a later experiment may compare four fixed configurations: no cache, corrected TVCache, TVCache plus the generic guarded memoizer, and the final ReJoin mechanism. It must keep model, task set, CPU/GPU budget, tool surface, and concurrency sweep fixed, and report completed rollouts per second, avoided executions, CPU use, sandbox count, p50/p95 rollout latency, and verifier success. This comparison is recorded here for continuity and is not part of the current planning task.

## Execution style

Keep early work with one coordinator and one implementation/experiment worker. A temporary review worker is optional when a packet needs an independent code check. Every worker reads the task records first, edits only its packet files, keeps raw outputs, marks unsupported behavior visibly, and appends change, reason, command, result, and next decision to `progress.md`.

## Deferred work

Until M0/M1 data supports it, do not add server endpoints, distributed cache, reflink or overlay snapshots, lineage engine, lazy materialization, shell dependency tracing, single-flight, cross-task or cross-tenant reuse, local GPU serving, training/RL, frozen holdout statistics, SQL, extra W2 templates, large randomized differential suites, fault injection, crash recovery, or publication-scale failure handling.

## Verification and records

Every packet must append to `progress.md` with change, reason, command, observed result, and next decision. Raw logs stay under the packet output directory. Each future test run writes `test_report_YYYY-MM-DD_<brief_description>.md` with exact command, environment, criteria, evidence, and errors. This planning task itself uses read-only source checks only and must not report future measurements as facts.

## Open decisions for execution time

1. Provider selected: `https://models-proxy.stepfun-inc.com`, `deepseek-v4-flash`; smoke results will decide P04 acceptance.
2. W1 input settled: ten tasks and verified image digests are recorded in the candidate manifest.
3. Which two concrete W2-T1 instances provide real compute and explicit effects?
4. Storage settled: durable source, image, and rollout data use the personal cloud task directory in `cloud_storage.md`; caches use worker temporary storage.
5. Does P00 need a fresh CPU run or can the prior reviewed baseline be cited for a given packet? The executing agent must decide from current checkout state and record the choice.
