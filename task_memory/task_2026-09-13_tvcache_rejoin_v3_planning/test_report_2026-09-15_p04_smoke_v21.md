## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Recorded direct verification for the completed P04 v21 smoke run. |

# P04 v21 smoke verification report

## Execution

The final run was `p04-20260915-v21`. It used the four fixed W1 smoke tasks (`wasm-pipeline`, `polyglot-c-py`, `multi-source-data-merger`, and `recover-accuracy-log`) with four fresh rollouts per task. The provider was `deepseek-v4-flash` at `https://models-proxy.stepfun-inc.com`, with native function calls, `thinking={"type":"disabled"}`, `parallel_tool_calls=false`, temperature `0.8`, top-p `0.95`, `max_tokens=4096`, `max_steps=96`, and the collector retry policy for transient HTTP 429 and 5xx responses.

The detached local controller was launched with the following reproducible command:

```bash
python3 /data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox/tests/e2e/run_rejoin_p04.py \
  --stage /data/ycfeng/tmp/rejoin-p04-control \
  --run-id p04-20260915-v21 \
  --concurrency 4
```

Each controller launch used the local mounted source `/data/ycfeng/tmp/rejoin-p04-control`. The StepMind Python `RJobBackend` jobs were created by personal creator `i-fengyicheng`, charged to `step_main`, and placed on H200 workers. A representative retained worker record reports local NFS source `100.96.128.194:/data/ycfeng/tmp/rejoin-p04-control`, worker status `succeeded`, and an H200 GPU.

The aggregate check was generated with:

```bash
python3 /data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox/research/rejoin/scripts/check_p04.py \
  --cloud-root /mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3 \
  --run-id p04-20260915-v21 \
  --report /data/ycfeng/tmp/rejoin-p04-control/p04-20260915-v21.smoke.json
```

The final local report is `/data/ycfeng/tmp/rejoin-p04-control/p04-20260915-v21.smoke.json`. The cloud report is `/mnt/codesign-exp/ycfeng/tvcache-rejoin/task_2026-09-13_v3/reports/p04-20260915-v21.smoke.json`; rollout traces, provider records, verifier files, and workspace archives are under the same cloud root's `rollouts/p04/p04-20260915-v21/` directory.

## Criteria

The check script monitored these six encoded smoke criteria:

1. All 16 completion records and traces reload, with complete verifier, log, and workspace archive files.
2. More than half of the rollouts have at least four tool calls.
3. Real workspace mutations occur.
4. Each task has at least two distinct tool-and-argument trajectories.
5. Both S0 and S1 tool support classes occur.
6. No rollout is marked `collection_error`.

The check is a collection gate. Verifier exit status is retained as task evidence and reported separately; the gate does not convert a model-produced verifier failure into a collection failure.

## Evidence

**PASS.** `check_p04.py` returned status `PASS` with all six checks true:

| Measure | Observed result |
| --- | ---: |
| Reloaded rollouts | 16/16 |
| Total tool calls | 412 |
| Rollouts with at least four calls | 16/16 |
| Rollouts with real mutations | 16/16 |
| Distinct trajectories | 4 for each of 4 tasks |
| Support classes | S0 and S1 |
| Collection errors | 0 |
| Verifier passes | 10/16 |
| Invalid or early termination | 1 (`polyglot-c-py/r1`, `step_limit`) |

Per-task verifier outcomes were `wasm-pipeline` 4/4, `polyglot-c-py` 2/4, `multi-source-data-merger` 4/4, and `recover-accuracy-log` 0/4. The four `recover-accuracy-log` rollouts all produced complete artifacts and real mutations, but the unchanged upstream verifier exited 1 in each case. This is recorded as a task-level data-quality limitation for P05. It is not evidence of a provider transport, collector, image, GPU, or cloud persistence failure.

The v20 transient HTTP 503 issue is closed for this run: v21 recorded zero collection errors after `collect_p04.py` retried transient 429 and 5xx responses. The v18 long native-action truncation is also closed for collection: the 4096-token request budget produced valid traces for the v21 run.

## Practical limit

This report establishes collection integrity and tool-surface coverage for the fixed smoke cohort. It does not estimate uncontended throughput, prove deterministic replay, or establish cache reuse benefit. Those questions belong to P05 and must account for the `recover-accuracy-log` verifier limitation.
