## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Recorded merged P05 collection validation, opportunity analysis, figures, and continuation evidence. |

# P05 opportunity analysis verification

## Execution

- Collection launcher: `/data/ycfeng/tmp/rejoin-p05-control-v2`, run `p05-20260915-v2`, local StepMind Python `RJobBackend`, H200, `step_main`, concurrency 4.
- Retry launcher: `/data/ycfeng/tmp/rejoin-p05-control-v3`, run `p05-20260915-v3`, five targeted rollouts after the v2 provider errors.
- Merged checker and first analyzer RJob: `exp-0915-222550-684805`.
- Task-scoped signature correction and final analyzer RJob: `exp-0915-223247-819216`.
- Report fetch RJob: `exp-0915-223748-753773`.
- Cloud report directory:

  ```text
  /mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3/reports/p05/p05-20260915-v2/
  ```

- Final local copies: `/data/ycfeng/tmp/rejoin-p05-control-v3/result-v2/`.

## Criteria

1. Reload exactly ten tasks × four rollouts using a successful v2/v3 run map.
2. Preserve and verify trace, provider metadata, workspace archive, manifests, verifier logs, and XML for every rollout.
3. Classify all calls as A/B/C/U/N and make class time totals sum to all observed tool time.
4. Produce hindsight and completed-donor online views.
5. Report post-divergence depth, per-task results, support class, top ten repeated signatures, and serial references.
6. Apply the recorded soft continuation heuristic without changing class definitions.

## Evidence

| Check | Result | Evidence |
|---|---|---|
| Merged artifact checker | PASS | `p05-merged.aggregate.json`: `all_40_reload=true`, `no_collection_errors=true`, `each_task_has_divergence=true`, `both_support_classes=true`, 667 calls. |
| Hindsight totals | PASS | A 65/0.174 s; B 38/2.295 s; C 45/0.008 s; U 57/2.398 s; N 462/61.957 s. Totals cover all 667 calls and 66.831 s. |
| Online donor view | PASS | Completed-donor C+U time share 1.81%; donor end time was required to precede recipient start. |
| Opportunity spread | PASS | 8/10 tasks have post-divergence C or U; modal prior mutation depth is 2. |
| Concentration | PASS | Task-scoped top-1 repeated signature is 7.95%; top ten are recorded in JSON and Figure O3. |
| Serial references | PASS | Ten top repeated expensive signatures attempted; all ten completed with status `pass` and ratios recorded. |
| Figures | PASS | O1 class share, O2 mutation depth, and O3 signature concentration are valid SVG artifacts. |

## Interpretation

- Hindsight C+U time share is 3.60%; completed-donor online C+U is 1.81%.
- C time is 0.01% and U time is 3.59%, so the evidence does not support a generic safe C memoizer at the P06 soft threshold.
- The next measurement target is a typed adapter for the repeated `multi-source-data-merger` S1 `exec` family, which contributes 1.650 s of U time. This is a redirect target, not a safety proof.

## Limits

The collection uses one ten-task cohort and four trajectories per task. Verifier exits were 0 for 10/40, while all 40 records and artifacts passed reload checks; verifier success is not used as a filter for opportunity classification. C is an observed S0 effect match and still needs paired differential validation. U has no complete dependency/effect description and must not be treated as a cache hit.
