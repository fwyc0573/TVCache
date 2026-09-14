## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the first P03 inventory and input readiness check. |
| 2026-09-15 | Closed the runtime audit with ten built images, ten registry digests, ten verifier passes, and the reviewed eight-tool surface. |

# P03 Cohort and Tool Surface Audit

## Scope

P03 needs 8–12 filesystem-heavy W1 tasks. Each selected item must have a task ID, source revision, runtime image digest, include or exclude reason, verifier, and task root. The same pilot must expose seven structured S0 tools and one mutating S1 `exec` tool.

## Initial read-only inventory (2026-09-13)

Commands used:

```bash
find . -type f \( -iname '*manifest*' -o -iname '*task*.json' -o -iname '*benchmark*' \) -not -path './.git/*'
rg -n 'task_id|verifier|image_digest|W1|tool surface' --glob '*.md' --glob '*.py' .
```

Observed repository inputs:

- The checkout contains the TVCache source, unit/integration tests, and prior rollout records.
- The checkout does not contain a W1 task manifest with the required task IDs, source revisions, runtime image digests, task roots, and verifiers.
- The only manifest-like task record found is an older EgoSchema asset manifest; it is a video dataset record and does not satisfy the W1 filesystem task requirements.
- The current P02 package has three smoke tools (`write_file`, `read_file`, and `list_dir`) and is intentionally below the P03 seven-tool surface.
- No new provider, GPU, Docker, or serving execution was attempted during this audit.

## Initial readiness result

P03 cannot be completed from the current checkout without inventing task metadata or image identities. The required inputs are an approved W1 task source, pinned source revisions, runtime image digests, task roots, and verifiers. Once supplied, cohort selection can be recorded and reviewed before implementing the seven S0 tools plus mutating S1 `exec`.

## Initial next action

Keep P03 pending. Obtain the missing W1 manifest and image metadata, then add an auditable cohort file and tool declarations. P04 provider work remains deferred until that cohort and tool surface pass review.

## Runtime completion (2026-09-15)

The supplied W1 manifest was checked out at Terminal-Bench revision `d28711d0da2675d0bb1d56de45ae5df6082438a3`. All ten selected task images were built with the StepBPS route on an H200 worker under `step_main`, and their final tags have non-empty registry manifest digests. Each worker ran the task `solution.sh` and then `run-tests.sh` in the same image with exit code 0; all worker jobs reached `succeeded`.

The seven S0 tools (`read_file`, `write_file`, `list_dir`, `grep`, `stat`, `mkdir`, `remove`) and mutating S1 `exec` are implemented in `research/rejoin/src/rejoin/tools.py`. Direct tests cover declarations, serializable results, workspace path checks, file operations, shell execution, and removal behavior.

**Result:** P03 is complete. The selected ten-task manifest is reviewable and reusable, and the four smoke tasks (`wasm-pipeline`, `polyglot-c-py`, `multi-source-data-merger`, `recover-accuracy-log`) have all required build and verifier evidence for P04 preparation.
