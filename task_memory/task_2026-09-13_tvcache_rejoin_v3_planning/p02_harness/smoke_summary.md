## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the P02 direct scripted rollout and reload checks. |

# P02 Smoke Summary

The lightweight `research/rejoin` package ran one deterministic local rollout from a clean temporary workspace. The rollout generated three JSONL records in this order:

1. `write_file` wrote `src/input.txt` and changed the workspace manifest.
2. `read_file` read the file and preserved the manifest digest.
3. `list_dir` listed `src` and preserved the manifest digest.

The trace reload succeeded. Every event had a contiguous sequence number, normalized arguments, result digest, timing values, and before/after workspace digest. The first event reported `src/input.txt` as changed; the two read-only events reported no changed paths. The direct scripts used only Python 3.10 standard-library functionality and did not call an API, GPU, Docker, TVCache server, or video sandbox.

Raw artifact: [`trace.jsonl`](trace.jsonl)
