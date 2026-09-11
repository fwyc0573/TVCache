## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-11 | Recorded the request to reproduce the completed TVCache real rollout on this machine. |

# Requirements

- `[Original Request]` Reproduce the complete end-to-end process from `task_2026-08-14_tvcache_rl_rollout_reproduction` on this new machine.
- `[Original Request]` If required files are missing locally, copy them from `shai-ycfeng` over SSH.
- `[Inherited Acceptance]` Preserve the fixed EgoSchema input, local VideoAgent tools, local Video-LLaVA VQA, TVCache lifecycle, StepCode provider, and two no-cache plus two TVCache rollouts.
- `[Inherited Acceptance]` Produce four successful rollout records, reward `1.0`, final answer index `1`, non-empty tool calls, positive TVCache exact hits, zero remaining run sandboxes, and a successful GPU worker terminal state.
