## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-11 | Created the new-machine reproduction plan. |

# Plan

1. Inspect source task records, current machine, remote assets, and personal RJobBackend readiness. (`inspect -> asset inventory`)
2. Copy only missing required assets from `shai-ycfeng` to local persistent paths and verify sizes/checksums. (`asset inventory -> cache/runtime verification`)
3. Verify the local source and worker launcher inputs, including the fixed manifest, secret presence without disclosure, and GPU capacity. (`worker readiness -> submission`)
4. Submit one fresh two-GPU H800 worker through local StepMind Python `RJobBackend`, monitor the same job, and retain logs/artifacts. (`submission -> monitoring -> terminal state`)
5. Inspect rollout and lifecycle artifacts against acceptance criteria, write the test report and summary, and commit completed code/document changes if any. (`artifacts -> report`)

## Acceptance Criteria

- Four rollout JSON files exist and parse.
- Every rollout has reward `1.0`, final answer index `1`, tool calls, and provider token totals.
- TVCache has exact hits and no pending teardown operations.
- `summary.json` reports four completed rollouts and no remaining run sandboxes.
- GPU worker reports `Succeeded`; worker `nvidia-smi`, logs, and launcher metadata are retained.

## Dependencies

`inspect -> {asset copy, worker readiness} -> submission -> monitoring -> artifact validation -> report`

## Errors Encountered

| Error | Attempt | Resolution |
| ----- | ------- | ---------- |
| Worktree `.git` points at an old host path | 1 | Use the main repository metadata for read-only checks; reproduction itself does not require history mutation. |
