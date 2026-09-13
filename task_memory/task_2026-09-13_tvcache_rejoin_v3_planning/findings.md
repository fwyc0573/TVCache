## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded initial source-location and scope findings while starting the v3 plan analysis. |
| 2026-09-13 | Completed the v3 source extraction: research questions, workloads, evidence classes, milestones, packets, gates, and deferred work. |

# Findings

## Source and Repository

- Requested source exists at `draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md` in this worktree.
- `draft-plan/legacy/AGENTS.md` says the legacy directory is reference-only; legacy documents are not the planning source.
- The source plan pins repository branch `tvcache-rl-reproduction-docs` and commit `43cf9d6a779eb5149e0fae50b9a3a891dcbaed6f`.
- The source plan is an early-stage research plan, not a production implementation plan.

## Initial Scope Interpretation

- Core questions are (1) whether post-divergence rollouts contain expensive reusable tool work and (2) whether a minimal guarded memoizer can safely reuse observation plus effects at lower cost than execution.
- The plan explicitly postpones lineage-aware serving, lazy materialization, full snapshots, distributed cache, full CLI, fault injection, paper-scale statistics, GPU, model serving, and TVCache serving-path changes.
- Phase 1 is observation-only: all tools execute for real, traces are collected, and an offline prefix oracle estimates existing TVCache reuse.
- Phase 2 uses one controlled multi-artifact workflow and a small guarded memoizer proof.

## Source-to-Plan Analysis

### Research question and story

The plan tests a stronger reuse claim than stateful prefix reuse: after two rollouts have different histories and full workspace states, a later tool call may still have equal local inputs and safely reusable observation/effects. The minimum story has four claims: prefix/history matching is coarser than true tool dependencies; real rollouts contain post-divergence redundant work; explicit local guards can identify some safe cases; and reuse must apply local effects to the recipient state rather than return stdout alone or replace the recipient workspace.

### Phase separation

- Phase 1 is observation-only. Every tool runs for real, trace events are written, and an offline prefix oracle estimates existing TVCache reuse. It does not call the TVCache executor, server, fork, snapshot, lineage, effect transaction, GPU, or local model serving.
- Phase 2 begins only after a positive opportunity signal and then a positive mechanism probe. It may fix only serving issues needed by the baseline, add a narrow executor hook, add typed adapters for high-value operation families, and measure whether lineage is worth its cost.
- Throughput, holdout statistics, broader workloads, and full system integration remain later work.

### Workloads

- W1 is the opportunity workload: 8–12 Terminal/coding-agent filesystem tasks, 4 rollouts per task, with a seven-tool S0 surface (`read_file`, `write_file`, `list_dir`, `grep`, `stat`, `mkdir`, `remove`) plus mutating S1 `exec`. No task-specific expensive tools are predeclared.
- W2-MVP is the mechanism workload: two deterministic `build_index(input, config -> output)` instances with explicit read set, write/effect set, real computation, and unrelated recipient mutation preserved. Suggested real execution time is 0.2–3 s. SQL, additional W2 templates, and randomized counterexamples are deferred.

### Evidence classification

Each tool invocation receives exactly one class:

- A: current TVCache prefix/history reusable; excluded from new ReJoin opportunity.
- B: different history but equal full workspace manifest; useful to a full-state cache, not the core claim.
- C: post-divergence supported local equivalence for an S0 invocation with equal identity, explicit facts, applicable effects, and different unrelated state; the main safe new opportunity.
- U: repeated normalized S1 invocation without a read/effect contract; valuable potential opportunity but not a safe hit.
- N: no donor.

The core post-divergence filter requires donor and recipient to have at least one different mutation before the candidate invocation. Analysis must report both hindsight upper bound and completed-donor online availability, using event time to avoid future-data hits.

### Trace and state records

Phase 1 uses only `TaskSpec` and `TraceEvent`. Trace fields include run/task/rollout identity, sequence, normalized arguments, S0/S1 support, declared mutation, cwd, start/end time, exit status, result digest, before/after workspace digests, changed paths, and optional typed S0 facts. Workspace state is a task-root manifest of relative path, type, size, and SHA-256; unsupported objects become unsupported evidence. `.git`, package caches, compiler caches, and oversized files are excluded or explicitly marked, and manifest time is measured.

### Policy and experiments

Use one authorized API model with stable structured output/tool calling. Record requested/returned model IDs, sampling settings, seed support, provider, and base URL profile. Do not add automatic fallback. M0-SMOKE is 4 tasks × 4 rollouts and must establish at least four calls per rollout, real mutation, trajectory divergence, natural S0/S1 use, and replayable traces. M0-PILOT is 8–12 tasks × 4 rollouts; holdout is not frozen.

### Cost and report gates

Pilot weights each call by observed `end_ns - start_ns`, records collection concurrency, and serially rechecks only the top ten repeated expensive signatures. The report must answer eight questions: A/B/C/U counts; C+U time share; concentration; trajectory/mutation depth; and S0 versus raw S1 location. The soft go signal is approximately `C+U >= 10%` of weighted tool time, post-divergence evidence in at least three tasks, and top-1 signature below roughly 60%. These are continuation heuristics, not statistical tests, and class definitions cannot be changed to pass them.

### Minimal mechanism probe

After a go signal, an in-memory memoizer implements `record`, `lookup`, guard validation, and local effect application only for W2-T1. A hit returns cached observation and applies effects to the recipient workspace; it never replaces the recipient with donor state. Preconditions include input/config existence and digest, implementation/runtime identity, and output parent existence. Unsupported side effects miss. Every hit is paired with fresh execution and compared on observation, manifest, output files, and verifier result. Measure `T_real`, `T_lookup`, `T_guard`, `T_apply`, and the ratio `(lookup + guard + apply) / real` without pre-filling a paper threshold.

### Execution packets and milestones

The source defines packets P00–P08: baseline capture; a minimal known cursor regression reproducer; minimal research harness; task cohort/tool surface; API rollout collector; opportunity pilot; data-driven decision; minimal memoizer; and Phase-2 design decision. M0 is P00–P06 and must deliver traces, A/B/C/U/N, post-divergence and online views, expensive signatures, and Go/Redirect/Stop. M1 is P07–P08 and must deliver one safe C reuse, recipient-preserving effects, differential equivalence, overhead, and an integration decision.

### Explicitly deferred work

Before M0/M1 the plan prohibits new TVCache endpoints, distributed cache, reflink/overlay snapshots, lineage engine, lazy materialization, dependency tracing with strace/ptrace, single-flight, cross-task/tenant reuse, local GPU model serving, training/RL, full holdout bootstrap statistics, SQL, W2-T2–T6, 1000+ randomized differential tests, fault injection, crash consistency, and publication-grade recovery.

### Success definition

The early-stage result is a data-backed answer to four questions: whether post-divergence opportunity exists beyond prefix reuse, whether it is in typed S0 or raw S1, whether local guards/effects are safe for a supported operation, and whether reuse overhead is clearly below real expensive execution. A negative result is a valid stop signal.

## Source gaps to check against code

- The plan names `ProviderChatClient`, `AsyncSemanticStatefulExecutor._execute_commands()`, and the B01 cursor issue as later implementation anchors; their current symbols and tests need read-only verification before implementation packets are scheduled.
- P02's proposed `research/rejoin/` layout, provider availability, benchmark task source, and image digests are planning assumptions, not current artifacts.
- P00 asks to record archived provider-backed video E2E facts; this task only records the requirement and does not re-run or certify those results.
