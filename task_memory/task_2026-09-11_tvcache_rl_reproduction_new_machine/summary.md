## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-11 | Archived the completed new-machine TVCache rollout reproduction. |
| 2026-09-12 | Reviewed and enhanced evidence links and completion details. |

# Task Overview

Reproduced the canonical EgoSchema VideoAgent TVCache E2E workflow on `kun-workspace-vgen2` using a local personal-authenticated StepMind RJobBackend H800 worker.

# Deliverables Inventory

- [submit_tvcache_reproduction_rjob.py](/data/ycfeng/step-sandbox/TVCache/.worktrees/tvcache-rl-reproduction/tests/e2e/submit_tvcache_reproduction_rjob.py)
- [run_real_video_rollouts_h800.sh](/data/ycfeng/step-sandbox/TVCache/.worktrees/tvcache-rl-reproduction/tests/e2e/run_real_video_rollouts_h800.sh)
- E2E outputs: [tool smoke JSON](/data/ycfeng/step-sandbox/TVCache/.worktrees/tvcache-rl-reproduction/task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/exp-0911-180851-903367-tool-smoke.json) and [rollout directory](/data/ycfeng/step-sandbox/TVCache/.worktrees/tvcache-rl-reproduction/task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/exp-0911-180851-903367-rollouts)
- Validation report: [test_report_2026-09-11_new_machine_e2e.md](/data/ycfeng/step-sandbox/TVCache/.worktrees/tvcache-rl-reproduction/task_memory/task_2026-09-11_tvcache_rl_reproduction_new_machine/test_report_2026-09-11_new_machine_e2e.md)
- Worker logs and GPU evidence: `/data/ycfeng/tmp/exp-0911-180851-903367/`

# Validation Status

RJob `exp-0911-180851-903367` succeeded on H800 node `gpu-h800-0443` under personal creator `i-fengyicheng`. Four rollouts completed with reward 1.0 and final answer index 1. TVCache recorded six exact hits and twenty prefix hits across the two TVCache variants; no sandbox remained active. The worker retained `gpu-memory.csv`, service logs, provider JSONL traces, tool smoke output, per-rollout JSON records, and `summary.json`.

# Open Items/Future Extensions

None for the requested reproduction.
