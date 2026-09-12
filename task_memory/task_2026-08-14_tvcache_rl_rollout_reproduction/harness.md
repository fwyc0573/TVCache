## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-08-17 | Added provider-migration gates for DeepSeek non-thinking text and local-only visual inference. |
| 2026-08-16 | Added the production teardown convergence and transport-only retry gate from v8 architecture review. |
| 2026-08-14 | Created task gates and drift-control rules. |

# Task Harness

## Implementation Gates

1. No production behavior change without a failing regression test first.
2. No silent fallback for cache, sandbox, Tinker, model, data, or dependency failures.
3. No GPU allocation until all CPU unit and integration gates pass.
4. No performance claim from the 1-question smoke test.
5. No multi-worker or multi-node TVCache deployment in this task.
6. No secrets in files, process listings, logs, or reports.
7. No temporary output under `/tmp`.
8. No broad Tinker cookbook synchronization without explicit user approval.
9. Production teardown may automatically retry only uncertain transport failures; semantic failures must remain fail-fast.
10. The active VideoAgent path must not require, propagate, or call an OpenAI credential or endpoint.
11. DeepSeek ReAct calls must use `deepseek-v4-flash`, `https://api.deepseek.com`, the `DEEPSEEK_API_KEY` environment value, and explicitly disabled thinking.
12. Caption retrieval and VQA must remain local LaViLa and Video-LLaVA operations; no provider fallback is allowed.

## Functional Acceptance Gates

- Cache exact-hit and partial-prefix behavior is demonstrated with backend execution counts.
- URL and runtime-directory settings reach every environment created directly or through the fork bank.
- Environment cleanup is observable and leaves no unexpected sandbox state.
- The production `async with` lifecycle reaches zero pending drains, stops, and ACKs after one lost response at each teardown stage while reusing the original operation IDs.
- Baseline and TVCache RL use the same fixed dataset item and configuration.
- Zero-advantage batches are explicit, valid outcomes and never produce an empty optimizer request.
- On-demand local captions preserve the existing three-value caller contract and report API token counts `0/0`.
- Unsupported non-Video-LLaVA VQA configuration raises before tool execution.

## Drift Checks

- Compare each implementation change against `requirements.md`, `design.md`, and this file.
- Record every change with motivation, expectation, method, and result in `progress.md`.
- Record unresolved deviations in `issues.md` and future-only work in `future.md`.
