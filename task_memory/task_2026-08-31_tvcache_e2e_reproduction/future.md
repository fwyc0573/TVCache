## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Initialize out-of-scope future work log |
| 2026-08-31 | Record prerequisite and production-code follow-up work |

# Future Work

- Provision the pinned VideoAgent Conda environment and Video-LLaVA Python/CUDA environment on an approved GPU worker, then download `cache_dir`, `tool_models`, and the EgoSchema videos into persistent workspace storage.
- Add reviewed configuration plumbing for the TVCache async-client URL, sandbox URL, and sandbox video dataset root; keep each value visible in startup logs and validate it at the receiving process.
- Add missing runtime dependencies to the authoritative manifests (`httpx`, cookbook/train imports, and dataset helper as appropriate), regenerate locks, and rerun the import gates.
- Define and implement semantics for the immutable-cache methods that currently raise `NotImplementedError`, then validate each route with direct HTTP evidence.
- Run the one-batch VideoAgent/Tinker command after credentials and assets are present; record model/sandbox readiness, rollout hit/miss counts, reward, latency, and checkpoint paths in a new test report.
