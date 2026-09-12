## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-09 | Recorded freed disk space, permission to resume the complete tool setup, and H800 fallback when H200 resources are unavailable. |
| 2026-09-08 | Recorded the provider boundary: StepCode must provide model inference only, while the local agent loop owns action parsing, tool execution, VideoAgent sandbox lifecycle, and TVCache observation; upstream tool/sandbox execution does not satisfy this round's cache measurement. |
| 2026-09-08 | Recorded the user's model-size choice: use locally downloadable weights and select the smallest verified model combination to minimize disk use. |
| 2026-09-08 | Recorded the decision to use the local StepCode Codex `deepseek-v4-flash` provider through the StepCast vLLM OpenAI-compatible image, move GPU execution to the H200 `step_main` cluster, and limit acceptance to real rollout plus no-cache/TVCache comparison without RL optimizer updates. |
| 2026-09-03 | Recorded that the user supplied a Tinker key in chat; the value is treated as compromised and must be rotated before use. |
| 2026-09-03 | Recorded the request for current official Tinker API-key registration guidance using the company HTTP proxy. |
| 2026-08-17 | Recorded confirmation that the disclosed DeepSeek key was revoked and a replacement was written to the user shell environment. |
| 2026-08-17 | Recorded the DeepSeek V4 Flash selection and persistent credential request without retaining the disclosed secret. |
| 2026-08-17 | Recorded approval to replace OpenAI with DeepSeek plus a local visual path and continue execution. |
| 2026-08-17 | Recorded the follow-up question about replacing the OpenAI key with a DeepSeek API key. |
| 2026-08-17 | Recorded the request for official web research on obtaining and securely injecting the two required API keys. |
| 2026-08-16 | Recorded the request to restore this existing task context and continue execution in the same task directory. |
| 2026-08-16 | Recorded the supplied v7 review handoff and accepted retry-safe teardown follow-up. |
| 2026-08-14 | Created the requirement record from the original request and planning Q&A. |

# Requirements

1. `[Original Request]` Treat this as a new task in the design, source-research, and understanding stage.
2. `[Original Request]` Assess whether the TVCache repository provides complete and sufficient documentation and source code for use in real GPU-based RL rollout scenarios.
3. `[Original Request]` Design and implement an end-to-end plan to reproduce TVCache functionality in a real RL rollout environment.
4. `[Original Request]` Use the repository's native Tinker-based rollout stack for the first reproduction.
5. `[Original Request]` Run a direct full-RL reproduction rather than stopping at a mock-only validation.
6. `[Original Request]` Prioritize functional success in the first GPU run; paper-level performance reproduction is not required in this task.
7. `[Original Request]` The user can provide both `TINKER_API_KEY` and `OPENAI_API_KEY`.
8. `[Original Request]` Root-cause fixes required for reproduction are authorized; temporary patches and fallback behavior are forbidden.
9. `[Original Request]` Use a single-node, two-H800 setup for the first real-environment run.
10. `[Original Request]` Use one EgoSchema question with two rollouts for the first RL smoke test.
11. `[Original Request]` Run an equivalent no-cache baseline before the TVCache run.
12. `[Original Request]` Keep paper-scale metrics, terminal workloads, and SkyRL-SQL reproduction as future work.
13. `[Original Request]` Replace the retired Tinker model with `Qwen/Qwen3.6-35B-A3B`.
14. `[Original Request]` Use Tinker's non-thinking renderer for the replacement model.
15. `[Original Request]` Upgrade and pin the Tinker SDK to `0.24.1`.
16. `[Original Request]` Store task records under `task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction/`.
17. `[Original Request]` Store test and experimental scripts under the repository-level `tests/` hierarchy.
18. `[Original Request]` Produce reproducible Markdown test reports with commands, environment details, PASS/FAIL outcomes, logs, and numeric metrics.
19. `[Original Request]` Continue from the supplied v7 architecture-review handoff: keep Phase 4 blocked, add commit/response-loss regression coverage, and implement a retry-safe drain/stop/ACK contract before repeating the full CPU gate and architecture review.
20. `[Original Request]` Restore the context from this existing task directory and continue executing the same task without creating a new task record.
21. `[Original Request]` Use web research to explain how to obtain both required API keys (`OPENAI_API_KEY` and `TINKER_API_KEY`) and how to inject them safely for the CPU master and later GPU worker.
22. `[Original Request]` Determine whether the current reproduction must use an OpenAI API key or can use a DeepSeek API key instead.
23. `[Original Request]` Replace the OpenAI dependency with DeepSeek plus a local visual path, then continue the reproduction task.
24. `[Original Request]` Use `deepseek-v4-flash`, follow the official DeepSeek API documentation, and persist the DeepSeek credential in the environment.
25. `[Original Request]` The previously disclosed DeepSeek key has been revoked, and a replacement key has been written to `~/.zshrc`; continue execution without recording or exposing its value.
26. `[Original Request]` Consult current official Tinker documentation through the HTTP proxy, explain how to register `TINKER_API_KEY`, and guide setting it as an environment variable.
27. `[Original Request]` Re-check the corrected `TINKER_API_KEY` environment state after the user reported exporting it; the supplied credential value must remain undisclosed in all task records and outputs.
28. `[Original Request]` Do not use Tinker for this reproduction because the user does not currently have a Tinker API key and does not plan to register one due to the billing cost.
29. `[Original Request]` Use the local StepCode Codex `deepseek-v4-flash` model service exposed through its concrete API/provider as the rollout model.
30. `[Original Request]` Use the vLLM inference server image `hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`.
31. `[Original Request]` Move GPU execution from the two-H800 plan to the H200 `step_main` cluster.
32. `[Original Request]` Limit this round's acceptance target to a real inference-driven agent rollout and a no-cache versus TVCache comparison; exclude RL optimizer updates.
33. `[Original Request]` For the first provider-based attempt, keep tool-call parsing, tool execution, VideoAgent sandbox lifecycle, and TVCache cache measurement local to this repository; treat upstream tool or sandbox execution as incompatible with the acceptance target.
34. `[Original Request]` Select the smallest verified local model weights to minimize disk usage while preserving the agreed real rollout tool contract.
35. `[Original Request]` 已经清楚了一定的磁盘空间，请你检查，并继续。如果h200集群无可用集群，迁移到h800集群进行测试验证。
