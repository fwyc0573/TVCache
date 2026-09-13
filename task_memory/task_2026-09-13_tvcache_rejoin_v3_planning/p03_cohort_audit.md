## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the first P03 inventory and input readiness check. |

# P03 Cohort and Tool Surface Audit

## Scope

P03 needs 8–12 filesystem-heavy W1 tasks. Each selected item must have a task ID, source revision, runtime image digest, include or exclude reason, verifier, and task root. The same pilot must expose seven structured S0 tools and one mutating S1 `exec` tool.

## Read-only inventory

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

## Readiness result

P03 cannot be completed from the current checkout without inventing task metadata or image identities. The required inputs are an approved W1 task source, pinned source revisions, runtime image digests, task roots, and verifiers. Once supplied, cohort selection can be recorded and reviewed before implementing the seven S0 tools plus mutating S1 `exec`.

## Next action

Keep P03 pending. Obtain the missing W1 manifest and image metadata, then add an auditable cohort file and tool declarations. P04 provider work remains deferred until that cohort and tool surface pass review.
