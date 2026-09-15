## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-15 | Audited P05 per-prompt rollout count, provider sampling fields, and the effect on opportunity frequency claims. |

# P05 sampling review

## Question

Check how many final samples are produced for the same task instruction and whether the current setting is sufficient for a reuse-frequency claim.

## Observed configuration

- `tests/e2e/run_rejoin_p05.py` creates four configs per included task with `rollout_id` values `r0` through `r3`.
- The ten included tasks therefore provide ten distinct task instructions and four final rollout trajectories per instruction, for 40 unique rollout slots.
- The v2/v3 run map contains 35 successful v2 records and five successful v3 replacements. The replacements fill existing rollout slots; they are not five additional independent samples.
- The four configs for each task carry the same task instruction, task image digest, task source revision, system policy, temperature `0.8`, and `top_p` `0.95`. Their requested seeds are `20260915`, `20260916`, `20260917`, and `20260918`.
- `research/rejoin/scripts/collect_p04.py` does not set an API `n` field. Each provider request therefore asks for one response. A rollout can issue up to 96 sequential provider decisions, but those decisions are turns inside one trajectory, not additional samples of the initial task prompt.
- A malformed-response retry keeps the same rollout slot and adds a retry instruction to the message list. It is retained as collection evidence and does not increase the independent trajectory count.
- The collector records `seed_support` as accepted while explicitly stating that deterministic behavior has not been established. The four seeds should therefore be treated as sampling attempts, not proven independent random draws.

## Direct count check

The v2 configuration files were reloaded from `/data/ycfeng/tmp/rejoin-p05-control-v2`.

| Measure | Observed value |
| --- | ---: |
| Included task prompts | 10 |
| Final rollout slots per task prompt | 4 |
| Final rollout slots in the merged P05 set | 40 |
| Provider responses requested per API turn | 1 |
| `max_steps` per rollout | 96 |
| `max_tokens` per API turn | 4096 |
| Sampling temperature / top-p | 0.8 / 0.95 |
| API `n` field | absent |

The exact instruction text has one stable hash within each task's four configs. The ten task hashes are different, so P05 does not repeat one common prompt 40 times; it repeats each of ten task prompts four times.

## Why four is weak for a frequency claim

For one task prompt, four trajectories provide only six unordered trajectory pairs, or at most twelve directed donor-recipient pairs before applying the time and post-divergence filters. Each recipient has only three possible donor trajectories. Rare repeated tool work can therefore be missed, and one unusual trajectory can have a large effect on the task-level share.

The 667 observed tool calls increase the number of events, but they do not increase the number of independent prompt-level trajectories. The current C/U counts and time shares are valid descriptions of this collected pilot; they are not stable estimates of the probability that a future rollout will expose reusable work.

## Recommended next decision

Keep the existing 40-rollout collection and cloud evidence. Before treating the P06 redirect as the final workload decision, choose one of these routes:

1. **Expand all ten task prompts to 16 trajectories each (recommended):** add `r4` through `r15`, giving 16 samples per prompt and 120 additional rollouts. Use a disjoint seed range for the added slots, keep the same provider policy, and write a separate sampling-extension run and report. This gives 120 unordered trajectory pairs per prompt, twenty times the four-sample pair count.
2. **Keep four trajectories per prompt:** retain P05 as a descriptive opportunity pilot only. Do not call the C+U share a probability estimate; use it only to select a candidate family for a guarded follow-up.

The first route gives a stronger answer to the user's concern while preserving comparability with the current run. It requires a P05 scope expansion and additional GPU/provider work, so the choice belongs in the P06 decision record. No sampling extension was submitted during this audit.

## Evidence limit

Even 16 trajectories per prompt would still be a research sample rather than a population estimate. It would improve opportunity support and sensitivity, but it would not establish production workload frequency or safe reuse. The typed `multi-source-data-merger` adapter still requires paired fresh-versus-reuse validation before any cache hit is allowed.
