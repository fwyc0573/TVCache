## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Define task-specific verification gates |

# Harness and Gates

- Run only repository-supported entry points or explicitly label exploratory probes.
- Record exact command lines and environment versions.
- Capture stdout/stderr and exit status in persistent task artifacts.
- Compare expected behavior with source contracts and observed values.
- Stop a check once its stated failure mode is resolved; avoid speculative coverage.
