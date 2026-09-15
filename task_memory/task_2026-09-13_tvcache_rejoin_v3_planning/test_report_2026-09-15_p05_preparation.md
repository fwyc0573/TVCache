## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Recorded P05 runner, collector, checker, and analyzer preparation checks. |

# P05 preparation verification

## Execution

- Repository: `/data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox`
- Python: `/usr/bin/python3` through the existing `/data/ycfeng/tmp/stepmind-env` interpreter.
- Syntax command:

  ```bash
  python3 -m py_compile research/rejoin/scripts/collect_p04.py \
    research/rejoin/scripts/check_p05.py research/rejoin/scripts/analyze_p05.py \
    tests/e2e/run_rejoin_p05.py tests/e2e/rejoin_worker.py
  ```

- Configuration command:

  ```bash
  python3 tests/e2e/run_rejoin_p05.py \
    --stage /data/ycfeng/tmp/rejoin-p05-control \
    --run-id p05-dryrun --prepare-only
  ```

- Direct analyzer rule check used two synthetic rollout event lists and imported `analyze_p05.classify` and `donor_class` with `PYTHONPATH=research/rejoin/src:research/rejoin/scripts`.

## Criteria

1. Every new Python module parses and compiles.
2. The runner prepares exactly ten included tasks × four rollout configs.
3. The collector accepts only `p04` or `p05` and keeps P04's default path.
4. A post-divergence S0 event with equal observed effect is classified C.
5. P05 output paths and report names are phase-specific.

## Evidence

| Check | Result | Evidence |
|---|---|---|
| Python compile | PASS | `py_compile` exited 0 for all five files. |
| P05 config preparation | PASS | Output `P05_PREPARED 40`; generated stage size was 796 KiB. |
| Synthetic C classification | PASS | `classify(...)` returned `C`; donor lookup returned the earlier rollout event. |
| P05 path/config inspection | PASS | Config contains `phase=p05`, `expected_rollouts=40`, `check_script=check_p05.py`, and `rollouts/p05` is selected by the collector. |
| Existing worker chroot helper | DEFERRED | `tests/e2e/check_rejoin_tool_process.py` stopped with its explicit `Run with sudo` requirement on the CPU master. The same worker isolation and UID evidence is retained in the P04 v21 report. |

## Limits

No provider call, GPU job, cloud artifact, A/B/C/U/N result, or P06 decision is established by this preparation report. Those require the P05 worker collection and cloud-side analyzer.
