## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Initialize post-completion archive |
| 2026-08-31 | Archive the completed reproduction guide and validation evidence |
| 2026-08-31 | Include final lock correction and completion-gate rerun |
| 2026-08-31 | Add fresh isolated-port verification and current document inventory |

# Task Overview

Investigated the TVCache repository from server startup through the client/executor, VideoAgent sandbox, EgoSchema data preparation, and Tinker training entrypoints. Produced an evidence-backed Chinese manual for human reproduction. The server/client protocol path is directly reproducible; the full video/Tinker path is documented as prerequisite-gated because the current environment lacks compatible runtime assets and credentials.

# Deliverables Inventory

- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/manual_reproduction.md` — complete Chinese manual with shell commands, arguments, process topology, logs/outputs, API differences, and debugging/editing workflow.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/tvcache_e2e_manual_reproduction.md` — stable entrypoint linking to the complete manual.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tests/integration/tvcache_http_smoke.py` — minimal reproducible HTTP protocol smoke script.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_http_smoke.md` — final direct HTTP smoke report.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_executor_smoke.md` — fake-environment executor/cache-hit/fork report.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_train_sandbox_preflight.md` — sandbox, train, and dataset preflight report.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_doc_command_guards.md` — shell credential-guard verification report.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_final_verification.md` — fresh static, lock, compile, smoke, and cleanup verification report.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/tvcache/server/uv.lock` — generated lock correction adding the declared `gunicorn==26.2.0` dependency so locked server setup is reproducible.
- `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/env_handbook.md` — verified environment recipe for detecting and aligning the server lock.

# Validation Status

| Validation target | Outcome | Evidence |
| --- | --- | --- |
| Server/client HTTP protocol | PASS | Fresh verification task `final-verify-20260831-162642` on port `18003`: `initial_found=False`, `put_success=True`, `exact_value=manual_value_b`, `exact_tool_exec_time=0.25`, `prefix_history_len=2`, `cache_hits=1`, `prefix_hits=1`, `all_env_count=1`, `RESULT=PASS`. |
| Async executor cache path | PASS | Fresh fake `ToolCallEnv` task `executor-final-20260831-162642` returned `r1 == r2 == mutate:a:state=1` and `r3 == read:b:state=1`; logs show exact hit, prefix/fork, `unref`, suffix execution, and two successful PUTs. |
| Python syntax and lock integrity | PASS | `compileall` exit `0`; server/client/train `uv lock --check` passed after the server lock correction (`15`, `22`, and `39` resolved packages respectively). |
| Manual command/static integrity | PASS | Current `manual_reproduction.md` is `756` lines; headings `## 1` through `## 13` each occur once, `84` fences are balanced, all `30` bash blocks pass `bash -n`, the entrypoint links resolve, and `git diff --check` passes. |
| Tree/run-output persistence | PASS | `/visualize` returned HTTP `200` with `9235` bytes; `/api/save` returned HTTP `200`, created the recorded JSON file, and `/api/runs` returned HTTP `200` with keys `auto_saved_runs`, `base_dir`, and `manual_runs`. |
| Process cleanup | PASS | After the fresh smoke, the started server was interrupted and port `18003` was free; the prior cleanup also found no task-owned TVCache, sandbox, Video-LLaVA, training, or fork-cache process and ports `8001`, `18001`, and `5000` free. |
| VideoAgent sandbox startup | BLOCKED | System stack exits before Flask bind with `RuntimeError: operator torchvision::nms does not exist`; pinned Conda runtime and model assets are absent. |
| Train entrypoint and dataset | BLOCKED | Bare train environment reports `ModuleNotFoundError: pydantic`; download needs undeclared `gdown`; processing needs missing `EgoSchema/videos`. |
| Full Video/Tinker E2E | BLOCKED | Requires compatible GPU/runtime, weights, videos, sandbox URL/path prerequisites, and valid Tinker/OpenAI credentials; no application source or README changed, and only the generated server lock was aligned with its existing manifest. |

# Open Items/Future Extensions

- Install the repository's pinned VideoAgent and Video-LLaVA environments, download model/data assets, and rerun the staged sandbox checks.
- Resolve the hard-coded `AsyncTVCacheClient` and sandbox URLs through a reviewed configuration change before using non-default ports.
- Replace the literal sandbox video source path with an explicit dataset-root configuration after the intended deployment path is confirmed.
- Decide and implement semantics for immutable-tree methods that currently raise `NotImplementedError` (`intel_prefix_match`, `can_extend`, `remove`, and related inspection endpoints).
