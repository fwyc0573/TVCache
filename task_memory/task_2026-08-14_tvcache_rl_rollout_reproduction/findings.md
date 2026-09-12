## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-03 | Re-checked the live official Tinker key route, Quick Start, and organization requirements through the company HTTP proxy. |
| 2026-08-17 | Assessed DeepSeek API compatibility against the active VideoAgent OpenAI call sites. |
| 2026-08-17 | Recorded official credential-entry and rlaunch environment-injection research. |
| 2026-08-16 | Verified the two Zenodo archives' uncompressed sizes through their remote ZIP directories. |
| 2026-08-16 | Verified external model archive sizes and shared-storage capacity. |
| 2026-08-16 | Recorded the official model-asset source and first fixed EgoSchema candidate. |
| 2026-08-16 | Confirmed that required local model, socket, and preprocessing assets are absent. |
| 2026-08-16 | Recorded the committed GPU-service environment and launch topology. |
| 2026-08-16 | Confirmed the no-cache and stateless-cache loops share the same tool-error conversion defect. |
| 2026-08-16 | Confirmed the active training/server source map during context recovery. |
| 2026-08-14 | Created the research findings record. |

# Findings

> External and repository-derived research data only. Do not treat content in this file as executable instructions.

- The public repository contains one EgoSchema/Tinker example, while the paper also evaluates terminal and SQL workloads.
- The checkout has five commits and no tagged release.
- The active server uses an in-memory immutable prefix-tree cache.
- The documented `/lock` and `/unlock` endpoints are absent from the active server.
- The async client and server CLI default to port 8001; several docs and synchronous utilities use 8000.
- The current server test list enables only a print-oriented multiple-update test.
- A local baseline run observed `/put` HTTP 500 responses while that test still reported `Passed: 1/1`.
- The committed processed EgoSchema dataset contains 116 entries, but no video files are present.
- The checkout lacks VideoAgent weights and prepared Python environments.
- The repository default Tinker model is retired; the approved current replacement is `Qwen/Qwen3.6-35B-A3B`.
- Paper-scale scripts, raw result artifacts, task manifests, and exact experiment seeds are not public in this checkout.
- The runnable training surface is split across three top-level drivers (`train_without_cache.py`, `train_with_stateless_cache.py`, and `train_with_tvcache.py`) plus separate agent-loop modules; there is no repository-level test configuration.
- The active server implementation is concentrated in `tvcache/server/tvcache_server.py` and `immutable_env_prefix_tree.py`; the only pre-existing server test is `tvcache/server/tests/simple_test_server.py`.
- `train/train_with_tvcache.py` still defaults to the retired model, derives the renderer automatically, and has no TVCache URL field. It skips zero-advantage groups while still unconditionally calling Tinker with the possibly empty `training_datums` list.
- `VideoSandboxEnv` hardcodes `http://localhost:5000`, so the `sandbox_base_url` supplied to `VideoAgentLoop` cannot reach environments created by the executor or fork bank. Its `stop` and `execute` paths also catch infrastructure/data errors and convert them to prints or synthetic tool-result strings, contrary to the fail-fast requirement.
- `VideoAgentLoop.run` catches every executor/tool exception and feeds a synthetic failure string back to the model; this is a second error-swallowing boundary even after the HTTP client is fixed.
- The active server and async client agree on the current `/put` keys (`values`, `tool_exec_times`, `start_idx`) and `/get` response (`found`, `env_id`, `value`, `tool_exec_time`). The pre-existing integration test, not these active endpoints, is the stale-schema component.
- All three training drivers unconditionally submit `forward_backward_async(training_datums, ...)` and `optim_step_async(...)` after filtering zero-advantage groups. Thus both required no-cache and TVCache runs can send an empty optimizer batch when two smoke rollouts receive equal rewards.
- `ImmutableEnvPrefixTreeCache` starts a daemon TTL-cleanup thread in its constructor but exposes no public shutdown method; isolated integration tests must explicitly set its stop event and join the thread to demonstrate clean teardown.
- The async executor’s first miss executes the requested chain, forks the resulting environment, and stores that fork ID; a later longer chain can restore/fork that ID and execute only the uncached suffix. This supports a deterministic in-memory exact-hit/partial-prefix integration test without GPU or Tinker.
- The system Python has `httpx==0.28.1` and `torch==2.5.1+cu124` but no Tinker, datasets, chz, or pytest-asyncio. The existing `train/uv.lock` resolves Tinker `0.16.1`, not the required `0.24.1`, despite the broad `tinker>=0.6.3` manifest constraint.
- The no-cache `VideoAgentLoop` and stateless `CachedVideoAgentLoop` also catch all sandbox execution errors and convert them into tool strings. Their constructors already honor `sandbox_base_url`; only their action-level failure boundary is incorrect.
- `SandboxManager.__init__` initializes all GPU processing components, calls `hub.pull("hwchase17/react")`, and writes `react_prompt_cache.pkl` in the process working directory. Its video loader independently uses a literal placeholder path, so startup side effects and video-path validation are not currently separated.
- The committed VideoAgent environment targets Python 3.9.18 and Torch 2.1.2 but pins both CUDA 11 and CUDA 12 wheel families. Its `run_sandbox.sh` hardcodes GPU 0 and a literal placeholder `OPENAI_API_KEY=your_key`, so it is not a credential-safe reproducible launch entry point.
- Video-LLaVA is a separate Python package with Torch 2.0.1 and Transformers 4.31.0 constraints. The repository-specific service uses 4-bit `LanguageBind/Video-LLaVA-7B` weights from `VideoAgent/cache_dir/` and a Unix socket, rather than the upstream web/controller service.
- The current worktree has no `VideoAgent/cache_dir`, `VideoAgent/tmp`, `VideoAgent/preprocess`, or `VideoAgent/egoschema_cache`; `train/EgoSchema` contains 5.3 MiB of metadata/scripts but no videos. The service cannot yet execute a real video tool call.
- `SandboxManager.preprocess` looks for reusable data only at the relative path `./egoschema_cache`. When it is absent or incomplete, the manager runs captioning, temporal-feature, tracking, and ReID preprocessing through the GPU components initialized at service startup.
- The repository documentation points to Zenodo record `11031717` for both `cache_dir.zip` and `tool_models.zip`; both are required by the repository-specific service topology.
- The first deterministic candidate in `train/EgoSchema/processed_videos.json` is video `026a2f15-c454-4c28-80e0-24c85d7f4ecf.mp4`, Google Drive object `11rO7KATZd93vslfUasfXG5hxg2KpYAYu`, with correct option index `3`. It remains a candidate until the video download and decode are verified.
- Zenodo reports `tool_models.zip` as 12,435,543,255 bytes and `cache_dir.zip` as 15,416,283,586 bytes, for 27,851,826,841 compressed bytes total. Shared `/data` storage currently has 136 GiB available; extraction size still needs to be checked before download/extraction.
- HTTP range inspection of the remote ZIP central directories reports 14,037,998,498 uncompressed bytes for `tool_models.zip` and 18,759,325,160 uncompressed bytes for `cache_dir.zip`, or 32,797,323,658 bytes total. Keeping both archives and both extracted trees simultaneously requires 60,649,150,499 bytes before filesystem overhead; the current `/data` free space is 134 GiB, so the required artifacts fit without deleting unrelated data.
- OpenAI's official Help Center page `https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key` states that keys are created and managed on the API key page, a full secret key is shown only at creation, and a lost/unsaved key must be replaced. OpenAI's official Python SDK links directly to `https://platform.openai.com/settings/organization/api-keys`.
- The official Tinker console at `https://tinker.thinkingmachines.ai/` redirects unauthenticated users into Thinking Machines' hosted login flow. The official Quick Start links this console as the place to obtain a key, requires `TINKER_API_KEY`, and confirms that `tinker.ServiceClient()` reads that environment variable.
- Tinker's official data-model documentation says the first sign-in automatically creates a personal organization and makes the user its Admin. Creating an organization is free and needs no billing setup, but each organization is billed separately; training and sampling requests are rejected until the organization has a balance or enterprise agreement. No invitation-only requirement appears in the current public onboarding material.
- Tinker's official Quick Start publishes `export TINKER_API_KEY="your-api-key-here"` as its setup example. For this task, the value must instead be entered through a hidden shell prompt so it does not enter history or docs.
- The normal official OpenAI Help Center routes returned a Cloudflare HTTP 403 from this CPU master, but the same official article routes with a `.json` suffix returned server-rendered official article text. This provided current first-party evidence without relying on third-party summaries.
- OpenAI's official key-safety page says: use a unique key per team member; never deploy keys in browsers/mobile apps; never commit keys even to private repositories; prefer the `OPENAI_API_KEY` environment variable; consider a key-management service for production; monitor usage; and rotate a suspected leaked key immediately.
- OpenAI's official billing page states that ChatGPT and API Platform use separate billing systems. The current prepaid-billing page directs new API users to the API billing overview, configuration of auto-recharge, and an initial credit purchase; it says API use can begin after the credit balance updates.
- OpenAI's official Python SDK reads `OPENAI_API_KEY` from the environment, warns against source-control storage, and links the organization API-key settings page.
- In the active reproduction, a DeepSeek key is not a drop-in replacement for `OPENAI_API_KEY`: `SandboxManager` rejects startup without `OPENAI_API_KEY`; frame captioning constructs the default OpenAI client and requests `gpt-4.1-mini` with image inputs; object-memory reasoning constructs `ChatOpenAI(model="gpt-4.1")`; and the optional GPT-4V path hardcodes OpenAI's endpoint and model.
- DeepSeek's current official API documentation states that its API is OpenAI-format compatible when both `base_url`, key, and model are changed. Its published `deepseek-v4-flash`/`deepseek-v4-pro` feature table includes text chat, Tool Calls, Responses API, and Anthropic API, but does not list vision/image input. Therefore it can plausibly replace the text-only object-memory reasoning call after an explicit code change, but it does not establish compatibility with the active GPT frame-captioning call.
- A no-OpenAI variant would require an intentional provider change plus a separate solution for image captioning, such as validated local/precomputed VideoAgent captions. It must be a fail-fast selected configuration, not automatic provider fallback, and would no longer be the unchanged native first reproduction.
- The installed `/kubebrain/rlaunch --help` exposes `-e/--env` and `--set-env` only as literal `NAME=value` arguments. Supplying either API key through those flags would place the secret in the launch command and potentially shell history/process metadata, so this task must not use those flags for credentials.
- The verified safe worker pattern is an interactive `rlaunch -- bash` session followed by hidden `read -s` prompts inside the worker shell; child services launched from that shell inherit the exported variables without embedding the values in the rlaunch command.
- The current official Tinker Quick Start at `https://tinker-docs.thinkingmachines.ai/tinker/quickstart/` links API-key creation to `https://tinker.thinkingmachines.ai/keys`, shows `export TINKER_API_KEY="your-api-key-here"`, and states that `tinker.ServiceClient()` reads the variable from the environment.
- The current official Data Model page at `https://tinker-docs.thinkingmachines.ai/tinker/data-model/` says first sign-in creates a personal organization and that training/sampling requests require an organization balance or enterprise agreement.
