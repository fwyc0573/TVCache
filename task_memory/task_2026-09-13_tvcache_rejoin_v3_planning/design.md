## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the interpreted research design and evidence flow from the v3 source plan. |
| 2026-09-15 | Added the P03 runtime evidence path and kept the design aligned with the completed harness and tool surface. |

# Design Record

## Purpose

This record turns the v3 document into a small research design that can be executed without silently expanding the scope. P00–P03 execution artifacts now exist; the design still does not claim provider opportunity measurements or TVCache serving results before P04–P06 evidence is collected.

## Core idea

The experiment separates two questions:

1. **Opportunity:** after two agent rollouts have different histories and workspace states, does a later tool call still repeat expensive work whose local inputs match?
2. **Mechanism:** for one explicitly supported operation, can a small guard validate the recipient state and replay observation plus effects faster than real execution while preserving recipient state?

Existing stateful prefix reuse is measured as class A and removed from the new-opportunity numerator. The new claim is about local equality after a prior mutation difference, not about merely different text histories.

## Data flow

```text
API agent policy
    -> research tool surface
    -> real tool execution
    -> TraceEvent JSONL + before/after workspace manifests
    -> offline opportunity analyzer
    -> A/B/C/U/N report and Go/Redirect/Stop decision
```

The Phase 1 analyzer reads finished traces. It does not call the TVCache server or executor during collection. A prefix oracle can inspect serialized calls after collection to estimate class A. This keeps serving defects out of the first opportunity measurement.

## Evidence model

| Class | Meaning | Use in decision |
|---|---|---|
| A | Existing TVCache stateful-history reuse | Report separately; exclude from new ReJoin opportunity. |
| B | Different history but equal full workspace manifest | Report as full-state-cache opportunity; not the main claim. |
| C | Supported S0 call with equal local facts and applicable effects after prior divergent mutations | Primary safe additional opportunity. |
| U | Repeated S1 call with no complete dependency/effect description | Potential opportunity only; never call it a safe hit. |
| N | No suitable donor | Denominator and negative evidence. |

The analyzer must report one class per call, post-divergence results, hindsight totals, and the online view in which a donor must finish before recipient lookup. Time weighting uses observed call duration and records collection concurrency.

## Workload design

### W1 opportunity workload

Select 8–12 filesystem-heavy Terminal/coding-agent tasks with a verifier, multiple tool turns, and real file changes. The pilot exposes seven general S0 operations and one S1 `exec`. S0 facts are explicit and declarative. S1 is always marked as mutating; no shell classifier is introduced. Task-specific expensive S0 operations are discovered from the pilot and can be admitted only in a later phase.

### W2 mechanism workload

Create two deterministic `build_index(input, config -> output)` instances. Each instance must declare read inputs, output/effect files, implementation/runtime identity, and unsupported side effects. The recipient performs an unrelated source mutation that remains present after reuse. The operation must do real work and run for roughly 0.2–3 s so the cost comparison is visible.

## Phase 1 records

`TaskSpec` contains task ID, source, image digest, instruction, and verifier. Each `TraceEvent` contains run/task/rollout IDs, sequence, tool name, normalized arguments, S0/S1 support, declared mutation, cwd, timing, exit status, result digest, before/after manifest digests, changed paths, and optional S0 facts.

The manifest covers relative path, file type, size, and SHA-256 within the task root. `.git`, package caches, compiler caches, unsupported external state, and over-size files are skipped with explicit records. Manifest time is itself measured so observation cost is visible.

## Phase 2 mechanism record

The in-memory memoizer stores:

```text
tool identity
arguments
preconditions
observation
effects
```

Lookup validates input/config existence and digests, implementation/runtime identity, and output-parent existence. A hit returns stdout/stderr/exit status and applies only listed output effects to the recipient. A hit never copies the donor workspace. Unsupported effects produce a miss.

Each hit has a paired fresh execution from the same recipient state. The comparison covers observation, full manifest, explicit output files, and verifier result. Timing records `T_real`, `T_lookup`, `T_guard`, and `T_apply`; the reported ratio is `(T_lookup + T_guard + T_apply) / T_real`.

## Repository fit

- Existing prefix semantics are implemented in `AsyncSemanticStatefulExecutor._get_serialized_stateful_chain()` at lines 234–243: non-mutating calls before the final call are omitted, and the final call is retained.
- Actual execution occurs in `_execute_commands()` at lines 308–341, where the environment is called and duration is measured. The later TVCache integration hook belongs immediately before the real `env.execute()` call, after the Phase 1 work has produced evidence.
- `ProviderChatClient` in `train/utils/provider_chat_client.py` provides the API request pattern and strict response checks. The new collector should reuse its ideas without assuming its current default model, endpoint, sampling support, or message format is sufficient.
- Existing tests cover provider response validation and prefix reuse, but the prior review records a known B01 cursor mismatch when a filtered prefix length is used as an index into the original command list. P01 records this issue without fixing it; Phase 1 does not depend on that executor path.

## Safety rules

- Every unsupported state or side effect is visible and becomes U/miss.
- No result may be called a measured value before the corresponding run artifact exists.
- No automatic model fallback is added; any provider change is recorded in a decision log.
- No holdout or publication-level statistics are built before M0 and the mechanism probe give a positive signal.
- Negative opportunity or unsafe differential results stop or redirect the next phase.
