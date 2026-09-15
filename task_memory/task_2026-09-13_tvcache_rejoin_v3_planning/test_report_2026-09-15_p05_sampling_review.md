## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Recorded the direct P05 sampling-count audit and its interpretation limit. |

# P05 sampling-count audit

## Execution

- Source configuration: `/data/ycfeng/tmp/rejoin-p05-control-v2/p05-20260915-v2.*.json`.
- Code inspected: `tests/e2e/run_rejoin_p05.py` and `research/rejoin/scripts/collect_p04.py`.
- Environment: CPU master, Python `3.10.6`; no provider or GPU job was submitted.
- Direct check:

  ```bash
  python3 - <<'PY'
  from pathlib import Path
  import collections, hashlib, json
  stage = Path('/data/ycfeng/tmp/rejoin-p05-control-v2')
  rows = []
  for path in stage.glob('p05-20260915-v2.*.json'):
      try:
          data = json.loads(path.read_text())
      except Exception:
          continue
      if not all(key in data for key in ('task', 'rollout_id', 'sampling')):
          continue
      instruction = data['task']['instruction']
      rows.append((data['task']['task_id'], data['rollout_id'],
                   hashlib.sha256(instruction.encode()).hexdigest()[:12],
                   data['sampling']['seed'], data.get('max_steps'),
                   data.get('max_tokens')))
  groups = collections.defaultdict(list)
  for row in rows:
      groups[(row[0], row[2])].append(row)
  assert len(rows) == 40
  assert len(groups) == 10
  assert {len(value) for value in groups.values()} == {4}
  assert {row[4] for row in rows} == {96}
  assert {row[5] for row in rows} == {4096}
  print('P05_SAMPLING_AUDIT PASS')
  print('task_prompts=', len(groups), 'final_rollouts=', len(rows),
        'samples_per_prompt=', sorted({len(value) for value in groups.values()}))
  print('unordered_pairs_per_prompt=', 4 * 3 // 2,
        'directed_pairs_per_prompt=', 4 * 3)
  PY
  ```

## Criteria

1. Count final rollout slots for every task instruction.
2. Confirm whether the provider request sets an API response count.
3. Distinguish independent trajectories from sequential tool turns and retry attempts.
4. Record the number of trajectory pairs available to the P05 matcher.

## Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Task instruction groups | PASS | 10 task instruction hashes; each group has exactly 4 configs (`r0`–`r3`). |
| Merged final slots | PASS | 40 final records: 35 v2 records plus 5 v3 replacements for existing slots. |
| Provider response count | PASS | `collect_p04.py` builds the payload without an `n` field; one response is requested per API turn. |
| Rollout limits | PASS | `max_steps=96`, `max_tokens=4096`, temperature `0.8`, top-p `0.95`. |
| Pair support | PASS | Four trajectories give 6 unordered pairs, 12 directed pairs, and 3 possible donors per recipient before filters. |

## Interpretation

The four trajectories per task are enough to run the P05 descriptive pilot and detect some repeated work. They are too few to support a stable estimate of prompt-level reuse probability. The 667 tool calls are event observations inside 40 trajectories; they do not increase the independent sample count for any one task instruction.

## Limits

The audit checks configuration and persisted local config records. It does not establish provider seed independence; the collector itself records that deterministic behavior has not been established. No sampling extension was run. The recommended extension is documented in `p05_sampling_review.md` and remains a P06 decision.
