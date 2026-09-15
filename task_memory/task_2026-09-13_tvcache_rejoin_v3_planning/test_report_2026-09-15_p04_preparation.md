## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-15 | Recorded real local tool checks, provider access, and the queued P04 execution. |

# P04 preparation verification

Preparation checks passed. The complete P04 smoke has not passed yet: the corrected first worker is waiting for H200 quota.

## Execution

Repository: `/data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox`.

CPU interpreter: `/usr/bin/python3`, Python 3.10.6, no conda activation. GPU launcher: `/data/ycfeng/tmp/stepmind-env/bin/python`, Python 3.10.6. Verifier packages were installed into `/data/ycfeng/tmp/rejoin-p04-control/public/verifier_packages` through the company mirror.

```bash
sudo -n env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp \
  /usr/bin/python3 \
  /data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox/tests/e2e/check_rejoin_tool_process.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=research/rejoin/src \
  python3 -m unittest discover -s research/rejoin/tests -v

TMPDIR=/data/ycfeng/tmp UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
  uv pip install --target /data/ycfeng/tmp/rejoin-p04-control/public/verifier_packages \
  --python /usr/bin/python3 \
  --index-url http://mirrors.i.basemind.com/pypi/simple/ --trusted-host mirrors.i.basemind.com \
  'pytest==8.4.1' 'iniconfig==2.1.0' 'packaging==25.0' 'pluggy==1.6.0' \
  'pygments==2.19.2' 'exceptiongroup==1.3.0' 'tomli==2.2.1' 'typing-extensions==4.15.0'

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/data/ycfeng/tmp/rejoin-p04-control/public/verifier_packages \
  python3 -c 'import pytest,pluggy,iniconfig,packaging; print(pytest.__version__,pluggy.__version__,packaging.__version__)'
```

## Criteria and observed evidence

| Check | Passing condition | Observed |
| --- | --- | --- |
| Tool process | Actual S0 write and S1 execution produce expected output | 21 -> 42, PASS |
| Actor filesystem | Controller mounts absent; unprivileged execution | UID 65534; `/data`, `/mnt`, `/tests` absent, PASS |
| Eight-tool surface | Existing declaration, operation, and path checks pass | 3 tests passed in 0.004 seconds |
| Verifier imports | Fixed pytest dependencies import | pytest 8.4.1, pluggy 1.6.0, packaging 25.0, PASS |
| Provider access | Live HTTP success and valid JSON action | HTTP 200; valid read_file action; 1.27 seconds |
| Real smoke | 16 complete, reloadable rollouts satisfying `p04_smoke.md` | Pending; no completed rollout claimed |

The local filesystem check removes its temporary runtime after passing. It verifies tool isolation and actual file effects on the CPU; it does not substitute for the pinned task images or their verifiers.

## Worker execution and continuation

First attempt `exp-0915-140853-974340` failed before provider execution: `nvidia-smi` exited 12. The wrapper now sets the NVIDIA binary and library search paths. Fresh job `exp-0915-141415-207218` is queued with the correct personal creator and local NFS source. The queue reports `Insufficient GPU quota`, `H200=0`.

Commands for the first rollout and automatic continuation:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/tmp/stepmind-env/bin/python \
  /data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox/tests/e2e/run_rejoin_p04.py \
  --stage /data/ycfeng/tmp/rejoin-p04-control --run-id p04-20260915-v2 \
  --task polyglot-c-py --rollout r0

TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/tmp/stepmind-env/bin/python \
  /data/ycfeng/step-sandbox/TVCache/.worktrees/yc-sandbox/tests/e2e/run_rejoin_p04.py \
  --stage /data/ycfeng/tmp/rejoin-p04-control --run-id p04-20260915-v2 \
  --concurrency 4 --await-first
```

The continuation waits for the first launcher to succeed, reuses its completed record, then submits the other 15 rollouts with at most four task workers in flight. It stops visibly if the first run fails. The final completing worker reloads all 16 traces and writes JSON and Markdown smoke reports to cloud `reports/` and the local staging directory. The launchers must remain alive during queuing and execution.
