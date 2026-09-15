## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Started P05 opportunity-pilot preparation after the P04 v21 smoke gate passed. |

# P05 Opportunity Pilot

## Goal

Measure repeated tool work across the ten verified W1 tasks and decide whether the evidence supports a guarded ReJoin mechanism study. P05 is an observation and analysis stage. It does not add cache behavior to TVCache.

## Collection

- Cohort: the ten included rows in `rejoin_w1_candidate_manifest.jsonl` at source revision `d28711d0da2675d0bb1d56de45ae5df6082438a3`.
- Rollouts: four independent provider trajectories per task, 40 total.
- Provider: `https://models-proxy.stepfun-inc.com`, model `deepseek-v4-flash`, native tools, `max_tokens=4096`, `max_steps=96`, `parallel_tool_calls=false`.
- Resource route: local StepMind Python `RJobBackend`, `H200`, `step_main`, local source mount, personal creator `i-fengyicheng`.
- Cloud layout:

  ```text
  /mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3/
    rollouts/p05/<run-id>/<task-id>/<rollout-id>/
    reports/p05/<run-id>/
    code/p05/<run-id>/
  ```

- Collection concurrency is recorded in the run command and report. Worker temporary files stay under `/data/ycfeng/tmp`; trace, workspace archive, verifier artifacts, and reports are written to the cloud root.

## Class rules

Each event is matched only with events from another rollout of the same task and the same tool plus normalized arguments.

- **A:** same invocation prefix and same workspace-before digest. This is existing stateful prefix/history reuse and is reported separately.
- **B:** different invocation history but same workspace-before digest and same observed result/effect. This is a full-state opportunity and is not the main post-divergence claim.
- **C:** S0 invocation after both donor and recipient have different prior mutations, with the same observed result/effect and a remaining recipient state difference. This is the primary safe opportunity candidate.
- **U:** repeated S1 invocation after prior divergence without a complete dependency and effect description. It is a potential opportunity only.
- **N:** no matching donor satisfies the applicable rule.

The analyzer produces two views. Hindsight permits any donor in the completed batch. The completed-donor online view keeps only donors whose event end time precedes the recipient event start time. A post-divergence match requires non-empty and different prior mutation histories on donor and recipient.

## Analysis and evidence

The event cost is `end_ns - start_ns`. The analyzer writes:

- `opportunity_pilot.md` and `opportunity_pilot.json`;
- per-task call/time/verifier tables;
- Figure O1, class time share;
- Figure O2, C/U opportunity by prior mutation depth;
- Figure O3, repeated signature concentration;
- a list of the ten most expensive repeated signatures and small serial reference rerun results.

The P06 continuation heuristic is recorded without changing class rules: C+U around 10% of observed tool time, post-divergence evidence in at least three tasks, and top-1 signature below around 60%.

## Acceptance checks

1. 40/40 rollout records, traces, provider metadata, workspace manifests, archives, and verifier artifacts reload.
2. Collection errors are zero or are reported with their exact task and rollout; no silent retry or record removal is allowed.
3. A/B/C/U/N class counts and time totals sum to all observed tool calls and time in each view.
4. Hindsight and completed-donor online views are both present.
5. Top repeated signatures are explicit, and serial reference attempts are limited to ten.
6. The report answers all eight P05 questions and states what the data cannot establish.

## Current status

The phase-aware collector, ten-task runner, P05 aggregate checker, and analyzer pass local syntax checks and a 40-config prepare-only run. The first launcher attempt (`p05-20260915-v1`) exposed a missing copied `verifier_packages` directory and is retained as staging evidence. The main `p05-20260915-v2` collection produced all 40 records but five records had provider collection errors: four HTTP 413 responses and one multiple-native-call response. A configurable 12,000-character provider context bound closed the 413 case. Fresh `p05-20260915-v3` retries for those five records succeeded. The final report uses an explicit run map so each of the 40 analyzed records points to its successful v2 or v3 cloud directory.

## Final result

The merged checker passed for all 40 rollouts and 667 tool calls. The full report and figures are stored at:

```text
/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3/reports/p05/p05-20260915-v2/
```

| Class | Calls | Time (s) | Hindsight time share |
|---|---:|---:|---:|
| A | 65 | 0.174 | 0.26% |
| B | 38 | 2.295 | 3.43% |
| C | 45 | 0.008 | 0.01% |
| U | 57 | 2.398 | 3.59% |
| N | 462 | 61.957 | 92.71% |

The completed-donor online view gives C+U time share of 1.81%, compared with 3.60% hindsight. Eight of ten tasks contain post-divergence C or U events. The most common prior mutation depth is 2. Task-scoped top-1 repeated signature share is 7.95%. Opportunity time is almost entirely raw S1 `exec`; observed C time is negligible.

The P06 continuation signal is therefore a redirect. The generic C memoizer threshold is not met. The highest-value follow-up is one typed adapter study for the repeated `multi-source-data-merger` S1 `exec` family, which contributes 1.650 s of U time. This result does not establish safe reuse for that family; it selects the next measurement target.
