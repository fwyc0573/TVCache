## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Recorded P03 worker, source, registry, evidence, and disk-management constraints. |

# P03 Operational Notes

- CPU master: no usable Docker-compatible runtime. Do not retry nested Docker builds here.
- Image build route: use StepBPS with context-free Dockerfiles under `/data/ycfeng/tmp/rejoin-p03-stepbps-dockerfiles/`.
- Verifier route: use StepMind Python `RJobBackend` on H200 with `step_main`, creator `i-fengyicheng`, and the local NFS source `100.96.128.193:/data/ycfeng/tmp`.
- Reusable source: keep `/data/ycfeng/tmp/terminal-bench-1-d28711d0da2675d0bb1d56de45ae5df6082438a3` at revision `d28711d0da2675d0bb1d56de45ae5df6082438a3`.
- Reusable evidence: keep `/data/ycfeng/tmp/rejoin-verifier-logs/`, final Dockerfiles, build snapshots, `rejoin_p03_runtime_digests.json`, and `run_rejoin_verifier_worker_v5.py`.
- Disk cleanup completed on 2026-09-15: archived failed P03 intermediates and generated Python caches were removed. No P03 large file was compressed because the only large reusable item is the direct source checkout needed by P04. Unrelated large files under `/data/ycfeng/tmp` were left untouched.
- Temporary files and caches belong under `/data/ycfeng/tmp`; do not place worker caches or raw logs in the Git worktree.

