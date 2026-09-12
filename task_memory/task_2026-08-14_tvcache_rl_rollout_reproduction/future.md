## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-08-16 | Added driver-wide proactive warmup ownership for future multi-batch runs. |
| 2026-08-14 | Created future-work register. |

# Future Work

- Reproduce the paper's EgoSchema scale and speedup metrics.
- Recover or obtain the exact 100-task paper manifest and original model access.
- Reproduce terminal-bench and SkyRL-SQL workloads.
- Implement and validate same-prefix request coalescing.
- Add shared-state sharding, multi-worker support, and multi-node environment routing.
- Measure cache-server saturation, tail latency, and proactive-fork resource amplification.
- Define and validate driver-wide ownership and teardown for proactive forks before enabling multi-batch TVCache training.
- Compare H800 results with the paper's A100/L40S hardware.
