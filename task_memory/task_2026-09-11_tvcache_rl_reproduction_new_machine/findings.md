## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-11 | Recorded canonical inputs and missing local assets. |

# Findings

- Canonical recipe is `task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/h800_reproduction.md`.
- Fixed manifest is `task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/egoschema_manifest_2026-09-08.json`.
- This machine is `kun-workspace-vgen2`; GPU operations must use the local StepMind Python `RJobBackend` with `i-fengyicheng` personal auth, as required by `/data/ycfeng/stepfun-env-handbook/stepmind-python-rjob.md`.
- Required runtime, model, cache, inventory, and video paths are currently absent locally and present on `shai-ycfeng`; copying them is in scope under the user's request.
