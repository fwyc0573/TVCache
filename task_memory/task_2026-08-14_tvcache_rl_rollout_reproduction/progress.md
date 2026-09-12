## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-10 | Recorded pinned asset validation, offline-loader GPU failures, SciPy repair, and CUDA 11.8 wheel acquisition. |
| 2026-09-09 | Recorded provider accounting fixes, live usage, ViCLIP verification, current downloads, and the failed H200 direct download probe. |
| 2026-09-09 | Resumed complete local-tool setup after disk cleanup; verified H200 CUDA execution, recorded missing dependencies, and prepared isolated Python 3.10 runtimes. |
| 2026-09-08 | Added a local GPT-2 tokenizer bundle (vocab/merges/config) to the small-model asset layout and made LaViLa resolve it through the central registry; focused provider/runtime tests remain green. |
| 2026-09-08 | Connected the local DINOv2-S checkpoint to Tracking with explicit non-pretrained construction and strict local state-dict loading; focused provider/runtime tests remain green. |
| 2026-09-08 | Downloaded and verified one fixed EgoSchema video from the Hugging Face raw-video mirror; created the reproducible sample manifest and began H200 `step_main` asset validation. |
| 2026-09-08 | H200 `step_main` worker reached `Ready` on `gpu-h200-0482` with the StepCast image, H200 GPU, video mount, and `STEPCODE_API_KEY=SET`; preflight found no VideoAgent model/runtime or preprocessing assets, so real visual tool-chain execution is blocked without the excluded local weights. |
| 2026-09-08 | Injected the local StepCode `apiKey` into H200 `step_main` via `rlaunch --env`; live protocol passed with `/v1/models` 200, `json_object` 200, and `role=tool` round-trip 200. `json_schema` was rejected with HTTP 400, so the adapter now validates JSON locally. |
| 2026-09-08 | H200 `step_main` provider smoke reached `Ready` with the specified image after correcting image startup (`--enable-sshd=false`, `--entrypoint=/bin/bash`), then failed fast because `STEPCODE_API_KEY=UNSET`. |
| 2026-09-08 | Stopped local-weight acquisition at the disk/scope gate: the active rollout exposes Video-LLaVA VQA, no smaller compatible VQA backend is verified, and the remaining filesystem space cannot safely hold the full Video-LLaVA plus the smallest VideoAgent bundle and preprocessing/runtime assets. |
| 2026-09-03 | Refreshed the authorized Tinker environment, verified SDK `0.24.1` import, and observed the first authenticated capability request blocked by HTTP 402 billing status. |
| 2026-09-03 | Confirmed `TINKER_API_KEY=SET` in interactive zsh, then stopped use of the credential because the full value was disclosed in chat and must be rotated. |
| 2026-09-03 | Rechecked shell startup files after the user reported setting `TINKER_API_KEY`; the variable is absent from all checked startup files and remains unset in interactive and non-interactive zsh. |
| 2026-09-03 | Re-verified the official Tinker key route and environment-variable instructions through the company HTTP proxy. |
| 2026-08-17 | Resolved the disclosed-key blocker and reopened CPU work for the DeepSeek/local-vision migration. |
| 2026-08-16 | Stopped at the Phase 4 credential gate because both required API keys are unset; no worker request was made. |
| 2026-08-16 | Closed I-047 and opened Phase 4 after v9 architecture CLEAR and code/spec/security APPROVE. |
| 2026-08-16 | Completed the fresh 175-test Python 3.12 gate after production teardown convergence and restored the frozen environment. |
| 2026-08-16 | Restored the task, archived both v8 verdicts, and reopened production teardown convergence remediation after the architecture BLOCK. |
| 2026-08-16 | Completed I-047 affected/full verification and the fresh 173-test Python 3.12 gate with frozen restoration. |
| 2026-08-16 | Added and confirmed the existing baseline client's generated stop-operation identity RED regression. |
| 2026-08-16 | Completed the authoritative post-I-046 Python 3.12 gate and restored the frozen environment. |
| 2026-08-16 | Completed the focused I-046 GREEN implementation and provisional full CPU suite. |
| 2026-08-16 | Added and verified the I-046 task-drain and run-lifecycle RED regressions. |
| 2026-08-16 | Restored the v6 review context, recorded the architecture BLOCK, and opened I-046. |
| 2026-08-16 | Audited bank deposit and higher-level withdrawal retry reachability for the fixed smoke. |
| 2026-08-16 | Completed the fresh post-I-044/I-045 Python 3.12 gate and restored the frozen environment. |
| 2026-08-16 | Completed the I-044/I-045 temporary-environment ownership RED-to-GREEN cycle. |
| 2026-08-16 | Added and verified the I-044/I-045 close-retry RED assertions. |
| 2026-08-16 | Recorded the matching v5 code/spec/security REQUEST CHANGES verdict. |
| 2026-08-16 | Recorded the v5 architecture BLOCK, opened I-044/I-045, and reopened CPU phases. |
| 2026-08-16 | Refreshed H800 launch guidance and credential/GPU readiness while v5 review runs. |
| 2026-08-16 | Completed the fresh 149-test Python 3.12 CPU gate and restored the frozen environment. |
| 2026-08-16 | Completed the I-043 partial-prefix cleanup ownership RED-to-GREEN cycle. |
| 2026-08-16 | Added and verified three I-043 partial-prefix ownership RED regressions. |
| 2026-08-16 | Completed the I-042 failed-withdraw ownership RED-to-GREEN cycle. |
| 2026-08-16 | Added and verified the I-042 failed-withdraw ownership RED regression. |
| 2026-08-16 | Restored the v4 review context, opened I-042/I-043, and reopened CPU TDD and implementation. |
| 2026-08-16 | Added and verified v3 RED regressions for I-035 through I-039. |
| 2026-08-16 | Recorded both v3 review failures and reopened CPU TDD for I-035 through I-041. |
| 2026-08-16 | Verified that the required Zenodo archives and extracted model trees fit on shared storage. |
| 2026-08-16 | Restored the task at the v3 pre-GPU review gate and re-read the authoritative H800 launch recipe. |
| 2026-08-16 | Completed the fresh Python 3.12 CPU gate, restored the frozen environment, and closed the v2 CPU blockers. |
| 2026-08-16 | Recorded the real Tinker preflight RED and native chz help-exit root cause. |
| 2026-08-16 | Recorded verified Python 3.12 artifact installations and successive frozen offline sync interruptions. |
| 2026-08-16 | Restored the Python 3.12 preflight interruption point and resumed the canonical SciPy artifact transfer. |
| 2026-08-16 | Restored the v2 remediation context and resumed at executor ownership and metric classification. |
| 2026-08-16 | Restored the interrupted metrics rework and completed baseline/stateless numeric statistics. |
| 2026-08-16 | Recorded the independent code/spec/security REQUEST CHANGES verdict. |
| 2026-08-16 | Paused GPU entry and reopened CPU work after an independent architecture BLOCK. |
| 2026-08-16 | Recorded the local environment and credential preflight before worker launch. |
| 2026-08-16 | Re-read the authoritative H800 worker recipe and confirmed that GPU allocation must use `rlaunch`. |
| 2026-08-16 | Recorded the fresh full CPU gate and archived Phases 2 and 3 as complete. |
| 2026-08-16 | Restored the task again at the remaining CPU TDD gate and confirmed the exact interruption point. |
| 2026-08-16 | Restored context, audited interrupted TDD work, and recorded the first reproduced test-environment failure. |
| 2026-08-14 | Created progress log and recorded worktree initialization. |

# Progress

### 2026-09-09 Continuation: Assets and GPU Runtime

- Motivation: resume the approved full-tool rollout after the user freed disk space; keep H800 as an authorized fallback when H200 step_main has no capacity.
- Expectation: preserve local VQA, prepare the smallest verified compatible weight set and separate legacy tool runtimes, and then perform the two baseline plus two TVCache rollouts.
- Method: observed **122,784,391,168 B** free space, resumed clean range downloads, queried the official Hugging Face model metadata, and ran `tests/e2e/videoagent_runtime_probe.py` in the specified image on H200. Exact runtime evidence is in `test_report_2026-09-09_h200_runtime.md`.
- Result: H200 candidate nodes each exposed **8** available GPUs; the live probe used **1** H200 and returned Python **3.12.13**, Torch **2.10.0+cu129**, and CUDA sum **4.0** against expected **4.0**. CLIP completed at **353,976,522 B** with its official SHA-256. ViCLIP remains in progress; LaViLa is pending. Selective Video-LLaVA acquisition is running through `tests/performance/download_videollava_assets.py` using the existing train environment's Hugging Face client.
- Asset inventory correction: the **14,933,716,280 B** Video-LLaVA main checkpoint additionally requires LanguageBind image/video towers of **1,710,619,975 B** and **2,114,828,105 B**. All revisions and LFS digests are in `/data/ycfeng/tmp/tvcache-asset-inventory-20260909/`. Current capacity covers them.
- Runtime preparation: portable Python **3.10.20** resides at `/data/ycfeng/tmp/tvcache-runtime-py310`; new environments are `/data/ycfeng/tmp/tvcache-videoagent-20260909` and `/data/ycfeng/tmp/tvcache-videollava-20260909`. VideoAgent installation uses its declared Torch **2.1.2**, torchvision **0.16.2**, Transformers **4.27.0**; Video-LLaVA uses Torch **2.0.1**, torchvision **0.15.2**, Transformers **4.31.0**. Installation is pending, so these are intended versions, not validated imports.
- Network failure and correction: two `uv` index attempts timed out even after synchronizing proxy cases; a requests probe timed out at the proxied PyPI TLS handshake. Direct official PyPI returned **HTTP 200 in 0.53 s**. The install process now bypasses the proxy only for `pypi.org` and `files.pythonhosted.org`; model downloads retain the proxy. Resolution/build progress has begun; final installation remains pending.
- Commit blocker: Git rejected both stage/commit because `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.git/worktrees/tvcache-rl-reproduction/index.lock` exists. It is **0 B**, modified **2026-09-07 15:50:32 +0800**, with no matching Git writer found. Explicit permission to delete this one stale lock was requested asynchronously. No lock removal or commit occurred.
- Outstanding chain: finish downloads/installations -> local model imports/constructors -> real preprocessing and VQA -> sandbox/TVCache -> baseline two rollouts -> TVCache two rollouts -> numeric report and teardown. Current real rollout count remains **0/4**.

### Small-Model DINOv2 Local-Weight Wiring

- Motivation: the H200 preflight review found that `torch.hub.load` defaulted to `pretrained=True`, so the downloaded DINOv2-S checkpoint was ignored and a second remote download could occur.
- Expectation: Tracking constructs `dinov2_vits14` without network weight loading and reads the exact checkpoint under `VIDEO_AGENT_MODEL_DIR`.
- Method: added `dinov2_checkpoint` to the central model registry; required the file, constructed with `pretrained=False`, normalized common checkpoint prefixes, and loaded the local state dict with `strict=True` before moving to CUDA. Tightened range-download read timeout from 600 s to 120 s for stalled proxy chunks.
- Result: `python3 -m py_compile` passed and the focused provider/runtime suite passed **15/15**. GPU constructor validation remains pending until all model files assemble.

### Small-Model GPT-2 Tokenizer Bundle

- Motivation: LaViLa's tokenizer constructor otherwise searches the implicit Hugging Face cache for `gpt2`, which is not part of the reproducible model directory.
- Expectation: Captioning reads tokenizer files from `VIDEO_AGENT_MODEL_DIR/gpt2_tokenizer` and fails clearly when the bundle is absent.
- Method: changed the registry value and Captioning path resolution, then downloaded the public `vocab.json`, `merges.txt`, and `tokenizer_config.json` files through the configured proxy.
- Result: the bundle is present under `/data/ycfeng/tmp/videoagent_small/gpt2_tokenizer`; syntax and focused provider/runtime tests passed **15/15**.

### Video-LLaVA Disk and Scope Gate

- Motivation: preserve the user's smallest-weight objective without producing a rollout whose advertised VQA tool can fail unpredictably because its model is absent.
- Expectation: establish whether the currently verified model path fits the available persistent workspace before acquiring more weights.
- Method: inspected the active VQA loader and rollout tool schema, compared the verified **14,933,716,280 B** selective Video-LLaVA inventory plus approximately **3.5 GB** small-model bundle against the observed **16,403,120,128 B** free space, and stopped the clean CLIP range download after a partial **224 MiB** transfer.
- Result: I-055 is blocked pending a user decision between preserving the complete Video-LLaVA-backed tool set with more disk and formally removing VQA from this round's schema/acceptance. The incomplete CLIP parts remain isolated under `/data/ycfeng/tmp/videoagent_small_clean`; no formal checkpoint was published and no mixed old parts were deleted.

### Tinker SDK Billing Gate

- Motivation: confirm that the refreshed environment can reach Tinker before continuing the real rollout path.
- Expectation: the pinned Tinker `0.24.1` SDK reads `TINKER_API_KEY` and returns server capabilities, or exposes a concrete account/configuration failure.
- Method: sourced the active user's zsh configuration, imported `tinker==0.24.1`, constructed `ServiceClient`, and called `get_server_capabilities()` without printing credentials or response secrets.
- Result: the SDK read the environment successfully, but Tinker returned HTTP **402** with `Access ... is blocked due to billing status` and directed the account to `https://tinker.thinkingmachines.ai/billing/balance`. The key gate is passed; training/sampling and GPU worker execution are blocked by organization billing until balance or an enterprise agreement is available.

### Tinker Credential Exposure and Rotation Gate

- Motivation: verify the user's corrected environment state while preserving credential safety.
- Expectation: confirm only whether `TINKER_API_KEY` exists, then prevent the disclosed value from entering any execution or task artifact.
- Method: started a fresh interactive zsh and emitted only the presence status; did not print, inspect, persist, or send the variable value.
- Result: `TINKER_API_KEY=SET` and shell stderr is empty. The full credential was included in the user message, so it is treated as compromised. Tinker SDK calls, GPU allocation, and worker launch remain paused until the key is revoked and replaced through the official Tinker Console.

### Tinker Credential Refresh Blocker

- Motivation: refresh the environment after the user reported writing `TINKER_API_KEY` to zsh startup configuration.
- Expectation: a new zsh process sources the configured key and reports presence without exposing its value.
- Method: sourced `/home/i-fengyicheng/.zshrc` in interactive and non-interactive zsh; inspected only redacted startup-file line shapes across `.zshenv`, `.zprofile`, `.zshrc`, `.zlogin`, `.profile`, `.bash_profile`, and `.bashrc`.
- Result: both zsh modes report `TINKER_API_KEY=UNSET`, and no checked startup file contains a Tinker key assignment or reference. The credential refresh cannot proceed until the key is written to the active user's startup file or entered through a hidden prompt. GPU allocation and further Phase 4 execution remain paused.

### Official Tinker API-Key Registration Guidance Refresh

- Motivation: provide current first-party instructions for obtaining `TINKER_API_KEY` and setting it without exposing the value.
- Expectation: confirm the live console/key route, the official environment variable name, and organization/billing prerequisites through the required HTTP proxy.
- Method: loaded `https://tinker-docs.thinkingmachines.ai/tinker/quickstart/`, `https://tinker-docs.thinkingmachines.ai/tinker/data-model/`, and the key route `https://tinker.thinkingmachines.ai/keys` with the company proxy initialized from `http://deploy.i.shaipower.com/httpproxy`; inspected only public documentation text and response redirects; checked local key presence without reading any value.
- Result: official Quick Start links key creation to `https://tinker.thinkingmachines.ai/keys`, shows `TINKER_API_KEY` as the required variable, and states that `tinker.ServiceClient()` reads it from the environment. The key route redirects unauthenticated users to official Tinker authentication. Official Data Model documentation states that first sign-in creates a personal organization, while training and sampling require an organization balance or enterprise agreement. Current shell state remains `TINKER_API_KEY=UNSET`; no key value was requested, printed, or stored.

### DeepSeek Key Rotation and Provider-Migration Resume

- Motivation: resume the approved DeepSeek plus local-vision migration after the disclosed credential was revoked.
- Expectation: close only the credential-disclosure blocker, preserve secret hygiene, and define testable provider boundaries before changing production code.
- Method: accepted the user's rotation confirmation without inspecting the value; updated `requirements.md`, `issues.md`, `design.md`, `harness.md`, and `plan.md`; reopened Phase 2 and Phase 3 for TDD and implementation.
- Result: I-048 is resolved. The active design now requires `deepseek-v4-flash` with disabled thinking, local LaViLa captions, and Video-LLaVA-only VQA with no OpenAI fallback. No provider production code has been changed yet; Phase 2 RED tests are next, while Phase 4 remains blocked by the unconfirmed Tinker credential and external GPU assets.

### DeepSeek Credential Disclosure Block

- Motivation: prevent a credential disclosed through chat from being copied into additional persistent or observable locations.
- Expectation: retain the provider/model decision while ensuring the disclosed value is neither used nor written to commands, shell startup files, repository artifacts, logs, or task records.
- Method: recorded only the sanitized `deepseek-v4-flash` decision and opened I-048; did not execute any credential-bearing command.
- Result: execution is stopped at the credential gate. The disclosed key is treated as compromised and remains unpersisted. The user must revoke it and create a replacement before secure injection and implementation continue.

### OpenAI-versus-DeepSeek Credential Feasibility Check

- Motivation: determine whether the remaining OpenAI credential gate can be removed without silently changing the required rollout behavior.
- Expectation: distinguish API-format compatibility from actual model/feature compatibility across every reachable VideoAgent call site.
- Method: traced the startup validation, frame-captioning client, object-memory reasoning client, optional GPT-4V request, default local Video-LLaVA selection, and six-tool rollout prompt; compared them with DeepSeek's current official API and model-feature documentation.
- Result: the unchanged reproduction still requires an OpenAI key. A DeepSeek key alone fails because the code still targets OpenAI endpoints and `gpt-4.1` models, while the active frame-captioning request sends images and DeepSeek's published model table does not claim vision input. DeepSeek can potentially replace only the text reasoning portion after an approved behavior change; a complete no-OpenAI variant also needs a validated local/precomputed captioning path. No code or credential state changed.

### Official API-Key Acquisition and Injection Research

- Motivation: unblock Phase 4 without exposing either credential in chat, repository files, command history, logs, or `rlaunch` arguments.
- Expectation: identify official creation portals and account/billing prerequisites for OpenAI and Tinker, then define hidden-prompt injection for both the CPU master and the interactive GPU worker.
- Method: recorded the user request in `requirements.md`; inspected current task state and the authoritative GPU handbook; retrieved the official Tinker Quick Start, documentation search index, console login redirect, and data-model onboarding text; inspected the installed `rlaunch` CLI; probed official OpenAI documentation/help pages; and installed the official OpenAI Developer Docs MCP configuration after confirming it was absent.
- Result: official evidence is complete. Tinker directs users to its console for key creation, reads `TINKER_API_KEY`, creates a personal organization at first sign-in, and requires an organization balance or enterprise agreement for training/sampling. OpenAI provides its key-management page, shows the full secret only once, requires separate API billing, and recommends `OPENAI_API_KEY` rather than repository storage. `rlaunch` accepts literal environment arguments, which are unsuitable for secrets, so credentials must be entered with hidden prompts separately inside each target shell. No key was requested, printed, stored, or tested, and no GPU resource was requested.

## 2026-08-14

### Status

- Completed: planning and source/paper audit.
- In progress: isolated task setup and baseline verification.
- Pending: TDD, implementation, CPU validation, GPU preparation, real RL smoke, review, and completion.

### Worktree Initialization

- Motivation: isolate implementation from `main` and comply with the project worktree convention.
- Expectation: create `.worktrees/tvcache-rl-reproduction` on a dedicated branch without polluting repository status.
- Method: added `.worktrees/` to the local Git exclude file and ran `git worktree add`.
- Result: worktree created on `task/tvcache-rl-reproduction` at baseline commit `3a4f95a`.

### Initialization Error

- Motivation: verify `.worktrees/` was ignored before creation.
- Expectation: `git check-ignore -v .worktrees` returns the matching exclude rule.
- Method: checked the path before the directory existed.
- Result: the command returned exit code `1`; created the empty directory, rechecked `.worktrees/`, then successfully created the worktree.

## 2026-08-16

### Context Recovery

- Motivation: resume the existing task without overwriting or repeating interrupted work.
- Expectation: identify the active branch, recorded plan state, uncommitted source changes, tests, and exact interruption point.
- Method: read all task records, ran the `planning-with-files` session catch-up script, inspected `git status`, `git diff --stat`, file paths, and modification times.
- Result: resumed branch `task/tvcache-rl-reproduction`; the catch-up script reported no additional unsynced context. Four production files contain 105 insertions and 47 deletions, and four unit-test files plus `tests/conftest.py` already exist. The last recorded plan still says Phase 1 is in progress, but filesystem timestamps show that TDD tests were created and implementation edits followed; their correctness and prior RED/GREEN evidence have not yet been audited.

### Current Status

- Completed: planning, source/paper audit, isolated worktree setup, and context recovery.
- In progress: audit the interrupted TDD/implementation changes and reproduce their test state.
- Pending: remaining CPU coverage and implementation, GPU preparation, real tool-chain validation, baseline/TVCache RL smoke, review, and completion.

### Interrupted TDD Audit

- Motivation: determine whether the uncommitted edits are trustworthy TDD work or partial changes that must be redone.
- Expectation: tests predate implementation, each test maps to an approved root-cause issue, and no unrelated behavior was bundled.
- Method: inspected the complete production diff, all five test-support/test files, and their filesystem modification times.
- Result: four unit-test modules were written at 18:06 on 2026-08-14 and the four production files were modified at 18:12, consistent with test-first ordering. The tests cover cache/sandbox HTTP fail-fast behavior, configuration propagation, correct root-bank `env_id` use, and executor cache statistics. The current GREEN state and original RED output remain to be reproduced or reconstructed before accepting Phase 2.

### Targeted Test Attempt 1

- Motivation: reproduce the interrupted test state before accepting or changing any implementation.
- Expectation: the four unit-test modules execute and expose either behavior failures or a clean GREEN state.
- Method: ran `TMPDIR=/data/ycfeng/tmp python3 -m pytest -q tests/unit/test_async_tvcache_client_fail_fast.py tests/unit/test_sandbox_client_fail_fast.py tests/unit/test_simple_dict_bank_configuration.py tests/unit/test_async_executor_configuration.py` with `/usr/bin/python3` 3.12.3 and pytest 9.1.1.
- Result: **FAIL before behavior validation** — 5/5 tests failed because `pytest-asyncio` is not installed, with 5 matching `PytestUnknownMarkWarning` messages. No repository or parent-workspace `task_memory/env_handbook.md` exists, so there was no recorded environment recipe to apply. Root-cause investigation is in progress; no dependency guess or test workaround has been applied.

### Test Runner Dependency Root-Cause Fix

- Motivation: make the project-declared test environment capable of executing its async regression tests.
- Expectation: adding the same async pytest plugin used by the vendored Tinker cookbook will remove the collection/runtime failure without changing test logic.
- Method: compared all package manifests and async-test references; found that `train/tinker-cookbook/pyproject.toml` declares `pytest-asyncio`, while `tvcache/client/pyproject.toml` declares pytest alone. Added `pytest-asyncio` to the client `dev` dependency group; lock regeneration and validation are next.
- Result: `uv lock --project tvcache/client` resolved `pytest-asyncio==1.4.0`, proving the plugin declaration is valid. The next isolated test run progressed past the async-plugin failure but stopped during collection because `httpx` is imported by the client source and tests yet absent from the client runtime dependencies.

### Targeted Test Attempt 2

- Motivation: verify the test-runner dependency fix inside the client’s own isolated `uv` environment.
- Expectation: async tests collect and execute under project-declared dependencies.
- Method: ran `TMPDIR=/data/ycfeng/tmp uv run --project tvcache/client --group dev python -m pytest -q ...`; `uv` created `tvcache/client/.venv` with CPython 3.10.20 and 23 locked packages.
- Result: **FAIL during collection** — 4 test modules raised `ModuleNotFoundError: No module named 'httpx'`. This exposed a second, separate manifest defect: `async_tvcache_client.py` directly imports `httpx`, but `tvcache/client/pyproject.toml` listed only Flask and Requests. Added `httpx>=0.28.1`, matching the already working system version; lock regeneration and behavior validation are next.

### Targeted Test Attempt 3

- Motivation: validate both manifest fixes and the interrupted production changes in the isolated client environment.
- Expectation: all five regression tests execute and pass with no warnings.
- Method: regenerated `tvcache/client/uv.lock`, then reran the four targeted modules using `TMPDIR=/data/ycfeng/tmp uv run --project tvcache/client --group dev python -m pytest -q ...`.
- Result: **PASS — 5/5 tests passed in 0.25 s** under CPython 3.10.20 with `httpx==0.28.1` and `pytest-asyncio==1.4.0`; no warnings were emitted. Added the verified environment recipe to `task_memory/env_handbook.md`.

### Remaining CPU Gate Audit

- Motivation: turn the plan’s remaining acceptance criteria into focused RED tests before further production edits.
- Expectation: identify exact code boundaries for sandbox configuration/error propagation, exact/prefix reuse, server schema, and empty optimizer batches.
- Method: inspected the training main loop, `VideoSandboxEnv`, `VideoAgentLoop`, async client/server endpoints, and immutable prefix-tree methods; searched all training drivers for optimizer submission.
- Result: confirmed four remaining root causes: sandbox URL is hardcoded, two layers convert tool infrastructure errors into strings, all training variants can submit empty Tinker batches, and the old server test uses `value` instead of `values`/`tool_exec_times`. One broad symbol search exceeded the configured answer limit; it was replaced by narrower file-specific queries and caused no code or environment change.

### Context Recovery Continuation

- Motivation: continue the existing task from its recorded interruption point without repeating completed work or overwriting uncommitted changes.
- Expectation: confirm the active worktree, branch, dirty files, task gates, and next uncompleted action.
- Method: activated `.worktrees/tvcache-rl-reproduction`, ran the planning session catch-up script, inspected Git state, and reread all task records plus `task_memory/env_handbook.md`.
- Result: confirmed branch `task/tvcache-rl-reproduction` at `3a4f95a`, with the prior source, dependency, test, and task-record edits still present. No unsynced session data was found. The exact interruption point is the start of remaining RED coverage for sandbox propagation/error handling, deterministic exact/prefix cache reuse, current server schema, and empty optimizer batches.

### Resumed Source-State Confirmation

- Motivation: preserve the boundary between the already verified TDD changes and the remaining behavior that still needs RED coverage.
- Expectation: only the previously recorded six production/dependency files and five test-support/test files are present, with no hidden partial implementation of the remaining fixes.
- Method: inspected the full tracked diff, enumerated repository-level test files, and mapped the active training and server symbols.
- Result: the tracked diff remains limited to 188 insertions and 48 deletions across the six previously recorded files. The existing five tests cover only the first configuration, fail-fast HTTP, fork-bank, and statistics slice; no tests or production edits yet implement the remaining sandbox lifecycle, agent-loop propagation, server-schema integration, empty-batch handling, or deterministic exact/prefix integration gates.

### Remaining RED Boundaries

- Motivation: define minimal behavior tests before touching the remaining production paths.
- Expectation: each root cause has a concrete public boundary whose failure can be observed without GPU access.
- Method: read `VideoSandboxEnv`, `VideoAgentLoop`, the TVCache training `Config` and `main`, all three optimizer call sites, and located the actual immutable-tree module.
- Result: the RED boundaries are now explicit: `VideoSandboxEnv` must accept and preserve `sandbox_base_url`, propagate stop and malformed-result errors, and preserve that URL when forking; `VideoAgentLoop` must pass the sandbox and TVCache URLs into both executor and fork bank and must propagate executor failures; all three drivers need one tested update boundary that records and skips empty batches; the active tree is at `tvcache/server/tvcache/immutable_env_prefix_tree.py`, not the previously inferred path.

### CPU Test Design Refinement

- Motivation: ensure the next tests exercise supported behavior rather than implementation details.
- Expectation: cover runtime configuration and failure semantics with small unit tests, then cover cache/server behavior with real in-memory tree operations.
- Method: inspected the existing test fixtures, server `/put` and `/get` endpoints, and the complete immutable cache class.
- Result: planned tests will use a lightweight import fixture only for unavailable Tinker types; real `VideoSandboxEnv` methods will be exercised with a controlled sandbox client. Server tests will call the Flask application with the current `values` and `tool_exec_times` payload and explicitly stop the daemon cleanup thread. Exact-hit and partial-prefix tests will pair the real immutable cache with a deterministic `ToolCallEnv`, recording backend executions, forks, and cache statistics numerically.

### Video Sandbox URL RED

- Motivation: prove that the configured sandbox URL is currently lost before changing `VideoSandboxEnv`.
- Expectation: construction with `sandbox_base_url="http://sandbox.test:5000"` fails because the class exposes no such configuration boundary.
- Method: added `test_video_sandbox_env_uses_configured_base_url` and ran it alone in the locked TVCache client test environment.
- Result: **RED confirmed** — 0/1 passed; construction raised `TypeError: VideoSandboxEnv.__init__() got an unexpected keyword argument 'sandbox_base_url'` in 0.23 s.

### Video Sandbox URL GREEN

- Motivation: route the training-owned sandbox address into each TVCache environment instead of hardcoding localhost.
- Expectation: the environment constructs its `SandboxClient` with the caller-provided URL.
- Method: added the `sandbox_base_url` constructor argument with the existing localhost value as the explicit default and passed it directly to `SandboxClient`.
- Result: **GREEN confirmed** — the focused test passed 1/1 in 0.18 s.

### Forked Sandbox URL RED

- Motivation: prove that restored/forked environments retain the same sandbox service address as their parent.
- Expectation: the child currently falls back to localhost because `fork()` does not forward the configured URL.
- Method: added a focused asynchronous fork test using the real `VideoSandboxEnv` lifecycle and a controlled sandbox transport.
- Result: **RED confirmed** — 0/1 passed; the child URL was `http://localhost:5000` instead of `http://sandbox.test:5000` in 0.23 s.

### Forked Sandbox URL GREEN

- Motivation: keep one sandbox endpoint across newly created, restored, and forked environments.
- Expectation: `fork()` creates the child with its parent’s stored URL.
- Method: stored `sandbox_base_url` on `VideoSandboxEnv` and forwarded it when constructing the forked child.
- Result: **GREEN confirmed** — both sandbox URL tests passed 2/2 in 0.17 s.

### Sandbox Start Lifecycle RED

- Motivation: verify that a multi-tool rollout does not repeatedly start the same sandbox.
- Expectation: two sequential tool calls currently trigger two start requests because successful startup is not recorded.
- Method: added a real `VideoSandboxEnv.execute` test with a counting sandbox transport and two tool calls.
- Result: **RED confirmed** — 0/1 passed; observed start calls were 2, expected 1, in 0.22 s.

### Sandbox Start Lifecycle GREEN

- Motivation: make sandbox startup state reflect a successful server response.
- Expectation: subsequent tool calls reuse the already started environment.
- Method: set `started=True` immediately after `start_sandbox` completes successfully.
- Result: **GREEN confirmed** — all three `VideoSandboxEnv` tests passed 3/3 in 0.19 s.

### Malformed Sandbox Result RED

- Motivation: prove that a malformed sandbox response is currently converted into a synthetic tool value.
- Expectation: the missing required `result` key should raise at the sandbox boundary.
- Method: added a focused execute test whose controlled server response contains only an `error` field.
- Result: **RED confirmed** — 0/1 passed; a `KeyError('result')` occurred internally but was printed and replaced with a failure string, so the caller observed no exception; runtime was 0.27 s.

### Malformed Sandbox Result GREEN

- Motivation: fail immediately when the sandbox violates its response contract.
- Expectation: callers receive the original missing-key error instead of a plausible tool-result string.
- Method: removed the broad catch and synthetic return from `VideoSandboxEnv.execute`.
- Result: **GREEN confirmed** — all four sandbox tests passed 4/4 in 0.18 s.

### Sandbox Stop Failure RED

- Motivation: prove that teardown failure preserves the original infrastructure error.
- Expectation: `RuntimeError("sandbox stop failed")` should reach the caller.
- Method: added a focused stop test with a controlled transport that raises the expected error.
- Result: **RED confirmed** — 0/1 passed; the original error was swallowed and replaced by `UnboundLocalError: local variable 'result' referenced before assignment` in 0.23 s.

### Sandbox Stop Failure GREEN

- Motivation: expose teardown failures at their source instead of masking them with a secondary local-variable error.
- Expectation: `stop()` returns normally on success and propagates the original exception on failure.
- Method: removed the broad catch from `VideoSandboxEnv.stop` and awaited the sandbox client directly.
- Result: **GREEN confirmed** — all five sandbox tests passed 5/5 in 0.22 s.

### Agent-Loop Sandbox Propagation RED

- Motivation: prove that the training-owned sandbox URL reaches both direct and fork-bank environments.
- Expectation: executor and bank construction currently omit `env_kwargs`.
- Method: added a constructor-level behavior test with recording executor and fork-bank boundaries.
- Result: **RED confirmed** — 0/1 passed; executor configuration had no `env_kwargs` entry and raised `KeyError` in 0.23 s.

### Agent-Loop Sandbox Propagation GREEN

- Motivation: keep direct, restored, and warmed environments on the same configured sandbox service.
- Expectation: both executor and fork bank receive identical `sandbox_base_url` environment arguments.
- Method: created one `env_kwargs` mapping in `VideoAgentLoop.__init__` and passed it into both components.
- Result: **GREEN confirmed** — all six loop/environment tests passed 6/6 in 0.18 s.

### Agent-Loop TVCache URL RED

- Motivation: prove that the cache endpoint can be owned by training configuration rather than an implicit client default.
- Expectation: `VideoAgentLoop` currently rejects an explicit TVCache URL.
- Method: added a constructor-level test that supplies `http://cache.test:8001` and inspects both cache-using components.
- Result: **RED confirmed** — 0/1 passed; construction raised `TypeError` for the unexpected `tvcache_base_url` argument in 0.24 s.

### Agent-Loop TVCache URL GREEN

- Motivation: use one explicit cache endpoint for executor lookups and fork-bank warmup.
- Expectation: both components receive the training-provided URL.
- Method: added `tvcache_base_url` to `VideoAgentLoop` and forwarded it to `AsyncSemanticStatefulExecutor` and `SimpleDictBank`.
- Result: **GREEN confirmed** — all seven loop/environment tests passed 7/7 in 0.18 s.

### Agent Tool-Failure Propagation RED

- Motivation: prove that executor infrastructure failures are currently turned into model-visible synthetic tool messages.
- Expectation: a `RuntimeError("tool backend failed")` should abort the rollout.
- Method: drove one real `VideoAgentLoop.run` turn with controlled sampler/renderer boundaries and an executor that raises.
- Result: **RED confirmed** — 0/1 passed; the rollout completed without raising because the broad action handler swallowed the error; runtime was 0.23 s.

### Agent Tool-Failure Propagation GREEN

- Motivation: keep infrastructure failure distinct from valid tool output and reward data.
- Expectation: executor errors abort the rollout with their original type and message.
- Method: removed the broad action-level exception conversion while preserving normal tool-result formatting.
- Result: **GREEN confirmed** — all eight loop/environment tests passed 8/8 in 0.18 s.

### Current Server Schema Integration Gate

- Motivation: replace the print-only stale-schema signal with an assertion-based server contract test.
- Expectation: `/put` accepts `values`, `tool_exec_times`, and `start_idx`; `/get` returns the stored final value and execution time; any HTTP 500 fails the test.
- Method: added a Flask integration test under `tests/integration/` using the real server and immutable cache, with explicit cleanup-thread teardown.
- Result: **PASS — 1/1 in 0.17 s**. `/put` returned HTTP 200 with zero removed environments; `/get` returned HTTP 200, `env_id="environment-1"`, value `"answer"`, and tool execution time `0.25` s.

### Deterministic Exact/Prefix Reuse Gate

- Motivation: validate executor and immutable-cache semantics independently of model sampling and GPU tools.
- Expectation: the first call executes one backend tool, the same exact chain executes zero additional tools, and a longer chain reuses the cached prefix and executes only its one-call suffix.
- Method: added an integration test pairing the real `AsyncSemanticStatefulExecutor` and `ImmutableEnvPrefixTreeCache` with a deterministic stateful environment and an asynchronous in-memory cache adapter.
- Result: **PASS — 1/1 in 0.18 s**. Backend execution counts were first=1, after exact hit=1, after partial-prefix extension=2; the exact executor recorded exact hits=1 and tool executions=0; the prefix executor recorded prefix hits=1 and tool executions=1. The cache cleanup thread stopped within the 1 s join limit and was not alive afterward.

### Empty Optimizer Batch RED

- Motivation: prove that zero-variance smoke rollouts have no safe, observable update boundary.
- Expectation: a shared training-update function is absent before implementation.
- Method: added a behavior test that requires an empty batch to skip both Tinker calls and record numeric datum/skip metrics.
- Result: **RED confirmed** — 0/1 passed in 0.05 s because `train/utils/training_update.py` does not exist.

### Empty Optimizer Batch GREEN

- Motivation: make zero-advantage filtering an explicit valid outcome rather than an invalid Tinker request.
- Expectation: zero datums produce no client calls and numeric skip metrics.
- Method: added the shared update boundary with an empty-batch branch that records `optim/training_datums=0.0` and `optim/skipped_empty_batch=1.0`.
- Result: **GREEN confirmed** — the focused empty-batch test passed 1/1 in 0.01 s with zero forward/backward and optimizer calls.

### Nonempty Optimizer Update RED

- Motivation: preserve the existing valid Tinker update behavior behind the new empty-batch gate.
- Expectation: one datum submits one forward/backward request and one optimizer request.
- Method: added a behavior test with a recording client and completed asynchronous result handles.
- Result: **RED confirmed** — 0/1 passed in 0.05 s because the intentionally minimal first implementation raised `NotImplementedError` for nonempty input.

### Training Update Boundary GREEN

- Motivation: support both valid nonempty updates and explicit empty-batch skips through one tested path.
- Expectation: one datum produces one forward/backward and one optimizer call; zero datums produce neither.
- Method: implemented the nonempty branch with the existing asynchronous submission order and numeric metrics.
- Result: **GREEN confirmed** — 2/2 tests passed in 0.02 s. Observed calls were empty batch: forward=0, optimizer=0; one-datum batch: forward=1, optimizer=1.

### Training Driver Update Wiring RED

- Motivation: prove that every required baseline/cache variant uses the tested empty-batch gate.
- Expectation: all three drivers still call Tinker directly.
- Method: added a parameterized AST wiring test that rejects direct optimizer methods and requires exactly one shared update call per driver.
- Result: **RED confirmed** — 0/3 passed in 0.08 s; each driver contained exactly two direct calls (`forward_backward_async` and `optim_step_async`).

### Training Driver Update Wiring GREEN

- Motivation: prevent any rollout variant from bypassing the zero-datum guard.
- Expectation: no driver directly submits Tinker updates; each calls the shared boundary once.
- Method: imported and called `apply_training_update` in the no-cache, stateless-cache, and TVCache drivers.
- Result: **GREEN confirmed** — all five update tests passed 5/5 in 0.03 s, including 3/3 driver wiring checks.

### Approved Model/Renderer RED

- Motivation: prove that baseline and TVCache variants still use the retired model and implicit renderer selection.
- Expectation: all three driver configurations differ from the approved replacement.
- Method: added a parameterized AST configuration test for the exact model, non-thinking renderer, and explicit renderer use.
- Result: **RED confirmed** — 0/3 passed in 0.07 s; every driver defaulted to `Qwen/Qwen3-30B-A3B-Instruct-2507` instead of `Qwen/Qwen3.6-35B-A3B`.

### Approved Model/Renderer GREEN

- Motivation: keep the no-cache and TVCache smoke runs on the same available model and explicitly disable thinking.
- Expectation: all drivers use `Qwen/Qwen3.6-35B-A3B` with `qwen3_disable_thinking`.
- Method: updated all three configuration defaults and replaced automatic renderer inference with `config.renderer_name`.
- Result: **GREEN confirmed** — all three model/renderer checks passed 3/3 in 0.03 s.

### Training-Owned TVCache URL RED

- Motivation: prove that the training configuration still cannot select the cache service endpoint.
- Expectation: the TVCache driver lacks `tvcache_base_url`.
- Method: added an AST configuration-and-wiring test for the explicit port-8001 URL.
- Result: **RED confirmed** — 0/1 passed in 0.05 s with `KeyError: 'tvcache_base_url'`.

### Training-Owned TVCache URL GREEN

- Motivation: align training, executor, fork bank, and server on one explicit cache address.
- Expectation: the TVCache driver defaults to port 8001 and forwards the field to every agent loop.
- Method: added `Config.tvcache_base_url` and the matching `VideoAgentLoop` keyword.
- Result: **GREEN confirmed** — all four training configuration tests passed 4/4 in 0.04 s.

### Training Dependency Source Map

- Motivation: prepare the required Tinker `0.24.1` environment without guessing transitive dependencies.
- Expectation: identify the package names and local editable projects used directly by the rollout surface.
- Method: inspected the training, cookbook, and client manifests plus direct training imports and the existing lock.
- Result: the root training project currently declares only `tinker>=0.6.3`; its lock pins Tinker `0.16.1`. The local package names are `tinker_cookbook` and `tvclient`, and the rollout source directly imports at least `chz`, `datasets`, `httpx`, `numpy`, `pydantic`, `torch`, Tinker, and both local packages. Exact manifest coverage will be verified before lock regeneration.

### Tinker SDK Pin RED

- Motivation: prove the training manifest does not yet meet the approved SDK version.
- Expectation: exact `0.24.1` is absent and a broad old constraint remains.
- Method: added a focused manifest test for the required exact pin.
- Result: **RED confirmed** — 0/1 passed in 0.05 s; the manifest contained `tinker>=0.6.3`.

### Tinker SDK Pin GREEN

- Motivation: make the training API surface reproducible against the user-approved SDK.
- Expectation: the manifest contains only the exact `tinker==0.24.1` requirement.
- Method: replaced the broad Tinker constraint with the exact pin.
- Result: **GREEN confirmed** — the focused pin test passed 1/1 in 0.01 s.

### Rollout Dependency Declaration RED

- Motivation: prove that a fresh training environment cannot yet import the native rollout stack from declared dependencies.
- Expectation: direct third-party and local editable requirements are absent.
- Method: added a manifest test for seven direct packages and both local source mappings.
- Result: **RED confirmed** — 0/1 passed in 0.05 s; the first missing direct dependency was `chz`.

### Rollout Dependency Declaration GREEN

- Motivation: make the training environment self-describing instead of depending on undeclared workspace state.
- Expectation: all direct rollout imports and both local packages are declared.
- Method: added seven direct requirements plus editable `tinker-cookbook` and `tvclient` source mappings.
- Result: **GREEN confirmed** — the manifest test passed 1/1 in 0.01 s.

### Training Lock Attempt 1

- Motivation: resolve the updated manifest and prove Tinker `0.24.1` compatibility.
- Expectation: `uv lock --project train` completes and updates the lock deterministically.
- Method: ran the resolver with `TMPDIR=/data/ycfeng/tmp` and CPython 3.12.3.
- Result: **FAIL** — after more than five minutes the process had emitted no resolver progress beyond interpreter selection and remained at 0.5% CPU; it was interrupted. No fallback or version change was applied. Package-index connectivity is being diagnosed before a different retry.

### Training Lock Root-Cause Diagnostic

- Motivation: distinguish network failure, unavailable Tinker version, and dependency-resolution cost.
- Expectation: a bounded verbose run identifies the exact slow stage.
- Method: verified PyPI directly, confirmed HTTP 200 in 1.547 s, then ran a 60 s verbose resolver diagnostic with a 20 s HTTP timeout.
- Result: PyPI connectivity is healthy and `tinker==0.24.1` was selected successfully. The resolver timed out while expanding the cookbook’s large dependency graph across Linux, macOS, Windows, x86_64, and arm64 variants, including unrelated recipe dependencies. The next attempt will constrain the lock to the required H800 deployment platform (Linux x86_64), addressing the observed root cause without changing package versions.

### GPU-Worker Lock Target RED

- Motivation: encode the actual deployment platform and prevent irrelevant cross-platform resolution.
- Expectation: the training manifest has no environment constraint.
- Method: added a manifest test for Linux x86_64. The first test string had an escaping syntax error, which was corrected before the behavioral run.
- Result: **RED confirmed** — 0/1 passed in 0.05 s because the environment marker is absent.

### GPU-Worker Lock Target GREEN

- Motivation: restrict dependency resolution to the actual single-node H800 worker platform.
- Expectation: the manifest targets Linux x86_64.
- Method: added the `tool.uv.environments` marker for `sys_platform == 'linux' and platform_machine == 'x86_64'`.
- Result: **GREEN confirmed** — the focused platform test passed 1/1 in 0.01 s.

### Training Lock Attempt 3

- Motivation: generate the reproducible training lock after correcting the resolver scope.
- Expectation: the resolver selects Tinker `0.24.1`, both local editable packages, and a Linux x86_64 graph.
- Method: ran `uv lock --project train` with a 600 s bound, `TMPDIR=/data/ycfeng/tmp`, and a 30 s HTTP timeout.
- Result: **PASS** — 158 packages resolved in 6 min 09 s. Tinker changed from `0.16.1` to `0.24.1`; `tinker-cookbook==0.1.0` and `tvclient==0.1.0` were added from their local paths.

### Baseline Loop Fail-Fast RED

- Motivation: ensure the required no-cache baseline and optional stateless comparison do not hide sandbox outages.
- Expectation: both loops currently convert a raised sandbox error into a tool string.
- Method: added one parameterized real-loop test with controlled sampler/renderer input and a sandbox client that raises `RuntimeError("sandbox backend failed")`.
- Result: **RED confirmed** — 0/2 passed in 0.12 s; neither loop propagated the error.

### Baseline Loop Fail-Fast GREEN

- Motivation: stop invalid rollout/reward generation when the sandbox infrastructure fails.
- Expectation: the no-cache and stateless loops preserve the original exception.
- Method: removed both broad action-level exception conversions while retaining successful cache/tool formatting.
- Result: **GREEN confirmed** — both parameterized loop tests passed 2/2 in 0.05 s.

### Baseline Malformed-Result RED

- Motivation: ensure a malformed HTTP 200 payload is not presented to the model as a valid failure message.
- Expectation: both loops currently synthesize a string when the required `result` key is absent.
- Method: refactored shared test setup and added a parameterized malformed-response behavior test.
- Result: **RED confirmed** — 0/2 passed in 0.09 s; neither loop raised `KeyError('result')`.

### Baseline Malformed-Result GREEN

- Motivation: enforce the sandbox response contract consistently across rollout variants.
- Expectation: missing `result` raises immediately; valid values retain the existing message format.
- Method: replaced conditional synthetic failures with required-key access and cached only validated values.
- Result: **GREEN confirmed** — all four baseline/stateless fail-fast tests passed 4/4 in 0.06 s.

### Fork-Bank Root Materialization RED

- Motivation: ensure a warmed root ID refers to a sandbox that actually exists on the backend.
- Expectation: `SimpleDictBank` currently stores a lazy constructor ID without creating the environment.
- Method: strengthened the fork-bank test to require a real forked root while preserving environment configuration.
- Result: **RED confirmed** — 0/1 passed in 0.28 s; only the unmaterialized `task-1-root` object was created and no `task-1-root-fork` existed.

### Fork-Bank Root Materialization GREEN

- Motivation: prevent the first cache miss from restoring an ID absent from the sandbox service.
- Expectation: warmup creates a real fork, stores its ID, and stops the temporary parent.
- Method: changed root deposit to await `fork()`, retain the child ID, and tear down the parent before publishing the bank entry.
- Result: **GREEN confirmed** — the configured fork-bank test passed 1/1 in 0.17 s and returned `task-1-root-fork`.

### Driver Teardown Failure RED

- Motivation: prevent leaked sandbox state from being hidden after rollout completion.
- Expectation: all three drivers swallow `stop_sandbox` failures.
- Method: added a parameterized wiring test that rejects handled teardown calls.
- Result: **RED confirmed** — 0/3 passed in 0.10 s; every driver contained one broad teardown handler.

### Driver Teardown Failure GREEN

- Motivation: make cleanup state trustworthy and visible in smoke-test evidence.
- Expectation: any sandbox teardown failure aborts instead of printing and continuing.
- Method: removed the three broad teardown handlers and awaited each loop directly.
- Result: **GREEN confirmed** — all ten training configuration/wiring tests passed 10/10 in 0.06 s.

### Required EgoSchema Directory RED

- Motivation: replace the sandbox’s committed placeholder path with explicit runtime configuration.
- Expectation: no isolated configuration boundary exists.
- Method: added a behavior test requiring a clear error when `EGOSCHEMA_VIDEO_DIR` is unset.
- Result: **RED confirmed** — 0/1 passed in 0.05 s because `video-agent-tools/VideoAgent/runtime_config.py` does not exist.

### Required EgoSchema Directory GREEN

- Motivation: fail at startup when the required external video source is not configured.
- Expectation: an unset or blank variable raises a named runtime error.
- Method: added `resolve_required_directory` with explicit environment lookup and no default.
- Result: **GREEN confirmed** — the missing-variable test passed 1/1 in 0.01 s.

### EgoSchema Directory Validation RED

- Motivation: reject configured files or missing paths before the first rollout.
- Expectation: the minimal environment lookup currently accepts a regular file.
- Method: pointed `EGOSCHEMA_VIDEO_DIR` at the existing training manifest and required `NotADirectoryError`.
- Result: **RED confirmed** — 0/1 passed in 0.05 s because no directory check ran.

### EgoSchema Directory Validation GREEN

- Motivation: surface invalid external assets during service startup.
- Expectation: only an existing directory is returned.
- Method: added `Path.is_dir()` validation and returned the resolved path.
- Result: **GREEN confirmed** — both runtime configuration tests passed 2/2 in 0.01 s.

### Sandbox Video-Directory Wiring RED

- Motivation: prove the validated configuration is not yet used by the sandbox manager.
- Expectation: the literal placeholder remains in the loader.
- Method: added a wiring test that rejects the placeholder and requires constructor-owned path use.
- Result: **RED confirmed** — 0/1 passed in 0.05 s; `path/to/train/EgoSchema/videos` remained in `sandbox_manager.py`.

### Sandbox Video-Directory Wiring GREEN

- Motivation: make video assets explicit and validate them before expensive component initialization.
- Expectation: `SandboxManager` owns the resolved directory and the loader uses it.
- Method: resolved `EGOSCHEMA_VIDEO_DIR` at the start of construction and replaced the literal source prefix.
- Result: **GREEN confirmed** — all three runtime configuration/wiring tests passed 3/3 in 0.01 s.

### Full CPU Gate and Phase Archive

- Motivation: establish fresh evidence for the complete CPU implementation before allocating GPUs.
- Expectation: every repository-level unit and integration test passes in the declared client development environment with no collection errors or warnings.
- Method: ran `TMPDIR=/data/ycfeng/tmp UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache uv run --project tvcache/client --group dev python -m pytest -q tests/unit tests/integration` and separately printed the interpreter and pytest versions from the same environment.
- Result: **PASS — 37/37 tests passed, 0 failed, in 0.32 s** with Python 3.10.20 and pytest 8.4.2. Phase 2 (TDD regression coverage) and Phase 3 (root-cause implementation) are complete. Detailed evidence is stored in `test_report_2026-08-16_cpu_gates.md`.

### Current Status After CPU Gate

- Completed: Phases 1–3, including planning/source audit, isolated setup, RED/GREEN coverage, root-cause implementation, dependency locks, and the full CPU gate.
- In progress: pre-GPU code review and GPU handbook/environment preparation.
- Pending: real tool-chain validation, matched no-cache/TVCache RL smoke runs, final review, final test report, summary, and branch consolidation.

### GPU Handbook and Host Check

- Motivation: follow the platform-authoritative launch recipe before any GPU allocation.
- Expectation: confirm the required quota/tag combination, predict-first rule, control path, and whether the current host already exposes GPUs.
- Method: read `/data/ycfeng/stepfun-env-handbook/guidence.md`, checked `nvidia-smi -L`, and located `rlaunch`.
- Result: the required single-node combination remains `--charged-group=codesign --private-machine=group --positive-tags=h800 --backoff-limit=1`; allocation must be preceded by `--predict-only`. `nvidia-smi -L` returned exit code 0 with 0 GPU device lines, so this is still a CPU master. The verified launcher is `/kubebrain/rlaunch`; worker control should use `brainctl exec`, not an assumed SSH path.

### Local GPU-Environment Preflight

- Motivation: identify external inputs and existing environments before requesting an H800 worker.
- Expectation: determine whether credentials, prepared environments, and documented launch inputs are already available without exposing any secret values.
- Method: checked only whether `TINKER_API_KEY`, `OPENAI_API_KEY`, and `HF_TOKEN` are nonempty; enumerated project-local virtual environments and relevant launch/configuration files.
- Result: all three credential variables are currently unset, and the only project-local environment is `tvcache/client/.venv`; the four GPU service/training environments still need preparation. `train/integration.md` describes the integration API but not a complete current GPU launch recipe. A read-only optional-file loop exited 1 because its final unmatched requirements-file probe supplied the command status; no source or environment was changed.

### GPU Asset Preflight

- Motivation: distinguish environment setup from external model/video downloads before worker allocation.
- Expectation: locate the repository-specific Video-LLaVA weights, socket directory, reusable EgoSchema preprocessing cache, and actual EgoSchema videos if already present.
- Method: inspected the service entry point and manager preprocessing path, then checked the expected worktree directories and dataset contents.
- Result: all required runtime asset directories are absent in the worktree; only 5.3 MiB of EgoSchema metadata/scripts exists. Video-LLaVA expects 4-bit weights under `VideoAgent/cache_dir`, while the sandbox optionally reuses `VideoAgent/egoschema_cache` and otherwise runs the complete GPU preprocessing pipeline. Asset acquisition remains part of Phase 4.

### External Model Archive Sizing

- Motivation: avoid starting large downloads without knowing their storage cost.
- Expectation: obtain authoritative compressed sizes and confirm shared storage can hold the downloads.
- Method: queried Zenodo record `11031717` through its API and checked `/data` capacity.
- Result: the two required archives total 27,851,826,841 compressed bytes (12,435,543,255-byte tool models plus 15,416,283,586-byte Video-LLaVA cache). `/data` has 136 GiB available. Existing copies and uncompressed size must be checked before extraction to avoid duplicating tens of gigabytes.

### Independent Architecture Review BLOCK

- Motivation: independently test whether the green CPU suite is sufficient to enter the costly GPU stage.
- Expectation: either obtain a supported architecture clearance or identify concrete lifecycle/configuration gaps before allocation.
- Method: `/root/cpu_arch_review` inspected the complete tracked/untracked implementation, tests, requirements, design, harness, and full runtime entry paths without editing files.
- Result: **BLOCK**. Seven CPU-reproducible gaps remain: fail-fast exceptions bypass rollout cleanup; Config cannot select one fixed question; rollout directories are absent and baseline/TVCache logs collide; `unref`/`get_all_envs` still silently degrade; empty sandbox fork/stop conflicts with `SandboxManager`; sandbox internals retain synthetic fallbacks and an unsafe VQA lock; required per-rollout numeric cache/token/fork metrics are not connected to driver output. Phase 2 and Phase 3 were reopened and GPU work was paused.

### Rework Status

- Completed: independent architecture root-cause review and evidence capture.
- In progress: systematic root-cause tracing and RED tests for the seven blockers.
- Pending: minimal GREEN fixes, fresh full CPU gate, repeated independent review, then Phase 4.

### Structured Cleanup Root-Cause Trace

- Motivation: verify the architecture finding directly before designing a fix.
- Expectation: identify the exact ownership boundary where rollout tasks, started sandboxes, and teardown should be joined.
- Method: read the complete `main` functions for the no-cache and TVCache drivers and traced each loop from construction through start, `asyncio.gather`, result processing, and stop.
- Result: both drivers start every sandbox before creating rollout coroutines, await one bare `asyncio.gather`, and perform stop calls only afterward. A start failure, rollout failure, cancellation, or first stop failure therefore bypasses cleanup for some or all created loops. The root cause is duplicated unstructured lifecycle ownership in each driver, not the fail-fast behavior itself.

### Rework Hypotheses

1. A shared rollout execution boundary that owns start, task creation, sibling cancellation/waiting, ordered results, and all-loop cleanup will remove the lifecycle leak without weakening fail-fast behavior.
2. Explicit `dataset_start` and `dataset_count` configuration applied before shuffle will make the one-question smoke deterministic while preserving the existing 100-item default.
3. Passing a run-specific rollout directory derived from `config.log_path` will prevent first-write failure and baseline/TVCache collisions.
4. Propagating cache lifecycle status failures and modeling unloaded sandboxes as a valid state will fix bank warmup at the actual client/service boundary.
5. Collecting per-loop stats after each result and persisting them under the run log path will satisfy the numeric evidence requirement without parsing free-form logs.

### Independent Code Review REQUEST CHANGES

- Motivation: obtain an independent code/spec/security decision in addition to the architecture lane.
- Expectation: confirm or refute the architecture blockers and identify concrete implementation-level omissions.
- Method: `/root/cpu_code_review` reviewed 28 files (15 tracked modifications, 11 tests, and 2 new source files) against the task requirements without editing or rerunning tests.
- Result: **REQUEST CHANGES — 0 CRITICAL, 8 HIGH, 2 MEDIUM**. The HIGH findings confirm the architecture blockers and add the CUDA 13 training lock risk plus incomplete `get_test_result` fail-fast coverage. MEDIUM findings identify an unclosed fork-bank HTTP client and import/startup cwd side effects. No real credential was found in tracked changes.

### Structured Rollout Cancellation RED

- Motivation: prove one failing rollout currently leaves a sibling task running and all started loop cleanup outside the failure path.
- Expectation: a shared execution boundary cancels and awaits the waiting sibling, then calls stop once for both loops while preserving the original rollout error.
- Method: added `test_rollout_execution.py` with one immediately failing loop and one indefinitely waiting loop; introduced only a `NotImplementedError` boundary before the behavioral RED run.
- Result: **RED confirmed — 0/1 passed in 0.05 s**. The expected `RuntimeError("rollout failed")` was replaced by `NotImplementedError`, proving the required boundary was absent.

### Structured Rollout Cancellation GREEN

- Motivation: give all three drivers one lifecycle owner that preserves fail-fast behavior without leaking siblings or started sandboxes.
- Expectation: all tasks are joined, pending siblings are cancelled/awaited, and every successfully started loop is stopped.
- Method: implemented start tracking, task creation, failure cancellation/waiting, and unconditional cleanup in `run_agent_loops`. The first GREEN attempt exposed an indentation defect that recorded only the final loop; corrected the source-level root cause and reran the focused test.
- Result: **GREEN confirmed — 1/1 passed in 0.01 s**. The original rollout error propagated, the waiting sibling observed cancellation, and both loops recorded exactly one stop call.

### Cleanup Error Aggregation RED/GREEN

- Motivation: prevent the first stop failure from hiding the rollout error or skipping cleanup of later loops.
- Expectation: all started loops receive one stop attempt and a combined exception preserves the primary rollout error plus every cleanup failure.
- Method: added a second lifecycle test with one rollout failure and one failing stop; then introduced `RolloutLifecycleError`, collected cleanup errors after all stop attempts, and chained the combined error from the primary failure.
- Result: **RED — 1/2 passed** because `cleanup failed` replaced the rollout error and skipped later cleanup. **GREEN — 2/2 passed in 0.02 s**; both stops ran and the chained error reported one cleanup failure alongside `rollout failed`.

### Driver Structured-Lifecycle Wiring RED/GREEN

- Motivation: ensure none of the three training entry points bypasses the tested lifecycle owner.
- Expectation: each driver calls `run_agent_loops` exactly once and contains no direct `gather`, `start_sandbox`, or `stop_sandbox` call.
- Method: added a parameterized AST gate, observed all three drivers fail, then flattened their loop groups into ordered loop/ID lists and delegated execution to the shared boundary.
- Result: **RED — 0/3 passed in 0.09 s**; all drivers lacked the shared call. **GREEN — 6/6 relevant wiring/teardown checks passed in 0.05 s** across no-cache, stateless-cache, and TVCache variants.

### TVCache Internal Resource Cleanup RED/GREEN

- Motivation: close the executor and cancel/await warmup deposits even when a tool call fails.
- Expectation: the original tool error propagates, the executor is closed, and a started warmup task observes cancellation before `run()` returns.
- Method: strengthened the real loop failure test, wrapped `_run` with explicit primary/cleanup error handling, moved warmup tasks to owned state, cancelled/awaited them on failure, and closed the executor on every path.
- Result: **RED — executor initially remained open; after its first fix, the warmup task remained live**. The first cancellation assertion required one deliberate sampler yield so the test task entered its coroutine. **GREEN — all 8 TVCache loop tests passed in 0.21 s**; executor close and warmup cancellation are both observed while the original tool error remains visible.

### Fixed Dataset Slice RED/GREEN

- Motivation: make the required one-question smoke an explicit, shared configuration rather than an accidental batch-size effect.
- Expectation: a validated selector returns exactly the requested range without mutating the source, and every driver applies `dataset_start`/`dataset_count` before shuffle.
- Method: added four behavior tests for valid and invalid ranges plus a three-driver AST wiring gate; implemented `select_dataset_slice`, added defaults `start=0` and `count=100`, and passed both values into dataset loading.
- Result: selector **RED — 0/4 passed**, then **GREEN — 4/4 passed in 0.01 s**. Driver wiring **RED — 0/3 passed**, then the combined dataset gates passed **7/7 in 0.04 s**. A smoke override of `dataset_start=0`, `dataset_count=1`, `batch_size=1`, `group_size=2`, and `epochs=1` now expresses exactly one fixed question with two rollouts.

### Run-Specific Rollout Logging RED/GREEN

- Motivation: prevent first-write `FileNotFoundError` and baseline/TVCache evidence collision.
- Expectation: each loop creates and uses a caller-provided directory, TVCache passes the same directory into its executor, and every driver derives the directory from its own `config.log_path`.
- Method: added behavior tests for the baseline, stateless, and TVCache loops plus a three-driver AST wiring test; introduced `rollout_log_dir`, created it at start, configured the executor file handler with it, and passed `os.path.join(config.log_path, "rollouts")` from each driver.
- Result: loop tests **RED — 0/2 baseline/stateless and 0/1 TVCache passed** due rejected configuration. Driver wiring **RED — 0/3 passed**. After the root-cause changes, **3/3 loop path tests** and **3/3 driver wiring tests** passed; log files are isolated under each run's configured path.

### Metrics Rework Context Recovery

- Motivation: resume the interrupted CPU blocker remediation without repeating completed work or weakening the closed GPU gate.
- Expectation: recover the exact test failure, current source state, and remaining review findings from the existing task records and worktree.
- Method: reread `requirements.md`, `plan.md`, `harness.md`, `progress.md`, `issues.md`, `review.md`, `notes.md`, `findings.md`, `design.md`, `summary.md`, and `future.md`; inspected Git state and the metrics tests/source; reran the recorded focused test in the locked client environment.
- Result: branch `task/tvcache-rl-reproduction` and all uncommitted work were intact. The focused test reproduced **2/2 failures** because baseline `VideoAgentLoop` and stateless `CachedVideoAgentLoop` lacked `get_stats()`; GPU preparation remains paused.

### Baseline/Stateless Numeric Statistics RED/GREEN

- Motivation: give all rollout variants the same structured cache/tool statistics contract required by `rollout_metrics.jsonl`.
- Expectation: one successful baseline tool call reports one total call, one miss, and one backend execution; stateless cache additionally reports one cache put, while unsupported hit/fork categories remain numeric zero.
- Method: strengthened the existing focused test with the complete expected dictionary, confirmed the two missing-method failures, then added per-loop counters, action-path updates, and copy-returning `get_stats()` methods.
- Result: **RED — 0/2 passed** with `AttributeError` for both loop classes. **GREEN — 2/2 passed, 6 deselected, in 0.05 s**; baseline reported `cache_puts=0`, stateless reported `cache_puts=1`, and both exposed all seven required numeric fields.

### Per-Rollout Metrics Persistence RED/GREEN

- Motivation: connect the existing structured result/statistics helpers to real driver output with stable sample and rollout identity.
- Expectation: each driver preserves the source `dataset_index` and `video_id`, builds one numeric record per rollout, and appends the records under its run-specific `config.log_path`.
- Method: traced data from `processed_videos.json` through slicing, shuffling, grouped rollout execution, and result regrouping; added six AST behavior gates; preserved both identity fields during dataset construction; retained each result's matching loop and sandbox ID; called `build_rollout_record()` and `write_rollout_records()` in all three drivers.
- Result: **RED — 0/6 passed** because all drivers discarded both identity fields and made zero metrics helper calls. **GREEN — 8/8 passed, 22 deselected, in 0.08 s**, including the six driver gates and both JSON record/persistence tests. Variants are recorded as `no_cache`, `stateless_cache`, and `tvcache`.

### Cache Lifecycle Client Fail-Fast RED/GREEN

- Motivation: prevent cache service outages or malformed lifecycle responses from becoming valid misses, empty environment sets, or unsuccessful booleans.
- Expectation: `get_test_result`, `unref`, and `get_all_envs` propagate HTTP status failures and require their documented response fields.
- Method: added three HTTP-500 tests and three HTTP-200 malformed-schema tests; removed the three broad `httpx.HTTPError` conversions and replaced response defaults with required-key access while retaining optional `test_result` for a legitimate not-found response.
- Result: HTTP tests **RED — 0/3 passed**, and schema tests **RED — 0/3 passed**. The complete client fail-fast module is now **GREEN — 8/8 passed in 0.07 s**. Active fork-bank cleanup propagation and resource ownership remain under test before I-016 is closed.

### Fork-Bank Lifecycle and Metrics RED/GREEN

- Motivation: prevent partial warmup deposits, failed withdrawals, and the bank-owned HTTP client from leaking resources; include proactive warmup forks in rollout evidence.
- Expectation: every temporary parent and unpublished fork is stopped after deposit failure, withdrawal attempts all forks after one stop error, the bank client closes on every rollout path, and bank fork counts are added to executor counts.
- Method: added five focused gates; made deposit publication transactional after fork creation and cache unreference; tracked and cleaned unpublished forks; stopped root parents in `finally`; added bank stats/close APIs; joined bank close in loop cleanup; combined bank/executor fork counts; collected withdrawal errors after all stop attempts; removed the import-time `FileHandler`.
- Result: initial focused run was **RED — 0/5 passed**; withdrawal/import-side-effect follow-up was **RED — 0/2 passed**. The complete bank plus TVCache-loop modules are now **GREEN — 15/15 passed in 0.21 s**. A successful one-fork warmup reports `environment_forks=1`, and a simulated second-fork failure leaves **2/2 parents and 1/1 created fork stopped**.

### SandboxManager Lifecycle and Fail-Fast RED/GREEN

- Motivation: make empty prewarmed sandboxes valid, prevent copied fork leaks, eliminate synthetic infrastructure answers, release the VQA lock after exceptions, and fail before GPU component startup when credentials are absent.
- Expectation: empty stop succeeds; fork toolkit failure propagates after deleting the copied sandbox; object-agent failure propagates; VQA lock is immediately reacquirable after failure; missing `OPENAI_API_KEY` initializes zero expensive components; prompt loading is module-relative and offline.
- Method: added a dependency-isolated behavior module plus runtime-config gates; made loaded-video cleanup optional; made fork creation transactional; removed the object-query catch/string conversion; replaced manual VQA acquire/release with a context manager; added required environment-value validation before component initialization; replaced constructor `hub.pull`/cwd pickle writes with the committed module-relative prompt asset.
- Result: **RED — 0/7 passed** with the seven expected lifecycle/configuration failures. The full SandboxManager/runtime-config focused suite is now **GREEN — 10/10 passed in 0.04 s**. The missing-key gate observed **0 component initializations**, and failed fork cleanup attempted **1/1 copied sandbox removal**.

### CPU-Only Training Lock Root-Cause Resolution

- Motivation: remove the lock's CUDA 13 runtime mismatch without coupling the remote Tinker driver to either H800 GPU.
- Expectation: active training code requires Torch only for CPU tensor construction, and the official CPU wheel yields a lock with no CUDA, NVIDIA, or Triton runtime packages.
- Method: searched active drivers/cookbook calls for CUDA device use; verified the official Python 3.12 x86_64 `torch==2.13.0+cpu` wheel; added two RED manifest/lock gates; pinned Torch to an explicit official CPU index; regenerated the Linux x86_64 lock in a 2 GiB user systemd scope; ran the focused gates and `uv lock --check`.
- Result: active rollout paths contain **0 CUDA calls**. Correct behavioral RED was **0/2 passed**; GREEN is **2/2 passed, 28 deselected, in 0.02 s**. Lock resolution completed with **139 packages**, removed **19 GPU-runtime packages**, selected `torch==2.13.0+cpu`, and the locked check resolved in **2 ms**.

### Training-Lock Diagnostic Errors

- Motivation: keep environment failures and their verified resolution auditable.
- Expectation: use only commands compatible with the host's Python and resource-control environment.
- Method: corrected each failed diagnostic before repeating the intended gate.
- Result: one broad read-only grep was interrupted after exceeding its useful scope; the first lock test used Python 3.11-only `tomllib` under Python 3.10 and was replaced by dependency-free lock assertions; `systemd-run --wait --scope` was rejected and the system scope required interactive authentication, while the verified `systemd-run --user --scope -p MemoryMax=2G` form succeeded. The verified recipe was added to `task_memory/env_handbook.md`.

### Fresh Full CPU Gate After Review Remediation

- Motivation: prove every CPU behavior together before requesting the two independent pre-GPU reviews.
- Expectation: all unit/integration tests, both locks, and the whitespace check pass with zero failures.
- Method: ran the complete repository-level suite in the locked client dev environment; corrected one stale test assertion that expected the formerly unpinned literal `"torch"`; removed one trailing whitespace line; reran the full suite, `git diff --check`, and both `uv lock --check` commands.
- Result: first full attempt was **88 passed, 1 failed in 0.61 s** due only to the stale test literal. Fresh final gate is **89 passed, 0 failed in 0.56 s** on Python **3.10.20** and pytest **8.4.2**. `git diff --check` emitted **0 findings**; training and client locks resolved **139** and **28** packages respectively with exit code 0. Phases 2 and 3 are complete; GPU remains paused pending two independent review verdicts.

### Context Recovery and v2 Review Reopen

- Motivation: resume the interrupted task from its recorded worktree and act on the fresh independent review evidence without repeating completed CPU work.
- Expectation: recover the exact branch, dirty state, task gates, and unresolved blockers; keep GPU preparation closed until both review lanes clear.
- Method: activated `.worktrees/tvcache-rl-reproduction`, reread the task requirements, plan, findings, notes, harness, design, issues, review context, and recent progress; inspected Git state; collected the completed architecture v2 verdict and the in-progress code-review v2 messages.
- Result: branch `task/tvcache-rl-reproduction` and all prior changes are intact. Architecture v2 is **BLOCK** because all three drivers lack `import asyncio`, loaded-only sandboxes fork before `captions.json` exists, and executor collision/`/put` cleanup is detached or incomplete. Code review v2 has independently confirmed the driver startup failure and identified a separate HIGH token/logprob alignment defect for the non-append `Qwen3DisableThinkingRenderer`; its final verdict is still pending. Phases 2 and 3 are reopened as **In Progress**, and Phase 4 remains **Pending**.

### v2 Blocker Root-Cause Trace

- Motivation: ground each new review finding in the active runtime path before changing tests or production code.
- Expectation: identify the exact ownership or state assumption that fails and separate independent defects into minimal TDD cycles.
- Method: inspected the active symbols for executor collision/cache publication, `SandboxManager.fork`/`preprocess`/`generate_toolkit`, and all three multi-turn loop implementations; compared them with the v2 review evidence.
- Result: the findings are source-confirmed. `_handle_removed_envs` catches every exception and calls async `stop()` through `asyncio.run` inside a detached thread; `_execute_and_put` and `execute` also start unjoined stop/removal threads. `_maybe_put_to_cache` receives a live fork, so a failed cache publication has no enclosing cleanup owner. `SandboxManager.fork` calls `generate_toolkit` whenever the sandbox directory is copied, although only `preprocess` creates the files required by `ToolKit`. Finally, all three loops overwrite `all_tokens` from the current renderer prompt while appending old logprobs using `prev_len`, which is valid only for append-only renderers and is incompatible with the configured non-append renderer.

### v2 Minimal-Fix Hypotheses

- Motivation: choose root-cause fixes that preserve current contracts and avoid broad refactoring.
- Expectation: each hypothesis has one observable failing behavior and one narrow ownership/state correction.
- Method: traced `ToolKit.__init__`, sandbox metadata, `_maybe_put_to_cache`, executor close behavior, and the current repository tests.
- Result: four bounded TDD lanes are sufficient. (1) Driver entry tests can prove every `asyncio.run` has a real module import. (2) `SandboxManager.toolkits` is the existing authoritative marker for completed preprocessing, so loaded-only forks must copy video metadata without generating a toolkit, while preprocessed forks regenerate one for the copied path. (3) `_maybe_put_to_cache` must own its unpublished fork until `/put` succeeds and await all evictions; removed-environment cleanup must be async and error-reporting rather than threaded. (4) Multi-turn alignment needs a shared helper whose contract rejects or correctly reconstructs non-prefix prompts; the exact implementation remains pending inspection of the official Tinker renderer/trajectory pattern.

### Official Tinker Rollout Pattern Lookup

- Motivation: resolve the non-append renderer defect from the repository's pinned official cookbook instead of inventing a token reconstruction scheme.
- Expectation: find the canonical transition/trajectory assembly that preserves sampled tokens, logprobs, and observations independently across turns.
- Method: read the applicable cookbook `AGENTS.md`, searched the RL implementation for `Trajectory`, `assemble_training_data`, and `sampled_logprobs`, and inspected the configured renderer contract.
- Result: the cookbook explicitly instructs RL code to collect `Trajectory` transitions and call `assemble_training_data`; `rl/data_processing.py` contains a `SequenceAccumulator` dedicated to joining per-transition observations/actions/logprobs. `Qwen3DisableThinkingRenderer` explicitly warns that observations do not grow by appending. A follow-up attempt to inspect renderer tests used a stale guide path and exited 2 after the useful source output; the actual test location must be discovered before continuing.

### Non-Append Renderer Root-Cause Resolution Design

- Motivation: determine the exact correct data shape before writing a regression test for I-025.
- Expectation: use the pinned cookbook's semantics so non-prefix observations produce valid training data rather than forcing one artificial sequence.
- Method: inspected `trajectory_to_data`, `Transition`, `Trajectory`, `do_single_rollout`, and the three drivers' current manual `Datum` assembly.
- Result: official Tinker behavior is explicit: each turn is a transition containing its own observation plus sampled action/logprobs; `trajectory_to_data` merges only when the next observation extends the previous sequence and otherwise emits a new `Datum`. The current loops instead force every turn into one token array, so a correct fix must preserve per-turn transitions (or equivalent segments) and allow one rollout to create multiple training datums. A length-only assertion cannot repair this defect.

### Code Review v2 Additional Findings

- Motivation: keep the issue register synchronized while the independent code-review lane finishes.
- Expectation: capture every source-grounded blocker before defining the RED test batch.
- Method: received the reviewer's line-level follow-up and compared it with the already traced client/executor ownership paths.
- Result: I-024 also includes client-close failure skipping environment stop, prefix ref/fork/execute failure leaks, and an unclosed executor `FileHandler`. New I-026 records that `exact_match`, `prefix_match`, and `put` accept malformed HTTP 200 payloads through default values. Both require failure-injection/schema RED tests; the final v2 code-review verdict is still pending.

### Independent Code Review v2 REQUEST CHANGES

- Motivation: close the second pre-GPU review lane with a complete auditable verdict.
- Expectation: enumerate all remaining correctness and launch-reliability gaps before implementation resumes.
- Method: `/root/cpu_code_review_v2` completed a read-only review of 36 implementation/test files and reported exact source lines, severity, test gaps, and minimum repair direction.
- Result: **REQUEST CHANGES — 0 CRITICAL, 5 HIGH, 3 MEDIUM**. In addition to I-022 through I-026, the review found unconditional five-attempt sampling retry (I-027), mutually non-exclusive prefix/miss metrics (I-028), residual sandbox reuse with repeatable IDs (I-029), and cwd/placeholder-key runtime configuration (I-030). No real credential was found. Both independent lanes now block Phase 4.

### First v2 RED Batch Design

- Motivation: turn the four independent high-severity correctness defects into focused behavior tests before production edits.
- Expectation: each test fails only because the reviewed behavior is currently wrong.
- Method: inspected existing test fixtures, active client methods, executor logger ownership, `sample_response`, rollout metrics, and Tinker's `TokensWithLogprobs` API; reviewed the test-mocking anti-pattern guidance.
- Result: existing fixtures can be extended without adding test-only production hooks. The entry gate will inspect/execute the real driver preamble; malformed HTTP tests will use complete endpoint-specific `MockTransport` payloads; sampling will assert one backend call on first failure; trajectory coverage will run two non-prefix real `ModelInput` observations and verify that official `trajectory_to_data` emits separate, token-aligned datums. Executor lifecycle remains a later failure-injection batch because it requires a complete resource-state test double rather than shallow call mocks.

### First v2 RED Batch

- Motivation: prove I-022, I-025, I-026, and I-027 with executable regressions before production changes.
- Expectation: all new cases fail for the exact reviewed behavior.
- Method: added parameterized driver import/trajectory gates, active-client malformed-schema tests, a two-turn non-append transition test for baseline/stateless loops, and a TVCache first-sampling-failure call-count test; ran only those nodes in the locked client dev environment.
- Result: **RED confirmed — 12 failed, 0 passed in 0.47 s**. The three imports and three trajectory calls were absent; exact/prefix/put accepted `{}`; both non-append loops hit the incorrect length assertion on turn 2; and TVCache called the failing sampler **5 times instead of 1**. Every failure matched its intended root cause.

### Driver Entry, Cache Schema, and Sampling GREEN

- Motivation: resolve three independent fail-fast defects without mixing them into the trajectory refactor.
- Expectation: every real driver has its required event-loop import, malformed active cache responses raise, and a failed remote sample is submitted exactly once.
- Method: imported `asyncio` in all drivers; replaced response defaults in `exact_match`/`prefix_match`/`put` with required fields and required successful publication; replaced the retry loop with one direct `sample_async` call.
- Result: **GREEN — 7/7 focused cases passed in 0.21 s**. The three entry gates, three malformed-schema cases, and sampling call-count/cleanup case all pass; the transition-aware tests remain intentionally RED pending the separate official-trajectory change.

### Transition-Aware Rollout RED

- Motivation: prove the full I-025 repair boundary, including all three loops, all three drivers, and numeric rollout evidence.
- Expectation: non-append observations remain separate transitions and drivers convert them with the official Tinker function.
- Method: extended the test fixtures with the real transition API shape; added a TVCache two-turn case and changed the metrics input to a two-transition trajectory; reran the seven focused nodes.
- Result: **RED confirmed — 7 failed, 0 passed in 0.36 s**. All three drivers lacked `trajectory_to_data`; baseline, stateless, and TVCache each failed the old turn-2 length assertion; metrics could not consume a trajectory. This confirms that fixing only one loop or only the length check would be incomplete.

### Transition-Aware Rollout GREEN

- Motivation: preserve the exact observation/action/logprob relationship for the configured non-append renderer.
- Expectation: each loop returns official Tinker transitions, each driver delegates segmentation/alignment to `trajectory_to_data`, and metrics count every submitted prompt/action token numerically.
- Method: replaced prefix-length accumulation in all three loops with `Trajectory`, `Transition`, and `TokensWithLogprobs`; changed all drivers to extend training data from the cookbook converter; changed rollout metrics to sum transition observation and action lengths.
- Result: the focused transition batch is **7/7 PASS in 0.25 s**. The broader entry/client/loop/metrics set is **71/71 PASS in 0.48 s**. The two non-append turns retain observations `[10, 11]` and `[90, 91]`, sampled tokens `[20]` and `[30]`, and logprobs `[-0.2]` and `[-0.3]`; their metric record reports **6 total tokens** and **2 sampled tokens**. A real Python 3.12 converter/preflight remains part of the final CPU gate.

### Sandbox and Runtime Path Root-Cause Trace

- Motivation: ground I-023, I-029, and I-030 before defining the second RED batch.
- Expectation: identify existing state markers and every active cwd-dependent path without widening scope to unrelated legacy workflows.
- Method: inspected `SandboxManager` construction/create/fork/preprocess, the sandbox server, Video-LLaVA service, `ToolKit` VQA IPC, launch script, driver sandbox-ID construction, and all relevant constructor call sites.
- Result: `toolkits` already marks completed preprocessing, while `loaded_video` marks only video load, so fork can distinguish states without a new flag. `create_sandbox(..., exist_ok=True)` is the direct residual-reuse cause. All three drivers use the same repeatable `batch_*` ID shape. The active service additionally hardcodes `./sandboxes`, `./egoschema_cache`, `cache_dir`, `tmp/vqa.sock`, `tmp/content.pkl`, and `OPENAI_API_KEY=your_key`. The bounded repair is to use the existing toolkit marker, fail on existing directories, namespace IDs per run/variant, and require validated absolute directories for the active server/preprocessing/Video-LLaVA IPC path.

### Sandbox and Runtime Path Repair Design

- Motivation: define a narrow, testable configuration contract before editing GPU-service code.
- Expectation: active services work from any cwd, credentials are never overwritten, and legacy helper scripts do not determine the rollout contract.
- Method: reviewed current runtime-config tests, exact driver ID construction, `ToolKit` IPC code, and non-active constructor call sites.
- Result: the active contract will require existing absolute directories through environment variables: `VIDEO_AGENT_SANDBOX_DIR`, `EGOSCHEMA_CACHE_DIR`, `VIDEO_LLAVA_CACHE_DIR`, and `VIDEO_LLAVA_RUNTIME_DIR`. `SandboxManager` will receive/store the validated preprocessing and IPC directories and pass IPC state into `ToolKit`; `video-llava.py` will use the same runtime directory. Driver IDs will prepend one process-run ID containing the variant. Legacy interactive/preprocess scripts are outside the active RL reproduction path and will not receive compatibility fallbacks.

### Sandbox and Runtime Path RED

- Motivation: prove the loaded/preprocessed fork contract, residual-directory failure, run-specific IDs, and absolute active runtime configuration before implementation.
- Expectation: every missing behavior fails independently and existing preprocessed-fork cleanup remains guarded.
- Method: added two sandbox lifecycle cases, three parameterized driver ID gates, an absolute-directory validation case, and one active-path source gate; ran eight focused nodes.
- Result: **RED — 7 failed, 1 passed in 0.19 s**. Residual creation did not raise; all three drivers lacked `run_id`; relative runtime configuration reached the wrong error; and active files retained hardcoded paths/key. The preprocessed toolkit-failure cleanup guard passed. The first loaded-only test double had a signature mismatch; after correcting it, the intended RED showed **1 unwanted toolkit creation**.

### Sandbox and Runtime Path GREEN

- Motivation: make sandbox state transitions and Phase 4 service locations explicit and fail-fast.
- Expectation: loaded-only forks remain valid without premature `ToolKit`, residual directories are untouched, IDs cannot collide across variants/runs, and active paths are independent of cwd.
- Method: gated fork toolkit regeneration on the source `toolkits` marker; changed sandbox creation to `exist_ok=False`; prepended variant plus `time_ns` run IDs; required absolute configured directories; threaded preprocessing and Video-LLaVA IPC paths through manager/toolkit/service code; removed the placeholder key export and relative fork log.
- Result: focused GREEN is **8/8 PASS in 0.10 s**; the full sandbox/runtime/training-configuration set is **53/53 PASS in 0.26 s**. A loaded-only fork creates **0 toolkits**, a preprocessed toolkit failure still removes **1/1 copied sandbox**, and a residual marker remains unchanged when creation raises.

### Context Recovery for Remaining v2 Blockers

- Motivation: resume the existing task without repeating completed RED→GREEN work or entering the prohibited GPU phase early.
- Expectation: recover the exact branch, dirty state, active phase, latest review verdicts, and next uncompleted test-first actions.
- Method: reread `requirements.md`, `plan.md`, `harness.md`, `progress.md`, `issues.md`, `review.md`, `design.md`, `findings.md`, `notes.md`, and the current CPU test report; ran the planning session catch-up script; inspected Git status, diff statistics, and recent commits.
- Result: resumed `task/tvcache-rl-reproduction` at baseline commit `3a4f95a` with the full uncommitted implementation intact and no extra catch-up output. Phases 2 and 3 remain **In Progress**; Phase 4 remains closed. The next work is I-024 transactional executor cleanup/logger ownership and I-028 mutually exclusive exact-hit/prefix-hit/miss accounting, followed by missing schema-type and `success=False` coverage and a fresh Python 3.12 CPU gate.

### Executor Ownership and Metric Root-Cause Trace

- Motivation: confirm I-024 and I-028 at the active code boundaries before writing fixes.
- Expectation: identify which resource changes ownership at each await point and why the current statistics violate the one-call/one-classification contract.
- Method: read the complete async executor, active async cache client, fork bank, deterministic cache integration test, and existing executor configuration tests.
- Result: I-024 is source-confirmed at five ownership boundaries: `close()` skips environment teardown if client close fails; `set_rollout_id()` creates an untracked `FileHandler`; removed-environment and test-result cleanup use detached `Thread` objects, with the test-result thread calling an async method without awaiting it; a fork created before `/put` has no cleanup owner if publication fails; and a prefix-restored fork has no cleanup owner if `unref`, suffix execution, or replacement of the prior rollout environment fails. I-028 is caused by incrementing `cache_misses` before checking `env_id`, then incrementing `prefix_hits` for the same call. The next action is focused failure-injection and classification RED coverage, not production edits.

### Executor Ownership, Metric, and Schema RED

- Motivation: prove every remaining executor ownership boundary and cache classification/schema defect before production changes.
- Expectation: focused tests fail only because cleanup is detached/non-transactional, prefix hits are double-counted, or HTTP 200 payload types are accepted without validation.
- Method: added `tests/unit/test_async_executor_lifecycle.py` with cache-publication, prefix reference/fork/execute, replacement, close, logger, test-result, and classification cases; extended the active-client suite with exact/prefix/put type validation plus explicit `success=False` coverage; ran both modules in the locked client dev environment.
- Result: **RED confirmed — 15 failed, 12 passed in 0.53 s**. All 11 executor cases failed at their intended boundary: prefix hit reported miss `1`; unpublished and prefix forks had `0` required stop calls; fork failure made `0` unref calls; replacement/eviction cleanup did not raise; client-close failure skipped the active environment; the owned handler remained installed/open; and async test/stop coroutines were not awaited. Four schema-type cases accepted invalid values. The `success=False` case already passed, confirming the existing rejection branch. One expected runtime warning reported the unawaited async test/stop coroutines and is part of the reproduced defect.

### Full-Prefix Reference RED

- Motivation: verify the exact-after-prefix race path also releases the reference acquired by `prefix_match`.
- Expectation: a full-length prefix result returns the cached value and performs exactly one `unref`.
- Method: added a focused one-call regression whose initial exact lookup misses and whose prefix lookup returns a full cached environment.
- Result: **RED confirmed — 0/1 passed in 0.26 s**. The value and exact-hit metric were correct, but observed unref calls were **0**, expected **1**. This extends I-024 to the full-prefix race path before implementation.

### Redundant-Prefix Reference RED

- Motivation: verify an already-active rollout also releases the reference acquired by a redundant prefix lookup before continuing in its current environment.
- Expectation: the suffix executes in the active environment and the server receives exactly one `unref` for the unused cached parent.
- Method: seeded `executed_commands=1` and an active rollout environment, then returned a one-command cached prefix for a two-command request.
- Result: after correcting one import-time `elif`/`except` syntax error in the in-progress lifecycle patch, the intended **RED** was confirmed: **0/1 passed in 0.25 s**, with observed unref calls **0**, expected **1**. The suffix result itself was correct.

### Executor Ownership, Metric, and Schema GREEN

- Motivation: resolve I-024/I-028 and the missing schema-type checks at their ownership and HTTP boundaries without retries or detached cleanup.
- Expectation: every acquired prefix reference is released once; every unowned environment is stopped on failure; cache publication transfers ownership only after success; all cleanup errors remain visible; handlers close; and each successful call records exactly one cache outcome.
- Method: added structured executor lifecycle error aggregation; made eviction and test-result teardown awaited; stopped unpublished forks on `/put` failure; made prefix fork/unref/suffix paths transactional; transferred a successful prefix fork before synchronously replacing the old rollout environment; closed the executor-owned `FileHandler`; moved miss accounting into the no-prefix branch; and added exact/prefix/put response type validation.
- Result: focused GREEN is **29/29 PASS in 0.25 s**. The first GREEN run also passed 29/29 in 0.23 s but emitted one pytest collection warning because the imported helper class name began with `Test`; aliasing the import removed the warning without changing production behavior. Numeric invariants now show prefix hit `1`, miss `0`, total classified calls `1`; failed publication stops `1/1` unpublished fork; fork failure performs `1` unref; client-close failure still performs `1` active-environment stop; and the owned handler count falls from `1` to `0`.

### Cached-Test Classification RED→GREEN

- Motivation: apply the I-028 one-call/one-classification invariant to the executor's cached test-result path as well as normal tool calls.
- Expectation: one cached test result records total calls `1`, exact hits `1`, prefix hits `0`, and misses `0`.
- Method: added a focused cached-test regression, observed the missing exact-hit increment, then classified that successful cache result at the source.
- Result: RED was **0/1 passed in 0.27 s** with exact hits `0`; the expanded executor/client integration gate is now **32/32 PASS in 0.25 s** with the expected `1/1/0/0` classification tuple and no warnings.

### Python 3.12 Preflight Environment Audit

- Motivation: prepare the required real Tinker converter and three-driver startup checks without relying on the Python 3.10 mock-only test environment.
- Expectation: identify the authoritative locked environment, available interpreter, and exact converter contract before synchronization.
- Method: read the train manifest/lock configuration, verified installed Python/uv versions, checked for an existing train virtual environment, reread the cookbook `AGENTS.md`, and inspected the real `trajectory_to_data` implementation plus all three driver entry blocks.
- Result: system Python is **3.12.3**, the train project requires Python `>=3.12`, pins `tinker==0.24.1` and CPU-only Torch, and currently has **no `train/.venv`**. The real converter explicitly emits multiple `Datum` objects for non-prefix observations. All three entry blocks now import and call `asyncio`, but existing coverage is AST/mock based; a locked train environment and real-import preflight are still required. One over-broad site-package search was interrupted and replaced by the already located vendored converter source.

### Train Environment Sync Attempt 1

- Motivation: create the real locked Python 3.12 environment needed for converter and entrypoint preflight.
- Expectation: install the 139 locked packages into `/data/ycfeng/tmp/tvcache-train-py312` under the verified 2 GiB memory scope.
- Method: ran `uv sync --project train --frozen` with `TMPDIR`/`UV_CACHE_DIR` under `/data/ycfeng/tmp`, `UV_HTTP_TIMEOUT=30`, `timeout 600s`, and `systemd-run --user --scope -p MemoryMax=2G`.
- Result: **FAIL — exit 124 after 600 s** while downloading/building dependencies; Torch's **182.9 MiB** wheel completed, but uv did not reach its transactional install phase. No sync process remains, target environment size is **68 KiB** with **0** installed distributions, storage still has **135 GiB** free, and the reusable uv cache now contains **850 MiB**. The next diagnostic is an offline frozen sync to identify exactly which locked artifact is still absent.

### Train Cache Completeness Diagnosis

- Motivation: distinguish one missing wheel from a general resolver or installation failure.
- Expectation: an offline frozen sync either installs from the 850 MiB cache or names the first exact missing artifact.
- Method: ran the same resource-scoped sync with `--offline`, then attempted only the reported package through the prescribed company proxy.
- Result: offline sync exited immediately and identified the exact missing artifact: `scipy==1.18.0` for CPython 3.12 Linux x86_64. The targeted proxy-enabled install made **3** attempts over **46.2 s** but timed out connecting to `https://pypi.org/simple/scipy/`; it installed **0** packages. The next step is a bounded connectivity comparison against the exact `files.pythonhosted.org` wheel URL already recorded by uv, not another full sync.

### SciPy Artifact Connectivity and Attempt 2

- Motivation: determine whether the prescribed proxy or the canonical wheel host is the transfer bottleneck, then fetch only the missing locked artifact.
- Expectation: the working route completes the 33.7 MiB wheel within the 600-second resource scope.
- Method: issued bounded HEAD requests to the exact lockfile URL with and without `all_proxy`; then ran `uv pip install --no-deps` directly from that canonical URL under the same memory/timeout guard.
- Result: direct HEAD returned **HTTP 200**, connect **0.147 s**, total **0.627 s**; the prescribed proxy returned **HTTP 000** after **30.003 s**. Direct bulk transfer still exited **124 at 600 s** before installation, so the target environment remains incomplete. The root cause is slow/non-resumable bulk transfer rather than package resolution or URL validity; inspect uv's partial cache and switch to a resumable download of the same artifact.

### Fresh Python 3.10 Full CPU Gate

- Motivation: detect regressions from the executor/schema changes while the independent Python 3.12 artifact transfer proceeds.
- Expectation: all repository unit/integration tests, both locks, and whitespace checks pass without warnings or changes.
- Method: ran all `tests/unit` and `tests/integration` modules in the locked client dev environment; ran `git diff --check` and both `uv lock --check` commands.
- Result: **128/128 PASS in 0.79 s** on the current locked Python 3.10 environment with no warnings. `git diff --check` produced **0 findings**. Client and train locks resolved **28** and **139** packages respectively in **1 ms** and **2 ms**, both exit 0. This is an intermediate gate; Python 3.12 and real Tinker preflight remain pending.

### Python 3.12 Preflight Context Recovery

- Motivation: continue from the exact dependency-transfer interruption point without repeating the completed CPU remediation or entering the closed GPU phase.
- Expectation: confirm the active branch, task gates, locked environment state, preflight script, and resumable SciPy transfer before the next installation attempt.
- Method: reread `requirements.md`, `plan.md`, `harness.md`, `progress.md`, `issues.md`, and `notes.md`; inspected Git state, the Python 3.12 preflight script, the SciPy lock entry, the target environment, and the live canonical-wheel download.
- Result: branch `task/tvcache-rl-reproduction` and prior changes are intact; Phases 2/3 remain **In Progress** and Phase 4 remains **Pending**. The target environment still contains **0 installed distributions**. The canonical SciPy wheel has locked size **35,287,115 bytes** and SHA-256 `1f55797419e16e7f30cf88ffb3113ce0467f00cfe3f70d5c281730b21769bfc2`; the live resumable transfer advanced from **6,742,016** to **6,811,648 bytes** over five seconds, so it is making progress and must finish before offline synchronization.

### Real-Tinker Preflight Syntax Gate

- Motivation: catch a local script defect while the locked dependency artifact continues downloading, without pretending that real imports have run.
- Expectation: the new Python 3.12 preflight script compiles as Python source and remains clearly separate from the pending runtime gate.
- Method: compiled the complete source text of `tests/integration/tinker_runtime_preflight.py` in memory with system Python 3.12.3; no imports or bytecode writes were performed.
- Result: **PASS — 164/164 source lines compiled**. This proves syntax only; Tinker 0.24.1 imports, converter values, driver imports, and three `--help` exits remain pending until the locked environment is installed.

### Real-Tinker Preflight API Audit

- Motivation: verify that the preflight addresses the actual pinned SDK surface rather than an assumed or older Tinker API.
- Expectation: locked Tinker 0.24.1 exports its version and the `ModelInput` methods used by the script, while the vendored converter retains the non-prefix split contract.
- Method: inspected the exact extracted Tinker 0.24.1 artifact in the uv cache and the locked vendored `trajectory_to_data` implementation.
- Result: Tinker metadata and `tinker.__version__` both identify **0.24.1**; `ModelInput.from_ints()`, `to_ints()`, and `length` are present. The converter emits a new `Datum` when a later observation is not a prefix extension, matching the preflight's expected **2 datums**. Runtime execution is still required.

### SciPy Artifact Completion and Offline Sync Attempt 2

- Motivation: supply the exact missing locked artifact without changing the dependency graph or relying on the unusable proxy path.
- Expectation: the resumable canonical download matches both lockfile size and digest, installs into the Python 3.12 target, and lets offline sync either complete or identify the next exact missing artifact.
- Method: resumed the same `files.pythonhosted.org` wheel across bounded 600-second scopes; checked its size and SHA-256 against `train/uv.lock`; installed it with `uv pip install --offline --no-deps`; reran frozen offline sync against the same target environment.
- Result: SciPy wheel integrity **PASS** at **35,287,115 bytes** with SHA-256 `1f55797419e16e7f30cf88ffb3113ce0467f00cfe3f70d5c281730b21769bfc2`; `scipy==1.18.0` installed successfully and the environment now has **1 distribution**. Offline sync then failed fast on the next exact absent artifact, `pyyaml==6.0.3` CPython 3.12 wheel (**807,870 bytes**); no installed package was rolled back.

### PyYAML Artifact Completion and Offline Sync Attempt 3

- Motivation: continue filling only artifacts proven absent by the frozen offline resolver.
- Expectation: the exact PyYAML wheel passes lockfile integrity checks, installs locally, and advances the diagnostic without changing any version.
- Method: downloaded the canonical CPython 3.12 manylinux wheel, checked size and SHA-256 against `train/uv.lock`, installed it offline with no dependency resolution, and reran frozen offline sync.
- Result: PyYAML wheel integrity **PASS** at **807,870 bytes** with SHA-256 `ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc`; `pyyaml==6.0.3` installed successfully. The next sync failed fast only on absent `charset-normalizer==3.5.1` CPython 3.12 wheel (**248,801 bytes**), confirming incremental progress.

### Charset-Normalizer Artifact Completion and Offline Sync Attempt 4

- Motivation: continue the same lock-preserving cache-completeness loop after the third exact missing artifact.
- Expectation: charset-normalizer installs from its verified wheel and the next offline sync either completes or reports one different absent artifact.
- Method: downloaded the exact canonical CPython 3.12 manylinux wheel, verified lockfile size and SHA-256, installed it offline with no dependencies, and reran frozen offline sync.
- Result: charset-normalizer integrity **PASS** at **248,801 bytes** with SHA-256 `b9af956078716df40d985fb0dfeb2c2120c5ca92ba4ff4b388acfd01cdc14d08`; `charset-normalizer==3.5.1` installed successfully. The environment now has **3 distributions**. The next and only reported absent artifact is `pyarrow==25.0.1` CPython 3.12 wheel (**50,102,437 bytes**).

### PyArrow Artifact Completion and Offline Sync Attempt 5

- Motivation: satisfy the large remaining locked dataset dependency without rerunning an unbounded full download.
- Expectation: the resumable PyArrow transfer matches the lock and advances frozen sync while preserving all earlier local installs.
- Method: downloaded the exact canonical CPython 3.12 manylinux wheel in a resource-bounded resumable scope, verified its size and SHA-256, installed it offline with no dependencies, and reran frozen offline sync.
- Result: PyArrow integrity **PASS** at **50,102,437 bytes** with SHA-256 `5389cdf79447ed1515c9e31620e6e1e2302249564d603f2ad727d4f6d313e4c3`; `pyarrow==25.0.1` installed successfully and the environment now has **4 distributions**. The next reported absent artifact is `textarena==0.7.4` universal wheel (**1,073,570 bytes**).

### TextArena Completion and Local-Wheel Provenance Diagnosis

- Motivation: finish the fifth reported artifact and explain why an already installed PyArrow was requested again instead of masking the repeated failure.
- Expectation: TextArena passes lock integrity; source inspection identifies whether the repeat is cache absence, installation loss, or provenance mismatch.
- Method: downloaded, verified, and installed the exact TextArena wheel; reran frozen offline sync; inspected all five installed distributions and their `direct_url.json`; then ran a frozen offline `--find-links /data/ycfeng/tmp --dry-run`.
- Result: TextArena integrity **PASS** at **1,073,570 bytes** with SHA-256 `684784e78278e518066f67557ee93b47c238d16cbbd15d3abdaa3147562d3024`; all **5** locally installed distributions remained present. The repeated PyArrow request is caused by their `file://` provenance differing from the registry-locked source, not by missing files or rollback. The `--find-links` dry run exited **0**, found a complete offline plan for **138 packages**, and reported **0 missing artifacts**; it will replace the 5 temporary file-provenance installs with the frozen environment.

### Frozen Find-Links Sync Attempt 1

- Motivation: reconcile the five verified local wheels with the registry-locked environment and install the remaining cached packages in one transaction.
- Expectation: the real sync matches the dry-run plan or identifies any artifact the planner did not validate.
- Method: ran frozen offline sync with `/data/ycfeng/tmp` as `--find-links` under the 2 GiB user scope.
- Result: **FAIL before environment modification** on missing `tokenizers==0.22.2` CPython ABI3 manylinux wheel (**3,274,982 bytes**). This establishes that uv's dry run validates the action plan but not complete artifact readability. The corrected loop keeps `--find-links` and downloads verified wheels without separately installing them, avoiding further `file://` provenance churn.

### Tokenizers Completion and Frozen Find-Links Sync Attempt 2

- Motivation: provide the first artifact missing from the real `--find-links` transaction while avoiding direct local installation provenance.
- Expectation: the verified wheel is discovered by the next offline sync, which either completes or names a different absent artifact.
- Method: resumably downloaded the exact tokenizers CPython ABI3 manylinux wheel, verified lockfile size and SHA-256, left it uninstalled in `/data/ycfeng/tmp`, and repeated frozen offline sync with `--find-links`.
- Result: tokenizers integrity **PASS** at **3,274,982 bytes** with SHA-256 `369cc9fc8cc10cb24143873a0d95438bb8ee257bb80c71989e3ee290e8d72c67`. The next sync advanced to absent `textual==8.2.8` universal wheel (**731,418 bytes**) and made no environment changes.

### Textual Completion and Registry-Provenance Recheck

- Motivation: supply Textual and verify whether `--find-links` alone can satisfy an already frozen registry URL.
- Expectation: the exact wheel passes integrity and either completes sync or gives evidence that installed/source provenance still blocks reconciliation.
- Method: downloaded and verified the locked Textual universal wheel, left it in the flat wheel directory, and repeated the real frozen offline `--find-links` sync.
- Result: Textual integrity **PASS** at **731,418 bytes** with SHA-256 `267375fd402dc8d981457212efa71f0e3365fd17bba144ba9bb3ed7563cb374a`. Sync then requested PyArrow again, proving that a flat wheel does not populate the canonical registry-URL cache entry for a frozen lock. The next bounded experiment installs an exact package by name from the offline flat index and checks whether this removes `direct_url.json`; that outcome determines whether installed-state reconciliation is valid.

### Name-Based Offline Install Provenance GREEN

- Motivation: make the verified local wheels satisfy the frozen registry lock without editing uv's internal cache or redownloading completed artifacts.
- Expectation: package-name installation from the offline flat index records ordinary installed packages with no `file://` direct requirement, after which none of those packages repeats as missing.
- Method: installed Textual by exact package name to verify metadata behavior; then reinstalled the five direct-file packages plus tokenizers by exact names with `--offline --no-index --find-links`, and inspected every distribution for `direct_url.json`; reran plain frozen offline sync.
- Result: **GREEN** — all **7/7** exact versions are installed and **0/7** contain `direct_url.json`. The next plain sync did not repeat SciPy, PyYAML, charset-normalizer, PyArrow, TextArena, tokenizers, or Textual; it advanced to the genuinely absent `inspect-ai==0.3.258` universal wheel (**34,829,837 bytes**).

### Inspect AI Artifact Completion and Offline Sync Attempt 6

- Motivation: provide the next exact locked dependency despite very low single-connection throughput.
- Expectation: byte-range assembly is accepted only if every segment length and the final lockfile digest match, then name-based installation advances the offline sync.
- Method: downloaded a prefix and verified 1 MiB tail from the canonical URL, split the remaining non-overlapping byte ranges across four bounded concurrent connections, checked all six segment sizes, assembled them in order, verified final size/SHA-256, and installed by exact package name from the offline flat index.
- Result: Inspect AI integrity **PASS** at **34,829,837 bytes** with SHA-256 `638da28a5f3a021152481c5aa22d440a2855e462804dce2d49a44e6e47be16a4`; `inspect-ai==0.3.258` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `transformers==5.4.0` universal wheel (**10,105,556 bytes**).

### Transformers Artifact Completion and Offline Sync Attempt 7

- Motivation: continue resolving only the artifact named by the previous frozen sync while retaining the proven name-based install semantics.
- Expectation: four non-overlapping ranges reassemble to the exact Transformers lock artifact and the next sync advances without repeating earlier packages.
- Method: split the canonical wheel into four equal byte ranges, downloaded them concurrently under the resource limit, verified all segment lengths, assembled the wheel, checked lockfile size/SHA-256, and installed by exact name from the offline flat index.
- Result: Transformers integrity **PASS** at **10,105,556 bytes** with SHA-256 `9fbe50602d2a4e6d0aa8a35a605433dfac72d595ee2192eae192590a6cc2df86`; `transformers==5.4.0` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `numpy==2.4.3` CPython 3.12 wheel (**16,621,358 bytes**).

### NumPy Artifact Completion and Offline Sync Attempt 8

- Motivation: supply the locked numerical runtime required by the real converter and the remaining dependency graph.
- Expectation: the four range segments reassemble exactly, name-based installation keeps normal provenance, and sync advances without repeating prior artifacts.
- Method: downloaded four complete non-overlapping canonical ranges, checked their lengths, assembled the NumPy wheel, verified lockfile size/SHA-256, installed by exact name from the offline flat index, and reran frozen offline sync.
- Result: NumPy integrity **PASS** at **16,621,358 bytes** with SHA-256 `e7dd01a46700b1967487141a66ac1a3cf0dd8ebf1f08db37d46389401512ca97`; `numpy==2.4.3` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `botocore==1.40.61` universal wheel (**14,055,973 bytes**).

### Botocore Artifact Completion and Offline Sync Attempt 9

- Motivation: fill the next locked dependency required by Inspect AI without changing package versions or the dependency graph.
- Expectation: verified range assembly and name-based installation advance frozen sync with normal provenance.
- Method: downloaded four non-overlapping canonical ranges, checked segment lengths, assembled and lock-verified the wheel, installed by exact name from the offline flat index, and reran frozen offline sync.
- Result: botocore integrity **PASS** at **14,055,973 bytes** with SHA-256 `17ebae412692fd4824f99cde0f08d50126dc97954008e5ba2b522eb049238aa7`; `botocore==1.40.61` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `pandas==3.0.5` CPython 3.12 wheel (**10,998,091 bytes**).

### Pandas Artifact Completion and Offline Sync Attempt 10

- Motivation: provide the locked dataframe dependency needed by `datasets`.
- Expectation: validated range assembly and name-based installation advance the frozen sync without reintroducing direct URL provenance.
- Method: downloaded four non-overlapping canonical ranges, verified segment lengths and the assembled wheel against the lock, installed by exact package name, and reran plain frozen offline sync.
- Result: pandas integrity **PASS** at **10,998,091 bytes** with SHA-256 `d373ce03ffd84010ed9839fa73672a9c8256990532e158440c0085db7d914b34`; `pandas==3.0.5` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `sympy==1.14.0` universal wheel (**6,299,353 bytes**).

### SymPy Artifact Completion and Offline Sync Attempt 11

- Motivation: provide Torch's locked symbolic-math dependency while preserving the CPU-only training environment.
- Expectation: verified range assembly and exact-name installation advance sync without altering Torch or any dependency version.
- Method: downloaded four canonical ranges, checked segment lengths, assembled and lock-verified the wheel, installed by exact name, and reran plain frozen offline sync.
- Result: SymPy integrity **PASS** at **6,299,353 bytes** with SHA-256 `e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5`; `sympy==1.14.0` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `pyqwest==0.9.0` CPython 3.12 wheel (**5,572,909 bytes**).

### Pyqwest Artifact Completion and Offline Sync Attempt 12

- Motivation: supply Tinker 0.24.1's locked native HTTP dependency.
- Expectation: the assembled wheel matches the exact lock artifact and name-based installation advances sync without direct URL metadata.
- Method: downloaded four non-overlapping canonical ranges, verified the segment lengths and final lockfile values, installed by exact package name, and reran plain frozen offline sync.
- Result: pyqwest integrity **PASS** at **5,572,909 bytes** with SHA-256 `3be3d38ccdab3077bf1cfe90c346ce927f9b49c56dcdf20e060f5f2502d01021`; `pyqwest==0.9.0` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `zstandard==0.25.0` CPython 3.12 wheel (**5,546,993 bytes**).

### Zstandard Artifact Completion and Offline Sync Attempt 13

- Motivation: provide Tinker 0.24.1's locked compression dependency.
- Expectation: verified range assembly and exact-name installation advance the offline sync with no source mismatch.
- Method: downloaded four canonical byte ranges, validated segment lengths and final lockfile size/SHA-256, installed by package name, and reran plain frozen offline sync.
- Result: zstandard integrity **PASS** at **5,546,993 bytes** with SHA-256 `5a56ba0db2d244117ed744dfa8f6f5b366e14148e00de44723413b2f3938a902`; `zstandard==0.25.0` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `joblib==1.5.3` universal wheel (**309,071 bytes**).

### Joblib Artifact Completion and Offline Sync Attempt 14

- Motivation: provide NLTK's small locked execution dependency after all larger native artifacts were resolved.
- Expectation: exact wheel verification and name-based installation advance the frozen sync.
- Method: downloaded the canonical universal wheel, verified lockfile size/SHA-256, installed by exact package name, and reran plain frozen offline sync.
- Result: joblib integrity **PASS** at **309,071 bytes** with SHA-256 `5fc3c5039fc5ca8c0276333a188bbd59d6b7ab37fe6632daa76bc7f9ec18e713`; `joblib==1.5.3` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `safetensors==0.7.0` CPython ABI3 wheel (**507,152 bytes**).

### Safetensors Artifact Completion and Offline Sync Attempt 15

- Motivation: provide Transformers' locked tensor serialization dependency.
- Expectation: exact wheel verification and name-based installation advance the frozen sync without source mismatch.
- Method: downloaded the canonical ABI3 wheel, verified lockfile size/SHA-256, installed by exact package name, and reran plain frozen offline sync.
- Result: safetensors integrity **PASS** at **507,152 bytes** with SHA-256 `dac7252938f0696ddea46f5e855dd3138444e82236e3be475f54929f0c510d48`; `safetensors==0.7.0` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `lxml==6.1.1` CPython 3.12 wheel (**5,240,367 bytes**).

### Lxml Artifact Completion and Offline Sync Attempt 16

- Motivation: provide Blobfile's locked XML runtime dependency.
- Expectation: validated range assembly and exact-name installation advance the frozen sync without source mismatch.
- Method: downloaded four canonical ranges, validated their lengths and final lockfile size/SHA-256, installed by exact package name, and reran plain frozen offline sync.
- Result: lxml integrity **PASS** at **5,240,367 bytes** with SHA-256 `ebe6af670449830d6d9b752c256a983291c766a1365ba5d5460048f9e33a7818`; `lxml==6.1.1` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `hf-xet==1.4.2` ABI3 wheel (**4,217,422 bytes**).

### Hf-Xet Artifact Completion and Offline Sync Attempt 17

- Motivation: provide Hugging Face Hub's locked native transfer dependency.
- Expectation: verified range assembly and exact-name installation advance the offline sync with ordinary provenance.
- Method: downloaded four canonical byte ranges, verified their lengths and the final lockfile values, installed by package name, and reran plain frozen offline sync.
- Result: hf-xet integrity **PASS** at **4,217,422 bytes** with SHA-256 `77e8c180b7ef12d8a96739a4e1e558847002afe9ea63b6f6358b2271a8bdda1c`; `hf-xet==1.4.2` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `debugpy==1.8.21` CPython 3.12 wheel (**3,968,900 bytes**).

### Debugpy Artifact Completion and Offline Sync Attempt 18

- Motivation: provide Inspect AI's locked debugger runtime dependency.
- Expectation: verified range assembly and exact-name installation advance the frozen sync with normal provenance.
- Method: downloaded four equal canonical byte ranges, verified the final size/SHA-256, installed by exact package name, and reran plain frozen offline sync.
- Result: debugpy integrity **PASS** at **3,968,900 bytes** with SHA-256 `c193d474f0a211191f2b4449d2d06157c689013035bd952f3b617e0ef422b176`; `debugpy==1.8.21` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `pycryptodomex==3.23.0` ABI3 wheel (**2,272,578 bytes**).

### Pycryptodomex Artifact Completion and Offline Sync Attempt 19

- Motivation: provide Blobfile's locked cryptographic dependency.
- Expectation: verified byte-range assembly and exact-name installation advance the frozen sync.
- Method: downloaded four canonical ranges, checked their lengths and the assembled lockfile size/SHA-256, installed by exact package name, and reran plain frozen offline sync.
- Result: pycryptodomex integrity **PASS** at **2,272,578 bytes** with SHA-256 `f489c4765093fb60e2edafdf223397bc716491b2b69fe74367b70d6999257a5c`; `pycryptodomex==3.23.0` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `pydantic-core==2.46.4` CPython 3.12 wheel (**2,094,516 bytes**).

### Pydantic-Core Artifact Completion and Offline Sync Attempt 20

- Motivation: provide Pydantic's locked native validation core used by Tinker and the drivers.
- Expectation: exact range assembly and name-based installation advance the frozen sync with no source mismatch.
- Method: downloaded four equal canonical ranges, verified segment lengths and final lockfile size/SHA-256, installed by exact name, and reran plain frozen offline sync.
- Result: pydantic-core integrity **PASS** at **2,094,516 bytes** with SHA-256 `926c9541b14b12b1681dca8a0b75feb510b06c6341b70a8e500c2fdcff837cce`; `pydantic-core==2.46.4` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `networkx==3.6.1` universal wheel (**2,068,504 bytes**).

### NetworkX Artifact Completion and Offline Sync Attempt 21

- Motivation: provide Torch's locked graph dependency.
- Expectation: exact range assembly and name-based installation advance the frozen sync with ordinary provenance.
- Method: downloaded four equal canonical ranges, verified the final lockfile size/SHA-256, installed by exact package name, and reran plain frozen offline sync.
- Result: NetworkX integrity **PASS** at **2,068,504 bytes** with SHA-256 `d47fbf302e7d9cbbb9e2555a0d267983d2aa476bac30e90dfbe5669bd57f3762`; `networkx==3.6.1` installed with **0 direct URL records**. Plain frozen offline sync advanced to absent `rich==14.3.3` universal wheel (**310,458 bytes**).

### Rich Artifact Completion and Offline Sync Attempt 22

- Motivation: provide the next exact frozen dependency while preserving registry-compatible installed provenance.
- Expectation: the Rich wheel matches the lock, installs by package name with no `direct_url.json`, and advances the real offline sync to a different missing artifact.
- Method: downloaded the canonical universal wheel, verified its size and SHA-256 against `train/uv.lock`, installed `rich==14.3.3` by exact package name from the offline flat index, inspected the Python 3.12 environment metadata, and reran the resource-scoped frozen offline sync.
- Result: Rich integrity **PASS** at **310,458 bytes** with SHA-256 `793431c1f8619afa7d3b52b2cdec859562b950ea0d4b6b505397612db8d5362d`; `rich==14.3.3` is installed, the environment contains **24 distributions**, and it contains **0 direct URL records**. The fresh frozen offline sync advanced only to absent `nltk==3.10.3` universal wheel (**1,798,643 bytes**, expected SHA-256 `ff9598a8e20518ee0d557745890cc4435b9578489e2dcbc69c4f81fa060caf7c`).

### NLTK Artifact Completion and Offline Sync Attempt 23

- Motivation: provide TextArena's locked NLTK dependency without altering the frozen dependency graph.
- Expectation: the canonical wheel matches the lock, exact-name installation preserves ordinary provenance, and the next offline sync advances without repeating NLTK.
- Method: downloaded the exact canonical NLTK wheel under a bounded user scope, verified size and SHA-256 against `train/uv.lock`, installed `nltk==3.10.3` by package name from the offline flat index, inspected environment metadata, and reran frozen offline sync.
- Result: NLTK integrity **PASS** at **1,798,643 bytes** with SHA-256 `ff9598a8e20518ee0d557745890cc4435b9578489e2dcbc69c4f81fa060caf7c`; `nltk==3.10.3` is installed, the environment contains **25 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `aiohttp==3.14.3` CPython 3.12 wheel (**1,792,122 bytes**, expected SHA-256 `543906c127fb1d929b95076db19b83fa2d46751006ff1e23b093aa5ac4d8db42`).

### Aiohttp Artifact Completion and Offline Sync Attempt 24

- Motivation: provide the exact locked HTTP runtime selected for Python 3.12/Linux without changing any source or version.
- Expectation: non-overlapping canonical ranges reconstruct the lock artifact, exact-name installation keeps normal provenance, and sync advances to a different missing dependency.
- Method: downloaded four byte ranges concurrently under the 2 GiB scope, verified each segment length plus the assembled wheel size/SHA-256, installed `aiohttp==3.14.3` by package name, inspected environment metadata, and reran frozen offline sync.
- Result: aiohttp integrity **PASS** at **1,792,122 bytes** with SHA-256 `543906c127fb1d929b95076db19b83fa2d46751006ff1e23b093aa5ac4d8db42`; `aiohttp==3.14.3` is installed, the environment contains **26 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `openai==2.54.0` universal wheel (**1,660,351 bytes**, expected SHA-256 `89089789197ccdb87f173a03145ed1598d00795220c93e96cf712b1cbf5e5f2b`).

### OpenAI Artifact Completion and Offline Sync Attempt 25

- Motivation: provide TextArena's exact locked OpenAI client without changing the frozen dependency graph.
- Expectation: verified range assembly and package-name installation preserve ordinary provenance and advance the offline sync.
- Method: downloaded four non-overlapping canonical ranges under the 2 GiB scope, checked all segment lengths and the final lockfile values, installed `openai==2.54.0` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: OpenAI integrity **PASS** at **1,660,351 bytes** with SHA-256 `89089789197ccdb87f173a03145ed1598d00795220c93e96cf712b1cbf5e5f2b`; `openai==2.54.0` is installed, the environment contains **27 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `pygments==2.19.2` universal wheel (**1,225,217 bytes**, expected SHA-256 `86540386c03d588bb81d44bc3928634ff26449851e99741617ecb9037ee5ec0b`).

### Pygments Artifact Completion and Offline Sync Attempt 26

- Motivation: provide Rich's exact locked syntax-highlighting dependency.
- Expectation: verified range assembly and exact-name installation advance frozen sync without introducing direct-file provenance.
- Method: downloaded four canonical byte ranges concurrently, verified each segment and the final lockfile size/SHA-256, installed `pygments==2.19.2` by package name, inspected environment metadata, and reran frozen offline sync.
- Result: Pygments integrity **PASS** at **1,225,217 bytes** with SHA-256 `86540386c03d588bb81d44bc3928634ff26449851e99741617ecb9037ee5ec0b`; `pygments==2.19.2` is installed, the environment contains **28 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `tiktoken==0.13.0` CPython 3.12 wheel (**1,136,523 bytes**, expected SHA-256 `a116178fa7e1b4065bff05214360373a65cac22f965be7b3f73d00a0dbfe7649`).

### Tiktoken Artifact Completion and Offline Sync Attempt 27

- Motivation: provide Inspect AI's exact locked token-counting runtime for the real Tinker preflight.
- Expectation: verified CPython 3.12 wheel assembly and exact-name installation advance frozen sync with ordinary provenance.
- Method: downloaded four non-overlapping canonical ranges, verified all segment lengths plus the assembled lockfile size/SHA-256, installed `tiktoken==0.13.0` by package name, inspected environment metadata, and reran frozen offline sync.
- Result: tiktoken integrity **PASS** at **1,136,523 bytes** with SHA-256 `a116178fa7e1b4065bff05214360373a65cac22f965be7b3f73d00a0dbfe7649`; `tiktoken==0.13.0` is installed, the environment contains **29 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `setuptools==84.0.0` universal wheel (**818,216 bytes**, expected SHA-256 `51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670`).

### Setuptools Artifact Completion and Offline Sync Attempt 28

- Motivation: provide Torch's exact locked packaging runtime in the Python 3.12 environment.
- Expectation: verified canonical wheel installation by name advances frozen sync without source-provenance drift.
- Method: downloaded four equal non-overlapping byte ranges, verified all segment sizes and the assembled lockfile size/SHA-256, installed `setuptools==84.0.0` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: setuptools integrity **PASS** at **818,216 bytes** with SHA-256 `51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670`; `setuptools==84.0.0` is installed, the environment contains **30 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `regex==2026.2.28` CPython 3.12 wheel (**802,037 bytes**, expected SHA-256 `d6b08a06976ff4fb0d83077022fde3eca06c55432bb997d8c0495b9a4e9872f4`).

### Regex Artifact Completion and Offline Sync Attempt 29

- Motivation: provide Transformers' exact locked regular-expression runtime.
- Expectation: verified CPython 3.12 wheel assembly and package-name installation advance sync without provenance drift.
- Method: downloaded four canonical byte ranges concurrently, checked segment lengths and final lockfile integrity, installed `regex==2026.2.28` by exact package name, inspected environment metadata, and reran frozen offline sync.
- Result: regex integrity **PASS** at **802,037 bytes** with SHA-256 `d6b08a06976ff4fb0d83077022fde3eca06c55432bb997d8c0495b9a4e9872f4`; `regex==2026.2.28` is installed, the environment contains **31 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `huggingface-hub==1.8.0` universal wheel (**625,208 bytes**, expected SHA-256 `d3eb5047bd4e33c987429de6020d4810d38a5bef95b3b40df9b17346b7f353f2`).

### Hugging Face Hub Artifact Completion and Offline Sync Attempt 30

- Motivation: provide the exact hub runtime shared by Datasets and Transformers.
- Expectation: verified canonical wheel installation by package name advances frozen sync with no direct URL metadata.
- Method: downloaded four equal canonical byte ranges concurrently, verified their lengths plus final size/SHA-256, installed `huggingface-hub==1.8.0` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: Hugging Face Hub integrity **PASS** at **625,208 bytes** with SHA-256 `d3eb5047bd4e33c987429de6020d4810d38a5bef95b3b40df9b17346b7f353f2`; `huggingface-hub==1.8.0` is installed, the environment contains **32 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `datasets==5.0.1` universal wheel (**559,079 bytes**, expected SHA-256 `9fbf73688f8c18f7529b4fe592abd04015f81d1e58001e4bac73ffb2b39d7cc4`).

### Datasets Artifact Completion and Offline Sync Attempt 31

- Motivation: provide the training project's exact locked dataset runtime.
- Expectation: verified canonical wheel installation advances frozen sync without changing the selected dataset version or provenance.
- Method: downloaded four non-overlapping canonical ranges, checked their lengths and the final lockfile size/SHA-256, installed `datasets==5.0.1` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: Datasets integrity **PASS** at **559,079 bytes** with SHA-256 `9fbf73688f8c18f7529b4fe592abd04015f81d1e58001e4bac73ffb2b39d7cc4`; `datasets==5.0.1` is installed, the environment contains **33 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `mpmath==1.3.0` universal wheel (**536,198 bytes**, expected SHA-256 `a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c`).

### Mpmath Artifact Completion and Offline Sync Attempt 32

- Motivation: provide SymPy's exact locked arbitrary-precision math dependency.
- Expectation: verified wheel installation by package name advances frozen sync without altering Torch or SymPy.
- Method: downloaded four non-overlapping canonical ranges, verified their sizes and the assembled lockfile integrity, installed `mpmath==1.3.0` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: mpmath integrity **PASS** at **536,198 bytes** with SHA-256 `a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c`; `mpmath==1.3.0` is installed, the environment contains **34 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `pydantic==2.13.4` universal wheel (**472,262 bytes**, expected SHA-256 `45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba`).

### Pydantic Artifact Completion and Offline Sync Attempt 33

- Motivation: provide the training project and Tinker stack's exact locked validation runtime.
- Expectation: verified wheel installation by package name works with the already installed matching pydantic-core and advances frozen sync.
- Method: downloaded four non-overlapping canonical ranges, verified their lengths plus final size/SHA-256, installed `pydantic==2.13.4` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: Pydantic integrity **PASS** at **472,262 bytes** with SHA-256 `45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba`; `pydantic==2.13.4` is installed, the environment contains **35 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `rpds-py==2026.6.3` CPython 3.12 wheel (**366,189 bytes**, expected SHA-256 `ecabd69db66de867690f9797f2f8fa27ba501bbc24540cbdbdc649cd15888ba6`).

### Rpds-py Artifact Completion and Offline Sync Attempt 34

- Motivation: provide jsonschema's exact locked persistent-data-structure runtime used by Inspect AI.
- Expectation: verified CPython 3.12 wheel installation advances frozen sync with ordinary registry-compatible provenance.
- Method: downloaded four canonical byte ranges concurrently, verified each segment and final lockfile integrity, installed `rpds-py==2026.6.3` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: rpds-py integrity **PASS** at **366,189 bytes** with SHA-256 `ecabd69db66de867690f9797f2f8fa27ba501bbc24540cbdbdc649cd15888ba6`; `rpds-py==2026.6.3` is installed, the environment contains **36 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `jiter==0.16.0` CPython 3.12 wheel (**343,805 bytes**, expected SHA-256 `46add52f4ad47a08bfb1219f3e673da972191489a33016edefdb5ea55bfa8c48`).

### Jiter Artifact Completion and Offline Sync Attempt 35

- Motivation: provide OpenAI's exact locked JSON parsing runtime.
- Expectation: verified CPython 3.12 wheel installation by package name advances frozen sync without provenance drift.
- Method: downloaded four non-overlapping canonical ranges, verified segment lengths and final lockfile integrity, installed `jiter==0.16.0` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: jiter integrity **PASS** at **343,805 bytes** with SHA-256 `46add52f4ad47a08bfb1219f3e673da972191489a33016edefdb5ea55bfa8c48`; `jiter==0.16.0` is installed, the environment contains **37 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `protobuf==7.35.1` ABI3 wheel (**327,130 bytes**, expected SHA-256 `74758715c53d7158fb76caf4f0cfdacc5329a4b1bb994f865d6cf302d413a1c4`).

### Protobuf Artifact Completion and Offline Sync Attempt 36

- Motivation: provide Tinker 0.24.1's exact locked serialization runtime.
- Expectation: verified ABI3 wheel installation by package name advances frozen sync and remains compatible with Python 3.12.
- Method: downloaded four non-overlapping canonical ranges, checked all segment lengths and final lockfile integrity, installed `protobuf==7.35.1` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: protobuf integrity **PASS** at **327,130 bytes** with SHA-256 `74758715c53d7158fb76caf4f0cfdacc5329a4b1bb994f865d6cf302d413a1c4`; `protobuf==7.35.1` is installed, the environment contains **38 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `multidict==6.7.1` CPython 3.12 wheel (**256,322 bytes**, expected SHA-256 `bfde23ef6ed9db7eaee6c37dcec08524cb43903c60b285b172b6c094711b3961`).

### Multidict Artifact Completion and Offline Sync Attempt 37

- Motivation: provide aiohttp's exact locked multidict runtime.
- Expectation: verified CPython 3.12 wheel installation advances frozen sync while preserving ordinary provenance.
- Method: downloaded four non-overlapping canonical ranges, verified all segment sizes and final lockfile integrity, installed `multidict==6.7.1` by exact name, inspected environment metadata, and reran frozen offline sync.
- Result: multidict integrity **PASS** at **256,322 bytes** with SHA-256 `bfde23ef6ed9db7eaee6c37dcec08524cb43903c60b285b172b6c094711b3961`; `multidict==6.7.1` is installed, the environment contains **39 distributions**, and it contains **0 direct URL records**. Frozen offline sync advanced to absent `frozenlist==1.8.0` CPython 3.12 wheel (**242,411 bytes**, expected SHA-256 `494a5952b1c597ba44e0e78113a7266e656b9794eec897b19ead706bd7074383`).

### Frozenlist Completion and Chess Build-Isolation Diagnosis

- Motivation: provide aiohttp's locked frozenlist runtime and diagnose the first source-build failure instead of treating it as another missing runtime package.
- Expectation: frozenlist installs with normal provenance; any subsequent build error identifies the isolated build requirement that the plain offline sync cannot read.
- Method: downloaded four canonical byte ranges, verified the assembled wheel against the lock, installed `frozenlist==1.8.0` by exact name, inspected environment metadata, reran frozen offline sync, inspected the locked Chess source and setuptools artifacts, and consulted `task_memory/env_handbook.md`.
- Result: frozenlist integrity **PASS** at **242,411 bytes** with SHA-256 `494a5952b1c597ba44e0e78113a7266e656b9794eec897b19ead706bd7074383`; `frozenlist==1.8.0` is installed, the environment contains **40 distributions**, and it contains **0 direct URL records**. Sync reached the cached `chess==1.11.2` source build but its isolated PEP 517 environment could not read the canonical `setuptools==84.0.0` wheel from uv's registry cache. The verified wheel exists in `/data/ycfeng/tmp`; the bounded root-cause test is an exact-name offline Chess install with that flat index available to build isolation.

### Chess Build-Isolation Attempt 1

- Motivation: expose the verified setuptools wheel to Chess's isolated build environment without changing versions or disabling build isolation.
- Expectation: uv resolves cached Chess from its registry cache and resolves the build-only setuptools requirement from the flat wheel index.
- Method: ran an exact-name `uv pip install` with `--offline --no-index --find-links /data/ycfeng/tmp --no-deps` against the Python 3.12 environment.
- Result: **FAIL before build or environment modification** because `--no-index` also excluded uv's cached registry metadata for Chess, and the flat directory contains no Chess source archive. The next attempt removes only `--no-index` while keeping `--offline`, `--find-links`, and `--no-deps`, allowing cached Chess selection and flat-index build requirements.

### Chess Build-Isolation GREEN and Full Frozen Sync

- Motivation: make the cached Chess source build consume the exact lock-verified setuptools wheel while retaining cached registry metadata and disabled network access.
- Expectation: exact-name Chess installation builds successfully with ordinary provenance, then plain frozen offline sync installs every remaining package without another artifact error.
- Method: ran `uv pip install --offline --find-links /data/ycfeng/tmp --no-deps ... chess==1.11.2` without `--no-index`; inspected Chess and direct URL metadata; reran plain resource-scoped `uv sync --project train --frozen --offline`; counted installed and locked packages; and ran `uv pip check`.
- Result: **GREEN** — Chess built and installed in **1.14 s**; it added no `direct_url.json`. Plain frozen offline sync installed the remaining **97 packages in 565 ms** and exited **0**. The final environment contains **138 compatible distributions** from a **139-package lock**, including `tinker==0.24.1` and `torch==2.13.0+cpu`; `uv pip check` checked **138** and reported all compatible. Exactly **2** direct URL records remain, both expected local locked projects (`tinker-cookbook` and `tvclient`), with **0 registry package direct URL records**. I-031 is resolved.

### Real Tinker Preflight RED and Help-Exit Root Cause

- Motivation: execute the real Python 3.12 converter and driver-entrypoint gate now that the complete frozen environment exists.
- Expectation: validate Tinker 0.24.1, two non-prefix datums, all three driver imports, and each driver's native help contract.
- Method: ran `tests/integration/tinker_runtime_preflight.py` under the locked Python 3.12 environment; reproduced `train_without_cache.py --help` with credentials removed; inspected chz 0.4.0's `exit_on_entrypoint_error`; and ran the vendored official `math_rl/train.py --help` as the working reference.
- Result: **RED — preflight exit 1** at the first help-code assertion. Both the project driver and official Tinker cookbook print valid help to stdout and return **1**. chz 0.4.0 explicitly maps `EntrypointHelpException` to `sys.exit(1)`; therefore the preflight's expected code **0** is incorrect, while the production drivers already follow the native cookbook pattern. The minimal correction is test-only: require native code 1, empty stderr, and the expected help fields.

### Real Tinker Preflight GREEN

- Motivation: validate the corrected test contract against all three real entrypoints and the pinned converter API.
- Expectation: Python 3.12.3 and Tinker 0.24.1 produce two token-aligned datums; all three drivers import, expose async `main`, and emit valid native chz help with no stderr.
- Method: changed only the preflight assertion to require native chz exit 1 plus empty stderr and required help fields, then reran the complete script in the resource-scoped frozen Python 3.12 environment.
- Result: **PASS — exit 0**. Converter output is exactly **2 datums**, inputs `[[10, 11], [90, 91]]`, targets `[[11, 20], [91, 30]]`, and **2 sampled tokens**. All **3/3** drivers imported, all **3/3** `main` functions are async, all **3/3** help invocations returned native code **1** with **0 stderr lines**, and help output contained **19, 19, and 20 lines**. I-032 is resolved.

### Python 3.12 Client Test Environment Attempt 1

- Motivation: run the complete 128-test CPU suite on Python 3.12 without adding test-only packages to the frozen training environment.
- Expectation: create a separate client `dev` environment from `tvcache/client/uv.lock` using the existing offline cache.
- Method: targeted `/data/ycfeng/tmp/tvcache-client-py312` with system CPython 3.12.3 and ran resource-scoped `uv sync --project tvcache/client --group dev --frozen --offline`.
- Result: **FAIL before package installation** on the canonical Pygments 2.19.2 URL. The already lock-verified Pygments wheel exists in `/data/ycfeng/tmp`, but plain frozen sync cannot treat that flat file as its canonical cache entry. The established root-cause path is to install the exact version by package name from the flat index, confirm no direct URL metadata, and rerun plain frozen sync.

### Python 3.12 Client Test Environment Attempt 2

- Motivation: satisfy the one missing client-dev artifact through the already verified name-based flat-index method.
- Expectation: Pygments remains installed and the following frozen client sync fills the rest of the Python 3.12 environment.
- Method: installed `pygments==2.19.2` by exact name with **0** direct URL records, then invoked the next frozen sync against the same target path.
- Result: **FAIL caused by command configuration**: the second sync omitted `--python /usr/bin/python3`, selected uv's managed Python **3.10.20**, automatically replaced the target virtual environment, and then reached the same Pygments cache error. No repository file changed, but the temporary target no longer contains the verified Python 3.12 install. To avoid another replacement, the next attempt uses a new target path, explicitly pins `/usr/bin/python3`, and exposes the flat wheel during the single sync transaction.

### Python 3.12 Client Test Environment Attempt 3

- Motivation: test whether a fresh correctly pinned client-dev sync can consume the verified flat Pygments wheel in one transaction.
- Expectation: `--find-links /data/ycfeng/tmp` supplies Pygments while all other locked packages come from uv's offline cache.
- Method: used a new target `/data/ycfeng/tmp/tvcache-client-test-py312`, explicitly pinned `/usr/bin/python3`, and ran frozen offline client sync with the flat index enabled.
- Result: **FAIL before package installation** on the same canonical Pygments URL. This confirms frozen sync continues to enforce the lock's canonical registry artifact and does not use the flat wheel as that cache entry. A fourth frozen-sync variant would repeat the same root cause and is prohibited. The bounded approach changes the test runner rather than the lock: add the client lock's exact pytest packages to the already complete Python 3.12 training environment, run the CPU gate, then restore and verify the frozen training environment.

### Python 3.12 Test Runner Artifact Diagnosis

- Motivation: add only the client lock's exact test-runner packages to the complete training environment.
- Expectation: uv's offline registry cache contains pytest and resolves the remaining pure-Python test dependencies without touching runtime versions.
- Method: requested exact `pytest==8.4.2` and `pytest-asyncio==1.4.0` with network disabled and the verified flat wheel directory available; then inspected all four relevant client lock entries.
- Result: **FAIL before environment modification** because pytest itself is absent from the selected uv cache. The client lock identifies four exact universal wheels: pytest **365,750 bytes**, pytest-asyncio **16,930 bytes**, pluggy **20,538 bytes**, and iniconfig **7,484 bytes**. The root-cause path is to download and verify those four canonical artifacts, then install the exact packages by name from the offline flat index.

### Python 3.12 Full CPU Gate

- Motivation: execute every repository CPU regression under the required Python 3.12 runtime with the complete real training dependency graph.
- Expectation: all 128 tests pass with pytest 8.4.2 and pytest-asyncio 1.4.0, after which the four test-only packages can be removed by frozen sync.
- Method: downloaded pytest, pytest-asyncio, pluggy, and iniconfig from their canonical client-lock URLs; verified all four size/SHA-256 pairs; installed all four by exact package name with no dependency resolution; and ran `python -m pytest -q tests/unit tests/integration` under the 2 GiB scope.
- Result: all four artifacts matched their lock values; the test environment contained **142 distributions** and only the same **2 expected local direct URL records**. The full gate is **128/128 PASS, 0 failed, 1.62 s** on Python **3.12.3**, pytest **8.4.2**, and pytest-asyncio **1.4.0**.

### Frozen Environment Restoration and Lock Gates

- Motivation: leave the training environment exactly frozen after the temporary Python 3.12 test runner and confirm both dependency locks plus repository whitespace.
- Expectation: plain frozen offline sync removes exactly four test-only distributions, restores 138 compatible packages, and both lock checks plus `git diff --check` exit 0.
- Method: reran resource-scoped `uv sync --project train --frozen --offline`; counted distributions and provenance; ran `uv pip check`; ran both project lock checks and `git diff --check`.
- Result: frozen sync removed exactly **4** test-only packages in **2 ms** and restored **138 distributions** with **2 expected local** and **0 registry** direct URL records. `uv pip check` checked **138** packages and found **0 incompatibilities**. Train lock resolved **139 packages in 2 ms**, client lock resolved **28 packages in 1 ms**, and `git diff --check` reported **0 findings**. I-022 through I-030 and I-033 are resolved; Phases 2 and 3 meet their CPU exit criteria pending independent review before Phase 4.

### Independent Pre-GPU Review v3 Dispatch

- Motivation: enforce the required two-lane independent gate after all v2 review findings and Python 3.12 evidence are closed.
- Expectation: architecture/lifecycle and code/spec/security reviewers independently inspect the complete dirty diff and return evidence-backed Phase 4 decisions.
- Method: dispatched read-only `/root/cpu_arch_review_v3` and `/root/cpu_code_review_v3` with separate ownership, exact task documents, baseline commit, source/test scope, and fresh gate metrics; both were instructed to ignore generated bytecode and make no edits.
- Result: both independent reviews are running. Phase 4 remains locked until the architecture lane is `CLEAR` and the code lane is `APPROVE`; any BLOCK or REQUEST CHANGES reopens only the directly affected CPU work.

### Generated-Artifact Cleanup Audit

- Motivation: separate reviewable source/tests from generated worktree artifacts without violating the explicit no-`rm` rule.
- Expectation: quantify untracked bytecode/log output and confirm whether any related server process remains live.
- Method: counted files and bytes under test `__pycache__` directories, inspected only the log metadata, and searched the process list for matching cache-server commands.
- Result: **32** generated bytecode files occupy **249,804 bytes**; `fork_cache_server.log` occupies **15,802 bytes**. No related live server process was found. These files are excluded from review and must not be committed, but deletion is deferred pending explicit user permission (I-034).

### Context Restoration at the v3 Review Gate

- Motivation: resume the existing task without repeating completed CPU work or bypassing the independent pre-GPU gate.
- Expectation: recover the exact interruption point, confirm repository and credential state, and retain Phase 4 as pending until both v3 reviewers approve.
- Method: re-read `requirements.md`, `plan.md`, `harness.md`, `design.md`, `issues.md`, `review.md`, `findings.md`, and the latest `progress.md` entries; inspected the branch/worktree state and credential presence; confirmed both v3 reviewers remain active; and re-read `/data/ycfeng/stepfun-env-handbook/guidence.md`.
- Result: context recovery is **PASS**. The active branch is `task/tvcache-rl-reproduction`; Phases 2/3 remain complete; Phase 4 remains locked pending architecture `CLEAR` plus code/spec/security `APPROVE`; both `TINKER_API_KEY` and `OPENAI_API_KEY` are unset; I-010 and I-034 remain open; the verified future H800 request must use `--charged-group=codesign --private-machine=group --positive-tags=h800 --backoff-limit=1`.

### Remote Model-Archive Capacity Gate

- Motivation: resolve the recorded Phase 4 storage uncertainty before downloading 27.85 GB of model archives.
- Expectation: obtain exact extracted sizes without downloading the full archives and prove that archive-plus-extraction coexistence fits shared storage.
- Method: queried Zenodo record `11031717`, verified byte-range support for both archive endpoints, parsed each remote ZIP central directory in memory, and compared the reported uncompressed totals with current `/data` capacity.
- Result: capacity gate **PASS**. `tool_models.zip` contains **197 files / 14,037,998,498 uncompressed bytes**; `cache_dir.zip` contains **29 files / 18,759,325,160 uncompressed bytes**. The two archives plus both extracted trees require **60,649,150,499 bytes** before filesystem overhead, while `/data` currently has **134 GiB free**. No archive or temporary file was written.

### Independent Pre-GPU Review v3 Verdicts

- Motivation: apply the deterministic pre-GPU gate after the fresh Python 3.12 CPU evidence.
- Expectation: enter Phase 4 only if architecture returns `CLEAR` and code/spec/security returns `APPROVE`.
- Method: collected and independently checked both read-only review reports against the cited executor, fork-bank, sandbox, launcher, model-path, binding, and test code.
- Result: gate **FAIL** — architecture returned **BLOCK** and code/spec/security returned **REQUEST CHANGES**. Confirmed blockers are caller-cwd-dependent VideoAgent assets, unreleased fork-bank cache references, non-transactional prefix environment ownership, partial `copytree` residue, and non-loopback service defaults. Startup-handler and cross-batch warmup ownership remain explicit investigation items. Phases 2/3 are reopened; Phase 4 remains pending.

### v3 Blocker RED Regressions

- Motivation: prove each v3 blocker with a focused executable failure before changing production code.
- Expectation: regressions fail specifically on transactional prefix ownership, fork-bank reference release, partial-copy rollback, caller-cwd-independent asset resolution, and loopback defaults.
- Method: added 14 focused cases across executor, bank, sandbox, runtime-path, sandbox-entrypoint, and TVCache-server tests. The system runner exposed its known missing async plugin; the 4 async nodes were then rerun with `tvcache/client/.venv` (Python 3.10.20, pytest 8.4.2, pytest-asyncio 1.4.0).
- Result: RED is **confirmed**. The 10 synchronous/parameterized cases failed on the intended missing rollback/path/binding behavior, and the 4 async cases failed on the intended old-environment ownership and missing `unref()` assertions. No production file was changed during the RED stage.

### Context Resume and I-040 RED Confirmation

- Motivation: resume at the recorded startup/resource-lifecycle interruption point without assuming the prior in-memory test state.
- Expectation: the two I-040 regressions fail only because startup cleanup excludes failed/unstarted loops and `VideoAgentLoop.stop_sandbox()` does not close its executor and fork-bank client.
- Method: re-read the task source-of-truth documents and current diff, then ran the two exact focused nodes with `tvcache/client/.venv`, `PYTHONDONTWRITEBYTECODE=1`, and `TMPDIR=/data/ycfeng/tmp`.
- Result: RED is **confirmed** with **0/2 passed and 2/2 failed in 0.25 s**. The failed-start loop had `stop_calls=0` instead of `1`; the stopped TVCache loop left `executor.closed=False` instead of `True`. The failures match I-040 and no production file changed during this confirmation.

### v3 Blocker GREEN for I-035 through I-039

- Motivation: remove the five confirmed v3 architecture/code blockers without adding fallback behavior.
- Expectation: VideoAgent assets work outside the module cwd, failed bank deposits release references, prefix switches preserve every owned environment, partial copies roll back, and both services default to loopback.
- Method: made model directories validated absolute inputs; resolved committed static resources from module paths; unified bank reference cleanup; made prefix ownership transfer transactional; rolled back partial copy state; changed service defaults to `127.0.0.1`; and exercised the 14 focused regressions plus their affected test files.
- Result: all five root causes are fixed. The interrupted-session focused gate was **14/14 PASS in 0.31 s** and the affected-file gate was **47/47 PASS in 0.39 s**. The resumed full CPU pytest gate also passed **145/145 in 0.85 s** with no bytecode output.

### I-040 Startup and Resource Cleanup GREEN

- Motivation: prevent a mid-startup failure from leaking handlers or HTTP clients owned by failed and not-yet-started TVCache loops.
- Expectation: cleanup covers every constructed loop, closes executor and fork-bank resources independently and idempotently, and attempts all cleanup operations without hiding errors.
- Method: added idempotence and multi-error RED coverage; changed `run_agent_loops()` to clean the complete input loop set; added per-resource successful-close state to `VideoAgentLoop`; and routed both `run()` and `stop_sandbox()` through one owned-resource cleanup method.
- Result: the expanded RED gate was **1/4 passed and 3/4 failed in 0.31 s** for the intended missing behaviors. After the root-cause change it was **4/4 PASS in 0.24 s**; both affected files were **19/19 PASS in 0.48 s**; the complete CPU pytest gate was **145/145 PASS in 0.85 s**.

### I-041 One-Batch Reachability Decision

- Motivation: decide the cross-batch warmup watch item against the exact required smoke rather than changing a future-only path.
- Expectation: prove whether the fixed one-question/two-rollout configuration can create a next-batch warmup deposit.
- Method: traced the TVCache driver with the recorded smoke overrides `dataset_count=1`, `batch_size=1`, `group_size=2`, and `epochs=1` through `n_train_batches`, `next_batch_idx`, `next_batch_task_ids`, and `VideoAgentLoop._run()`.
- Result: I-041 is **unreachable in this task**. `n_train_batches=1`, initial `next_batch_idx=1`, and `1 < 1` is false; the first loop receives an empty target list and schedules **0 warmup tasks / 0 proactive forks**. Multi-batch driver-wide ownership is deferred in `future.md`; no production behavior was changed.

### Fresh Python 3.12 CPU Gate after v3 Remediation

- Motivation: validate I-035 through I-040 under the exact frozen training runtime before requesting v4 review.
- Expectation: all CPU tests and the real Tinker preflight pass; temporary test packages are then removed; environment, locks, and diff remain clean.
- Method: verified the environment started with 138 distributions and no pytest packages; temporarily installed the four exact client-lock test wheels; ran the full pytest suite and Tinker preflight under Python 3.12.3; restored with frozen offline sync; then ran `uv pip check`, both lock checks, environment/provenance counts, and `git diff --check`.
- Result: **PASS**. Pytest passed **145/145 with 0 failures in 1.60 s**. Preflight emitted **2 datums / 2 sampled tokens**, imported **3/3** drivers, and observed help codes **1,1,1** with output lines **19,19,20**. Frozen sync removed exactly **4** test-only packages; the environment returned to **138** compatible distributions, **2** expected local direct-URL records, and **0** registry direct-URL records. Train/client locks resolved **139/28** packages in **2/1 ms**; `git diff --check` found **0** issues.
### V4 Review Context Recovery and CPU Gate Reopen

- Motivation: resume from the exact v4 review interruption point without repeating the completed 145-test CPU gate or entering Phase 4 with unresolved lifecycle blockers.
- Expectation: recover both independent verdicts, verify their findings against the current source, persist every open issue, and reopen only the affected CPU phases.
- Method: ran the `planning-with-files` session catch-up script with `TMPDIR=/data/ycfeng/tmp`, inspected the branch and task records, recovered the completed reviewer records, and read the relevant `SimpleDictBank.withdraw()` and partial-prefix executor paths.
- Result: session catch-up found no additional unsynchronized context. The v4 architecture/lifecycle lane is **CLEAR**, while the v4 code/spec/security lane is **REQUEST CHANGES** with **0 CRITICAL, 2 HIGH, 0 MEDIUM/LOW**. I-042 records failed fork ownership being dropped by `withdraw()`; I-043 records failed new-fork cleanup ownership being dropped by partial-prefix error paths. Phases 2 and 3 are reopened as **In Progress**, and Phase 4 remains locked. No production code or test was changed in this recovery step.

### I-042 Failed-Withdraw Ownership RED

- Motivation: independently reproduce the reviewer finding and prove that a failed fork remains retryable before changing `SimpleDictBank.withdraw()`.
- Expectation: the first withdrawal attempts `fork-1` and `fork-2`, retains only failed `fork-1` under its original parent, and a later withdrawal retries only `fork-1`.
- Method: added `test_fork_bank_withdraw_retries_only_failed_forks` and ran it alone with `TMPDIR=/data/ycfeng/tmp tvcache/client/.venv/bin/python -m pytest -q tests/unit/test_simple_dict_bank_configuration.py::test_fork_bank_withdraw_retries_only_failed_forks`.
- Result: **RED confirmed — 0/1 passed, 1/1 failed in 0.26 s**. Both forks were attempted once, but the recorded task ownership was `{}` rather than expected `{"root": ["fork-1"]}`. This isolates the root cause to clearing all ownership before cleanup and not restoring failed IDs; no production code changed.

### I-042 Failed-Withdraw Ownership GREEN

- Motivation: preserve retry ownership for only the fork IDs whose stop operations failed, without retrying already cleaned forks or changing the bank's successful withdrawal behavior.
- Expectation: after the first failure, the bank owns only `fork-1`; a second withdrawal retries `fork-1` and never retries successful `fork-2`.
- Method: collected failed fork IDs by original parent during `withdraw()`, merged only those IDs into the current task map under the existing lock before raising cleanup errors, reran the new node, and then ran the complete bank configuration module.
- Result: **GREEN confirmed**. The new regression passed **1/1 in 0.17 s**; the complete module passed **8/8 in 0.18 s**. Observed stop order was `fork-1`, `fork-2`, then retry `fork-1`, with no second `fork-2` stop. I-042 is resolved at the focused-test level; the fresh full CPU gate remains pending.

### I-043 Partial-Prefix Cleanup Ownership RED

- Motivation: independently reproduce every reviewed partial-prefix path in which a new fork exists, its immediate cleanup stop fails, and the executor must retain ownership for `close()`.
- Expectation: setup, cache-reference release, and suffix-execution primary failures each preserve both errors; after the stop fault is cleared, `close()` performs a second stop attempt for the same fork.
- Method: extended the test environment with an explicit `get_id` failure injector, added three focused lifecycle tests for setup, `unref`, and suffix failures, and ran the three nodes together in the locked client test environment.
- Result: **RED confirmed — 0/3 passed, 3/3 failed in 0.30 s**. Each case exposed both its primary error and `stop failed: cached-parent-fork-1`, and each recorded exactly **1** stop before `close()`. After faults were cleared, the observed count remained **1** instead of expected **2**, proving that all three paths lose cleanup ownership. No production code changed in this RED step.

### I-043 Partial-Prefix Cleanup Ownership GREEN

- Motivation: keep every reviewed new partial-prefix fork owned after a failed stop so later structured cleanup can retry it.
- Expectation: setup, `unref`, and suffix failure paths still report their primary and cleanup errors, while `close()` performs a second stop after the injected stop fault is removed.
- Method: in each of the three partial-prefix cleanup exception handlers, appended the failed `forked_env` to `_pending_cleanup_environments` before raising the aggregated lifecycle error; reran the three new nodes and then the complete executor lifecycle module.
- Result: **GREEN confirmed**. The new regressions passed **3/3 in 0.17 s**, and the complete lifecycle module passed **18/18 in 0.20 s**. In every new regression the same fork recorded **1** failed stop before recovery and **2** total stops after `close()`. I-043 is resolved at the focused-test level; the fresh full CPU gate remains pending.

### Fresh Python 3.12 CPU Gate After I-042/I-043

- Motivation: prove that both lifecycle ownership fixes work in the pinned real training environment, do not regress the prior 145 cases, and leave the frozen environment unchanged after testing.
- Expectation: all **149** tests pass; Tinker produces **2** aligned datums and imports **3/3** drivers; frozen restoration removes all **4** temporary test packages; both locks, compatibility, provenance, and diff checks pass.
- Method: verified the restored environment began with **138** distributions and no pytest packages; temporarily installed the four exact client-lock test wheels; ran the complete unit/integration suite and Tinker preflight under Python 3.12.3; restored with frozen offline sync; then ran `uv pip check`, both lock checks, provenance/distribution counts, and `git diff --check`.
- Result: **PASS**. Pytest passed **149/149 with 0 failures in 1.61 s**. Preflight emitted **2 datums / 2 sampled tokens**, imported **3/3** drivers, and observed help codes **1,1,1** with output lines **19,19,20**. Frozen sync removed exactly **4** packages; the environment returned to **138** compatible distributions, **2** expected local direct-URL records, and **0** registry direct-URL records. Train/client locks resolved **139/28** packages in **2/0.98 ms**; `git diff --check` found **0** issues. Phases 2 and 3 are complete again; v5 independent review is next.

### Post-CPU-Gate H800 Readiness Refresh

- Motivation: keep Phase 4 inputs current while the v5 reviewers work, without allocating GPUs before both review gates open.
- Expectation: verify only credential presence, local GPU visibility, and the authoritative launch contract; do not reveal secrets or start a worker.
- Method: reread `/data/ycfeng/stepfun-env-handbook/guidence.md`, checked whether the two required API-key variables are nonempty, and queried local GPU count through `nvidia-smi`.
- Result: the CPU master exposes **0 GPUs**; `TINKER_API_KEY` and `OPENAI_API_KEY` are both **UNSET**. The verified future two-H800 request still requires `--charged-group=codesign --private-machine=group --positive-tags=h800 --backoff-limit=1` and a prior `--predict-only` check. I-010 remains open, and no worker was requested.

### V5 Architecture Review BLOCK

- Motivation: independently verify that the I-042/I-043 remediation closes the reviewed ownership gaps and that no fixed-smoke-reachable lifecycle blocker remains before Phase 4.
- Expectation: I-042/I-043 remain correct, I-041 remains unreachable for the single-batch configuration, and every failed environment stop leaves a retry owner.
- Method: `/root/cpu_arch_review_v3` performed a fresh read-only v5 architecture/lifecycle review and fault-probed the remaining publication and removed-environment cleanup paths.
- Result: **BLOCK**. I-042/I-043 are confirmed fixed and I-041 remains unreachable, but two reachable paths still lose ownership: cache `put` plus unpublished-child stop failure and removed-environment stop failure. Both probes observed **1** stop before `close()` and still **1** after `close()`, instead of expected **2**. I-044/I-045 are open, Phases 2/3 are **In Progress**, and the Phase 4 architecture gate remains closed.

### V5 Code/Spec/Security Review REQUEST CHANGES

- Motivation: independently verify the complete current diff against requirements, lifecycle correctness, fixed-smoke reachability, test adequacy, and credential safety before opening the code gate.
- Expectation: confirm I-042/I-043 behavior, identify only evidence-backed remaining blockers, and find no stored real credential.
- Method: `/root/cpu_code_review_v3` performed a fresh read-only v5 review, ran the four focused I-042/I-043 nodes, fault-probed the adjacent publication/removal cleanup paths, and scanned 64 non-bytecode files for credentials.
- Result: **REQUEST CHANGES** with the same two HIGH blockers tracked by I-044/I-045 and no additional findings. I-042/I-043 passed **4/4 in 0.18 s**. The credential scan found **0** real keys, PEM values, or literal Bearer tokens; six broad matches were placeholders or variable propagation. The Phase 4 code gate remains closed pending RED-to-GREEN remediation and v6 review.

### I-044/I-045 Temporary-Environment Ownership RED

- Motivation: independently reproduce both v5 blockers and prove that error propagation alone does not preserve cleanup ownership.
- Expectation: cache publication child and removed environment each record one failed stop during the primary operation, then a second stop when the fault is cleared and `close()` runs.
- Method: extended the two existing lifecycle failure tests with exact pre-close and post-close stop-count assertions, then ran only those nodes in the locked client test environment with bytecode and pytest cache disabled.
- Result: **RED confirmed — 0/2 passed, 2/2 failed in 0.27 s**. Both environments recorded **1** stop before `close()` and still **1** afterward, instead of expected **2**. This confirms I-044/I-045 share the same root cause: a failed temporary-environment stop does not register a pending owner. No production code changed in this RED step.

### I-044/I-045 Temporary-Environment Ownership GREEN

- Motivation: preserve one structured cleanup owner for every temporary environment whose stop fails, without duplicating owners or changing active rollout-environment ownership.
- Expectation: unpublished publication children, removed environments, and the already covered partial-prefix temporary forks all enter pending cleanup on stop failure; after recovery, `close()` changes stop count from **1** to **2**.
- Method: added `_stop_temporary_environment()`, which awaits stop, registers the object by identity only when stop fails, and re-raises the original error; routed cache publication, removed-environment, and partial-prefix temporary cleanup through that helper; reran the two v5 blocker nodes and the complete lifecycle module.
- Result: **GREEN confirmed**. The blocker nodes passed **2/2 in 0.21 s**, and the complete executor lifecycle module passed **18/18 in 0.24 s**. Both new assertions observed exactly **1** stop before recovery and **2** after `close()`. I-044/I-045 are resolved at the focused-test level; the fresh full CPU gate remains pending.

### Fresh Python 3.12 CPU Gate After I-044/I-045

- Motivation: prove the unified temporary-owner fix works in the pinned real training environment, retains all prior behavior, and leaves the environment exactly restored before v6 review.
- Expectation: all **149** tests pass; Tinker emits **2** aligned datums and imports **3/3** drivers; frozen restoration removes **4** temporary test packages; compatibility, locks, provenance, and diff checks pass.
- Method: verified the environment began with **138** distributions and no pytest packages; temporarily installed the four exact test wheels; ran the complete suite with pytest cache and bytecode disabled; ran the real Tinker preflight; restored by frozen offline sync; then checked packages, both locks, provenance, and the complete diff.
- Result: **PASS**. Pytest passed **149/149 with 0 failures in 1.67 s**. Preflight emitted **2 datums / 2 sampled tokens**, imported **3/3** drivers, and observed help codes **1,1,1** with output lines **19,19,20**. Frozen sync removed exactly **4** packages and restored **138** compatible distributions, **2** expected local direct-URL records, and **0** registry direct-URL records. Train/client locks resolved **139/28** packages in **2/0.91 ms**; `git diff --check` found **0** issues. Phases 2/3 are complete; v6 two-lane review is next.

### Fixed-Smoke Bank Reachability Audit

- Motivation: distinguish fixed-smoke blockers from future multi-batch bank paths and verify that I-042 can actually be retried by its higher-level owner.
- Expectation: the one-batch smoke creates zero deposit tasks, while a failed withdrawal leaves the loop eligible to call withdrawal again.
- Method: traced `n_train_batches`, `next_batch_task_ids`, `VideoAgentLoop._run()` deposit creation, and `stop_sandbox()` state transitions in the current production code.
- Result: with `dataset_count=1`, `batch_size=1`, and `epochs=1`, `n_train_batches=1`; the `next_batch_idx < n_train_batches` branch is false, the first loop receives an empty list, and the other loop receives no `next_batch`, so **0** deposits are created. If `withdraw()` fails, `_sandbox_withdrawn` remains false; a later `stop_sandbox()` attempts withdrawal again. Deposit-specific failed-stop ownership remains a future multi-batch concern under I-041 rather than a fixed-smoke blocker.

### V6 Context Recovery and Architecture BLOCK

- Motivation: resume from the exact v6 review interruption point without repeating the completed 149-test gate or entering Phase 4 with an unowned cache sandbox.
- Expectation: recover the live reviewer state, persist only final evidence-backed findings, and identify the precise ownership boundary before any production change.
- Method: read the task requirements, harness, design, plan, notes, findings, latest progress/issues/review records, ran the planning catch-up script, inspected the complete dirty diff summary, and collected `/root/cpu_arch_review_v3`'s final read-only verdict and probe.
- Result: catch-up found **0** unsynchronized records. The v6 architecture verdict is **BLOCK**. Its successful-publication probe recorded **1 cache put**; before close both parent and child were active, while after `executor.close()` only the parent had stopped and **1 cache-resident child remained active and discoverable**. I-046 is open, Phase 2 is **In Progress**, Phase 3 is **Pending**, and Phase 4 remains closed. The code/spec reviewer is still running; no production code or test changed in this recovery step.

### I-046 Root-Cause Data-Flow Investigation

- Motivation: distinguish the missing final owner from the already fixed failure-path pending owners and avoid an executor-local fix that would destroy parallel rollout reuse.
- Expectation: identify one lifecycle boundary that runs only after all rollouts, preserves cache reuse during execution, detaches cache state atomically, and retains any failed sandbox stop for retry.
- Method: traced successful publication from `AsyncSemanticStatefulExecutor._maybe_put_to_cache()` through `/put` into `ImmutableEnvPrefixTreeCache`, then traced executor, loop, shared rollout, driver, TVCache-server, and sandbox-server teardown paths. Checked tree locks, reference counts, TTL cleanup, and final-batch control flow.
- Result: the root cause is confirmed: successful publication intentionally relinquishes the child object after storing only its `env_id`; executor cleanup cannot stop it without invalidating other rollouts, and no later owner exists. The correct boundary is run-level cleanup after training finishes or errors. The cache must first reject drain while any reference count is positive, then atomically clear the task tree and return its environment IDs. A coordinator must retain IDs whose environment construction or stop fails and retry only those IDs on a later close. Draining per executor or after every successful non-final batch is incorrect because it breaks shared and cross-batch reuse.

### I-046 Task-Drain and Run-Lifecycle RED

- Motivation: prove every missing layer before implementation and ensure the fix cannot stop a cache child while another rollout still references it.
- Expectation: active-reference protection, cache/server/client drain, parallel reuse teardown, run-level retry ownership, error preservation, and driver wiring all fail only because the new lifecycle contract is absent.
- Method: added **11** focused cases across `tests/integration/test_executor_cache_reuse.py`, `tests/integration/test_tvcache_server_schema.py`, `tests/unit/test_async_tvcache_client_fail_fast.py`, `tests/unit/test_tvcache_run_lifecycle.py`, and `tests/unit/test_training_configuration.py`; ran them with `TMPDIR=/data/ycfeng/tmp`, bytecode disabled, and pytest cache disabled in `tvcache/client/.venv`.
- Result: **RED confirmed — 0/11 passed, 11/11 failed in 0.39 s**. Failures were exactly the intended missing contract: no tree `drain_task`, HTTP route returned **404**, no strict async-client method, no run-lifecycle module, and no driver lifecycle wiring. The active-reference case failed on absent drain rather than an unrelated setup error; the successful publication/reuse setup reached the missing coordinator import. No production code changed in this RED step.

### I-046 Task-Drain and Run-Lifecycle GREEN

- Motivation: give successfully published cache environments one final owner without shortening their reuse lifetime or hiding teardown failures.
- Expectation: task drain is reference-safe and atomic at the tree lock; the HTTP/client boundary validates the full schema; final run cleanup stops every detached sandbox, retains failed IDs/tasks for a later close, and preserves simultaneous training and cleanup errors.
- Method: added `ImmutableEnvPrefixTreeCache.drain_task()`, `/drain_task`, strict `AsyncTVCacheClient.drain_task()`, and `TVCacheRunLifecycle`; changed the TVCache driver into a lifecycle-owned wrapper around `_run_training()` and registered every encountered task ID. Reran the **11** RED nodes, then eight affected unit/integration modules, then the complete CPU suite in the existing client test environment with bytecode/cache disabled.
- Result: **GREEN confirmed**. The RED batch passed **11/11 in 0.29 s**; affected modules passed **106/106 in 0.74 s**; the provisional complete suite passed **160/160 in 0.98 s**. The parallel-reuse test observed the published child still alive after both executor closes, then cache env count **1→0** and active deterministic environments **1→0** after run-level close. The failed-stop test observed only the failed environment receive a second stop attempt; the failed-drain test retried only its task. The authoritative Python 3.12 gate and independent v7 review remain pending.

### Fresh Python 3.12 CPU Gate After I-046

- Motivation: verify the task-level drain and run-level teardown contract in the pinned production-like training environment before requesting v7 review.
- Expectation: all **160** tests and the real Tinker preflight pass; frozen restoration removes all **4** temporary test packages; the environment returns to **138** compatible distributions; both locks and the complete diff remain clean.
- Method: confirmed the environment started with **138** distributions and no pytest packages; temporarily installed pytest 8.4.2, pytest-asyncio 1.4.0, pluggy 1.6.0, and iniconfig 2.3.0; ran the complete unit/integration suite and Tinker preflight under Python 3.12.3; restored with frozen offline sync; then checked package compatibility, package provenance, both locks, and `git diff --check`.
- Result: **PASS**. Pytest passed **160/160 with 0 failures in 1.68 s**. Preflight emitted **2 datums / 2 sampled tokens**, imported **3/3** drivers, and observed native chz help codes **1,1,1** with output lines **19,19,20**. Frozen sync removed exactly **4** test packages and restored **138** compatible distributions, **2** expected local direct-URL records, and **0** registry direct-URL records; pytest and pytest-asyncio are both absent after restoration. Train/client locks resolved **139/28** packages in **2/0.95 ms**; `git diff --check` found **0** issues. Phase 3 is complete again; Phase 4 remains locked pending v7 architecture `CLEAR` and code/spec/security `APPROVE`.

### V7 Review Verdicts and Continuation Recovery

- Motivation: resume from the supplied v7 handoff without treating the normal-path 160-test result as proof of response-loss safety.
- Expectation: preserve the independent verdicts, locate the precise interruption point, and reopen only the CPU lifecycle phases affected by the new failure-path blocker.
- Method: re-read the existing task requirements, plan, harness, design, notes, issues, review, summary, test report, current worktree status, and the tree/server/client/run-lifecycle code; reconciled the supplied architecture handoff with the completed `/root/cpu_code_review_v3` result.
- Result: recovery is complete. The v7 code/spec/security verdict is **APPROVE**, but the architecture verdict is **BLOCK**. In the drain response-loss probe, cache count changed **1→0**, lifecycle pending IDs remained **0**, one sandbox remained active, the second drain returned **0 IDs**, and a second `close()` made **0 stop attempts**. In the sandbox-stop response-loss probe, the sandbox was actually deleted, retry raised `FileNotFoundError`, and the pending ID could not converge. I-047 is open; Phase 2 is **In Progress**, Phase 3 is **Pending**, and Phase 4 remains closed. No production code or test changed during recovery.

### I-047 Interface and Ownership Trace

- Motivation: ground the response-loss tests in the real component boundaries before selecting any implementation.
- Expectation: identify exactly where ownership is destroyed and which existing interfaces must carry stable operation identity.
- Method: inspected `SandboxClient.stop_sandbox()`, the Flask `/stop` endpoint, `SandboxManager.stop_sandbox()`, cache construction and `/drain_task`, `AsyncTVCacheClient` reuse after close, and the run lifecycle state machine.
- Result: the hypothesis is confirmed. Cache drain has no `drain_id`, pending record, or ACK; it clears the tree before the response. Sandbox stop has no operation ID or completion record; it removes the directory before the response and rejects later absence. `TVCacheRunLifecycle` removes a task immediately after receiving drain IDs and reconstructs failed environments without any stable stop token. The accepted minimal transaction is therefore one stable drain ID per task, server-retained detached IDs until idempotent ACK, one stable stop ID per environment, and lifecycle ACK only after all stop confirmations.

### I-047 RED Test Matrix

- Motivation: isolate the two response-loss failures and the ACK boundary before touching production code.
- Expectation: focused tests fail only because stable drain identity, retained drain ownership, idempotent stop completion, and ACK state do not yet exist.
- Method: traced every current caller of `SandboxClient.stop_sandbox()` and `ImmutableEnvPrefixTreeCache.drain_task()`, then mapped the smallest regression set across cache/server/client, run lifecycle, and sandbox manager tests.
- Result: the RED batch will cover: same-`drain_id` replay of detached IDs; rejection of a competing drain ID; idempotent drain ACK; client request/response schema for drain and ACK; lifecycle recovery when drain commits before a lost response; ACK retry without repeated stops; and sandbox stop retry after deletion with exactly one filesystem removal. Production code remains unchanged.

### I-047 Commit/Response-Loss RED

- Motivation: prove the accepted retry-safe teardown contract catches the v7 failure before changing production behavior.
- Expectation: every selected test fails on the absent `drain_id`/ACK API, missing lifecycle state, missing stable stop operation ID, or missing sandbox completion record.
- Method: added focused regressions in the existing lifecycle, sandbox manager/client, TVCache client/server, `VideoSandboxEnv`, and cache-reuse test modules; ran 19 selected nodes with `tvcache/client/.venv`, `TMPDIR=/data/ycfeng/tmp`, bytecode disabled, and pytest cache disabled.
- Result: **RED confirmed — 0/19 passed, 19/19 failed in 2.27 s**. Failures were the intended missing contract: tree/client/lifecycle drain signatures lacked `drain_id`; `ack_task_drain` and `/ack_task_drain` did not exist; sandbox manager/client and `VideoSandboxEnv` lacked stop operation IDs; no completed-stop replay existed; and the existing server response omitted `drain_id`. Collection and test dependencies were healthy. No production code changed during this RED step.

### I-047 Existing-Caller Stop Identity RED

- Motivation: preserve the no-cache and stateless-cache callers that currently invoke `SandboxClient.stop_sandbox()` without an explicit operation ID while still requiring every stop RPC to carry stable identity.
- Expectation: two stop attempts for the same sandbox through one client generate one non-empty operation ID and reuse it.
- Method: added `test_sandbox_client_reuses_generated_stop_operation_id` and ran only that node with `tvcache/client/.venv`, `TMPDIR=/data/ycfeng/tmp`, bytecode disabled, and pytest cache disabled.
- Result: **RED confirmed — 0/1 passed, 1/1 failed in 0.09 s**. The first request contained only `sandbox_id`; the fake server raised `KeyError: 'operation_id'`. This isolates the compatibility root cause before production changes.

### I-047 Cache Drain Receipt and ACK GREEN

- Motivation: prevent a committed cache drain from destroying the only copy of detached environment IDs when the HTTP response is lost.
- Expectation: one stable `drain_id` replays the same detached IDs until ACK, a competing ID is rejected, repeated ACK is idempotent, and the async client validates the echoed operation identity.
- Method: added pending and acknowledged drain records under the cache dictionary lock, extended `/drain_task`, added `/ack_task_drain`, updated the async client schema, and ran the two tree regressions, the server schema regression, and all client drain/ACK cases.
- Result: **GREEN confirmed — 9/9 selected tests passed, 18 deselected, in 0.26 s**. Cache count becomes zero only once, same-ID drain replay returns the original IDs, a competing drain remains rejected, and repeated ACK succeeds without restoring or redraining the tree.

### I-047 Run Lifecycle State Machine GREEN

- Motivation: retain caller-side ownership across lost drain, stop, or ACK responses instead of rebuilding each retry from incomplete state.
- Expectation: each task reuses one drain ID, each detached environment reuses one stop operation ID, successful stops are never repeated, and ACK occurs only after all stops for that task succeed.
- Method: replaced the task/environment sets with explicit pending-drain, pending-stop, and pending-ACK maps; generated drain IDs at registration; derived stop IDs from the drain receipt; and ran the complete lifecycle unit module plus the parallel-reuse integration case.
- Result: **GREEN confirmed — 7/7 tests passed in 0.23 s**. Commit-then-response-loss retries reuse identical drain and stop IDs; ACK response loss triggers only a second ACK; a failed stop blocks only its task ACK while unrelated tasks still converge.

### I-047 Sandbox Stop Completion Replay GREEN

- Motivation: make a committed sandbox deletion retryable after its success response is lost, while keeping unknown first-time deletion attempts fail-fast.
- Expectation: the server records a completed stop by operation ID, same-ID replay performs zero additional filesystem removals, a different ID for the missing sandbox raises, and existing callers reuse a stable generated ID.
- Method: added manager-side completion records, required and echoed `operation_id` at the Flask boundary, added stable per-sandbox IDs and response validation in `SandboxClient`, forwarded explicit lifecycle IDs through `VideoSandboxEnv`, and updated the manager's internal cleanup caller.
- Result: **GREEN confirmed — 17/17 selected tests passed in 0.47 s**. The replay test observed exactly **1** `rmtree` call across **2** same-ID stops; the client generated one non-empty ID and reused it; explicit lifecycle IDs reached the sandbox RPC unchanged.

### I-047 Affected and Provisional Full Gates

- Motivation: verify the three protocol layers together and detect regressions outside the selected RED nodes before modifying the frozen Python 3.12 environment.
- Expectation: all seven directly affected modules and the complete unit/integration suite pass in the existing client test environment.
- Method: ran the complete cache reuse, server schema, TVCache client, run lifecycle, sandbox client, sandbox manager, and TVCache loop modules; then ran `tests/unit` plus `tests/integration` with pytest cache and bytecode disabled.
- Result: **PASS**. The affected-module gate passed **68/68 in 0.67 s**. The provisional complete suite passed **173/173 in 1.15 s** under Python **3.10.20**.

### Python 3.12 Environment Lookup Correction

- Motivation: identify the authoritative environment before the final CPU gate without changing package state.
- Expectation: inspect the previously recorded Python 3.12 environment and confirm pytest is absent before temporary installation.
- Method: initially probed a worktree-local `train/.venv`, then stopped after that path returned exit **127**; re-read the existing test report and `task_memory/env_handbook.md`, and inspected `/data/ycfeng/tmp/tvcache-train-py312`.
- Result: the first probe used the wrong path; no environment was modified. The authoritative environment is `/data/ycfeng/tmp/tvcache-train-py312`, uses Python **3.12.3**, contains **138** distributions, and had both pytest packages absent before the gate.

### Fresh Python 3.12 CPU Gate After I-047

- Motivation: prove retry-safe teardown under the pinned production-like training runtime and restore the exact frozen environment before requesting v8 review.
- Expectation: all **173** tests and the real Tinker preflight pass; frozen restoration removes exactly **4** temporary test packages; compatibility, provenance, locks, and diff checks remain clean.
- Method: temporarily installed pytest 8.4.2, pytest-asyncio 1.4.0, pluggy 1.6.0, and iniconfig 2.3.0 from verified offline wheels; ran the full suite and Tinker preflight under Python 3.12.3; restored with frozen offline sync; then checked packages, provenance, both locks, generated-artifact count, and `git diff --check`.
- Result: **PASS**. Pytest passed **173/173 with 0 failures in 4.05 s**. Preflight emitted **2 datums / 2 sampled tokens**, imported **3/3** drivers, and observed help codes **1,1,1** with output lines **19,19,20**. Frozen sync removed exactly **4** packages; the environment returned to **138** compatible distributions, **2** expected local direct-URL records, **0** registry direct-URL records, and no pytest packages. Train/client locks resolved **139/28** packages in **19/1 ms**; `git diff --check` found **0** issues. The existing I-034 bytecode count remains **36**; no generated artifact was deleted without permission.

### Context Restore and V8 Verdict Recovery

- Motivation: resume the existing task at the exact independent-review interruption point without duplicating completed I-047 implementation or opening the GPU phase from stale CPU evidence.
- Expectation: recover the current branch, task records, dirty implementation, both reviewer verdicts, and the precise remaining gate.
- Method: re-read `requirements.md`, `plan.md`, `harness.md`, `design.md`, `notes.md`, `issues.md`, `review.md`, and the latest CPU report; inspected branch status and the complete dirty diff; recovered `/root/cpu_arch_review_v8` and `/root/cpu_code_review_v8`.
- Result: context recovery is **PASS**. The branch is `task/tvcache-rl-reproduction`; the code/spec/security lane is **APPROVE** with **0/0/0/0** findings and **15/15** directed tests passing in **0.38 s**; the architecture lane is **BLOCK**. Phase 2 is reopened, Phase 3 is pending, Phase 4 remains closed, I-047 remains open, and I-034 still requires explicit deletion permission.

### V8 Architecture Blocker Root-Cause Verification

- Motivation: verify the external architecture finding against the actual production call path before changing code.
- Expectation: determine whether the implemented retry-safe state machine is automatically driven by the fixed-smoke entrypoint after an uncertain transport response.
- Method: traced `train/train_with_tvcache.py::main()` through `TVCacheRunLifecycle.__aexit__()`, `close()`, the pending drain/stop/ACK maps, `AsyncTVCacheClient`, `VideoSandboxEnv`, and `SandboxClient`; compared the production path with the manual multi-call lifecycle regressions.
- Result: the finding is **confirmed**. `main()` enters one lifecycle context, and `__aexit__()` invokes `close()` exactly once. One lost drain response leaves pending counts **(1,0,0)** and raises out of the context; the only tests at that boundary call `close()` manually again. The protocol preserves ownership in memory, but production does not converge it. The minimal root-cause target is the existing context-manager exit: reuse the same lifecycle and IDs, retry only `httpx.TransportError`-class uncertainty, and keep HTTP status, schema, validation, and other semantic errors fail-fast.

### I-047 Production Context Convergence RED

- Motivation: reproduce the v8 one-shot production failure at the actual `async with` boundary before changing lifecycle behavior.
- Expectation: one context exit should eventually recover one committed-but-lost drain response, one committed-but-lost sandbox-stop response, and one committed-but-lost ACK response using the original IDs; an HTTP status rejection must still execute exactly once.
- Method: added two lifecycle tests with real `httpx.ReadError` transport failures and `httpx.HTTPStatusError` semantic failure, then ran only those nodes in `tvcache/client/.venv` with `TMPDIR=/data/ycfeng/tmp`, bytecode disabled, and pytest cache disabled.
- Result: **RED confirmed — 1/2 passed, 1/2 failed in 0.26 s**. The semantic 409 case passed with exactly **1** drain and **1** client-close call. The production context case failed on the first lost drain response, with **1** drain, **0** stop, and **0** ACK attempts, proving that `__aexit__()` still does not drive the retained state forward. No production code changed during RED.

### I-047 Production Context Convergence GREEN

- Motivation: make the fixed-smoke production entrypoint use the retry-safe protocol state already retained by the lifecycle, without retrying deterministic server or schema failures.
- Expectation: the same lifecycle instance survives one lost response at each drain/stop/ACK stage, reuses one drain ID and one stop ID, reaches zero pending state, and retries no HTTP status error.
- Method: added a context-exit convergence loop that recognizes only `httpx.TransportError` or a lifecycle aggregate containing only transport errors, waits **1.0 s** between attempts, and otherwise re-raises immediately; reran the two new nodes, the complete lifecycle module, driver configuration plus cache-reuse integration, and the complete provisional CPU suite.
- Result: **GREEN confirmed**. The new nodes passed **2/2 in 0.20 s**; the lifecycle module passed **8/8 in 0.20 s**; adjacent driver/integration tests passed **44/44 in 0.46 s**; the provisional complete suite passed **175/175 in 1.04 s**. The transport probe observed drain calls **2**, stop calls **2**, ACK calls **2**, unique drain IDs **1**, unique stop IDs **1**, retry delays **3**, pending counts **(0,0,0)**, and client-close calls **4**. The semantic 409 probe remained **1** drain and **1** client-close call.

### Fresh Python 3.12 CPU Gate After Production Convergence

- Motivation: verify the entrypoint convergence fix in the pinned production-like training runtime and restore the frozen environment before repeat independent review.
- Expectation: all **175** tests and the real Tinker preflight pass; frozen restoration removes exactly **4** temporary test packages; the environment returns to **138** compatible distributions; package provenance, both locks, and the complete tracked diff remain clean.
- Method: confirmed the environment began with **138** distributions and no pytest packages; installed the four exact offline client-lock test wheels; ran the complete suite and Tinker preflight under Python 3.12.3; restored with frozen offline sync; then checked package compatibility, distribution/provenance counts, both locks, and `git diff --check`.
- Result: **PASS**. Pytest passed **175/175 with 0 failures in 1.80 s**. Preflight emitted **2 datums / 2 sampled tokens**, imported **3/3** drivers, and observed help codes **1,1,1** with output lines **19,19,20**. Frozen sync removed exactly **4** packages; `uv pip check` verified **138** compatible distributions; pytest and pytest-asyncio are absent; local/registry direct-URL counts are **2/0**. Train/client locks resolved **139/28** packages in **2/1 ms**; `git diff --check` found **0** issues. Phases 2 and 3 are complete again; I-047 and Phase 4 remain gated by repeat architecture review.

### V9 Independent Review Verdicts

- Motivation: independently determine whether the production context now closes the v8 one-shot teardown gap before any GPU allocation.
- Expectation: I-047 closes and Phase 4 opens only if architecture returns `CLEAR` and code/spec/security returns `APPROVE`.
- Method: `/root/cpu_arch_review_v8` and `/root/cpu_code_review_v8` performed read-only incremental reviews of lifecycle classification, production wiring, pending-state transitions, primary-error preservation, cancellation, semantic fail-fast behavior, credentials, and focused response-loss probes; neither repeated the authoritative full suite.
- Result: gate **PASS**. Architecture returned **CLEAR** with **0 BLOCK / 0 WATCH**; code/spec/security returned **APPROVE** with **0 CRITICAL / 0 HIGH / 0 MEDIUM / 0 LOW**. Reviewer evidence included lifecycle **8/8 PASS**, production/I-046 **2/2 PASS**, drain/stop/ACK attempts **2/2/2**, unique IDs **1/1**, retry delays **3**, pending **(0,0,0)**, semantic HTTP 409 retry count **0**, cache environments **1→0**, active environments **1→0**, and credential/whitespace findings **0/0**. I-047 is resolved and Phase 4 is open. `UnsupportedProtocol` and `LocalProtocolError` are broader `TransportError` subclasses, but the valid fixed loopback HTTP topology cannot produce them; reviewers classified that invalid-override boundary as outside this fixed-smoke gate.

### Phase 4 Credential and Worker Entry Gate

- Motivation: verify mandatory external credentials and the authoritative GPU launch path before any resource request or secret-bearing process starts.
- Expectation: both `TINKER_API_KEY` and `OPENAI_API_KEY` are present without revealing their values; the CPU master has no local GPU; the verified `rlaunch` path is available; predict-only precedes live allocation.
- Method: re-read `/data/ycfeng/stepfun-env-handbook/guidence.md`, checked only whether the three credential variables are nonempty, counted `nvidia-smi -L` device lines, and located `rlaunch`.
- Result: **BLOCKED before allocation**. `TINKER_API_KEY`, `OPENAI_API_KEY`, and optional `HF_TOKEN` are all **UNSET**; local GPU count is **0**; launcher is `/kubebrain/rlaunch`. The two required keys are needed for Tinker training/sampling and VideoAgent service initialization. Per the blocking protocol, no `--predict-only` or live two-H800 request was issued. Resume only after secure credential injection and explicit user confirmation.
### 2026-09-08 Plan Reconfirmation: Provider-Backed H200 Rollout

- Motivation: replace the unavailable and unfunded Tinker path while preserving a real model-driven measurement of local TVCache behavior.
- Expectation: provider inference stays separate from local tool execution, sandbox lifecycle, and cache accounting; the first GPU case uses H200 `step_main`.
- Method: completed the `grill-me` decision sequence against the current agent loop, tool schema, sandbox API, and TVCache executor boundaries.
- Result: **CONFIRMED**. StepCode `deepseek-v4-flash` is the model provider, the specified StepCast vLLM image is the OpenAI-compatible runtime layer, the local agent loop owns `Response` parsing and `role=tool` result replay, and no-cache/TVCache each run two rollouts for one fixed EgoSchema question. RL optimizer updates are outside this round. Implementation and provider protocol smoke are pending.
### StepCode Provider Migration and Transport Adapter

- Motivation: make the confirmed provider boundary executable without Tinker: StepCode supplies model output, while local VideoAgent and TVCache own tool execution.
- Expectation: remove OpenAI visual fallbacks, require StepCode configuration, and provide a strict OpenAI-compatible chat transport that preserves `role=tool` messages and structured-output requests.
- Method: changed `sandbox_manager.py`, `captioning.py`, and `tools.py`; updated the stale migration assertions to the StepCode environment; added `tests/unit/test_provider_chat_client.py`; ran focused and affected tests.
- Result: provider migration passed **27/27**; adapter RED was **3/3 failures** before implementation and GREEN is **3/3 passed** after implementation. Provider endpoint/structured-output runtime smoke and provider rollout integration remain pending.

### EgoSchema Video Acquisition and H200 Asset Gate

- Motivation: provide one fixed real EgoSchema input for the approved no-cache versus TVCache provider rollout comparison without downloading the full dataset.
- Expectation: obtain a valid video whose metadata and checksum match a committed EgoSchema row, then verify all runtime assets before allocating a long-lived worker.
- Method: selected the first processed-video row whose raw video was available from `VLM2Vec/egoschema-rawvideo` after Google Drive repeatedly timed out; downloaded through the company HTTP proxy; checked the file with `ffprobe` and SHA-256; wrote `egoschema_manifest_2026-09-08.json`.
- Result: video `0c481667-9303-4f4a-b331-0b412aaafa2d.mp4` is **5,732,750 bytes**, H.264, 480x360, 30 fps, **180.0 seconds**, SHA-256 `db2bb94ff43ccb040fe5fd117e19e6f907e9065d74ec7276596a9c8ba4d554af`. The manifest records question, five options, correct index `1`, source URL, and persistent path `/data/ycfeng/tvcache_assets/egoschema/run-20260908/videos/0c481667-9303-4f4a-b331-0b412aaafa2d.mp4`.

### H200 `step_main` Video-Agent Asset Gate

- Motivation: determine whether the specified H200 worker can start the existing VideoAgent sandbox and execute a real visual tool with the downloaded sample.
- Expectation: the worker exposes the required model/runtime/preprocessing directories, or the absence is reported before a rollout claim is made.
- Method: launched the specified StepCast image on H200 `step_main` with `/data` mounted and the controlled StepCode credential; verified `nvidia-smi`, credential presence, video metadata, and candidate model directories. The first attempt used a duplicated bash argument and exited `126`; the corrected entrypoint form reached `Ready` and completed the asset preflight before being interrupted during an unnecessarily broad filesystem scan.
- Result: H200 and credential gates passed (`GPU 0: NVIDIA H200`, `STEPCODE_API_KEY=SET`). The worker exposed the downloaded video but no `/models`, `/data/models`, VideoAgent model directory, Video-LLaVA runtime, or EgoSchema preprocessing cache. Code inspection confirms `SandboxManager.__init__` constructs `Captioning`, `SegmentFeature`, and `Tracking`, each loading local weights, while `ToolKit` requires viCLIP and Video-LLaVA assets. The real visual tool-chain therefore cannot start under the current decision to avoid downloading local model weights; no fake tool result or incomplete rollout was recorded.

### 2026-09-09 Continuation: Download Routing and Provider Accounting

- Motivation: resume asset preparation and ensure real rollout metrics reflect provider inference and local tool execution.
- Expectation: finish verified assets, retain token usage, and export final reward/cache/fork counters correctly.
- Method: verified stale Git lock ownership and removed only the already-authorized old index lock; committed the H200 probe/report as `88446ab`. Compared official download paths using 1 MiB range reads. LaViLa direct returned HTTP 206 in 0.37 s; proxy failed after 21.52 s. PyTorch PyPI direct returned HTTP 206 in 3.42 s; proxy hit a 10.04 s read timeout. Added domain-specific NO_PROXY entries while retaining the company proxy. Both old 600 s installers expired before installation; restarted the same pinned dependency sets with four concurrent downloads and MemoryMax=2G.
- Result: ViCLIP completed at 1,710,545,812 bytes and SHA-256 `7a4d6ad6eac6632db3693f4b97f9f8f6445b65b1e139a6fc6686150522238c56`, matching official metadata. Runtime symlink is ready. LaViLa and Video-LLaVA remain in progress. Xet logged repeated transfer failures while final blobs stayed empty; the verified HTTP path with direct CDN access now writes resumable `.incomplete` blobs. Xet's cumulative transport counter is not treated as completed checkpoint bytes.
- Provider accounting root cause: client discarded usage; loops did not synchronize final_answer; baseline omitted execution counters; TVCache returned a pre-execution stats snapshot. The executor itself updates counters correctly, so no executor accounting change is needed.
- Method: preserved complete()'s string result and recorded validated usage in the client. Synchronized final answers, counted successful no-cache tool executions, and returned the final executor/fork-bank snapshot. Ran the controlled production-loop accounting probe before and after the fix.
- Result: before the fix both loop rewards were 0 against result reward 1.0, and both returned tool_executions 0. After the fix both rewards are 1/1.0 and tool_executions/cache_misses/total_calls are 1/1/1; merged TVCache environment_forks is 3 (executor 1 plus fork bank 2). Probe: `tests/e2e/provider_loop_metrics_probe.py`; logs: `/data/ycfeng/tmp/tvcache-provider-metrics-{red,green}-20260909.log`. Client checks passed 8/8 in 0.07 s. A live provider call returned prompt/completion/total 113/49/162, reasoning 43, cached prompt 0. Details are in `test_report_2026-09-09_provider_usage.md`.
- Pending: downloads and both installations; model constructors; GPU services/tool smoke; no-cache 2 rollouts; TVCache 2 rollouts; GPU memory sampling, cleanup evidence and final report. The new `tests/e2e/provider_cache_rollout.py` is an execution entrypoint under preparation, not evidence of completed real rollouts.

### 2026-09-09 Follow-through: H200 Capacity and Download Route

- Motivation: distinguish capacity blockage from slow CPU-host asset transfer before considering worker migration.
- Expectation: use H200 when available; move download execution only with measured worker network evidence.
- Method: fresh predict-only requested 1 H200/8 CPU/65,536 MiB and returned gpu-h200-0301 with 7 available GPUs. A short worker used the specified StepCast image and a bounded 8 MiB mirror range request.
- Result: allocation reached Ready in 24 s after creation; direct hf-mirror.com connection failed with ConnectTimeout (10 s configured). Launcher exit 1 and RJob final phase Failed were confirmed. The failed direct-worker-download branch is stopped; CPU downloads remain active. No H800 fallback is needed on the observed capacity evidence.
- Asset routing: hf-mirror.com returned the pinned config and matching official image/video tower SHA-256 and sizes. Download preparation now feeds the existing ranged downloader into the normal HF blob cache, then uses snapshot_download for small metadata and snapshot links. Final LFS SHA-256 validation remains mandatory. Current output log is /data/ycfeng/tmp/tvcache-videollava-download-20260909-ranged.log; prior `.incomplete` files are retained.
- Additional dependency: exact OpenAI CLIP source revision d05afc436d78f1c48dc0dbf8e5980a9d471f35f6 was downloaded to /data/ycfeng/tmp/tvcache-clip-source/CLIP-d05afc436d78f1c48dc0dbf8e5980a9d471f35f6. Install it with --no-deps into the completed VideoAgent environment; include the repository Video-LLaVA root on PYTHONPATH for the VQA environment.
- Commit: provider usage client, its selected tests, and live report committed as f6935a2. Loop accounting corrections and the real-rollout execution script remain in the worktree for integration. The execution script's --help imported successfully; this is CLI readiness only. An earlier import-only diagnostic timed out at 60 s; the subsequent controlled direct production-loop run completed and supplied the actual accounting evidence.

Checkpoint metrics: `{"timestamp": "2026-09-09T17:15:06.757008+08:00", "free_bytes": 121024778240, "lavila_completed_part_bytes": 926941184, "lavila_total_bytes": 1325978405, "lavila_percent": 69.91, "videollava_completed_range_bytes": 150994944, "videollava_inflight_range_bytes": 15728640, "videollava_total_required_lfs_bytes": 18759164360, "real_no_cache_rollouts": 0, "real_tvcache_rollouts": 0}`. Download PIDs and installer commands can be recovered with `pgrep -af "download_ranged_asset|download_videollava_assets|uv pip install"`; current log names are recorded above.

Selected LFS inventory correction: all selected LFS files total **18,759,664,083 bytes**, including the tokenizer, as computed from the pinned metadata and the downloader allow_patterns. The checkpoint above reports **18,759,164,360 bytes** for the four large model weight files only.

### 2026-09-09 Follow-through: LaViLa checkpoint complete

- Motivation: close the VideoAgent asset prerequisite before constructor and service smoke checks.
- Expectation: ranged downloader produces the exact official checkpoint with verifiable size and digest.
- Method: retained resumable downloader output and ran `stat`, `sha256sum`, and `md5sum` on the completed `.pth` file.
- Result: file size is 1,325,978,405 bytes; MD5 is 68a71f28ef211469a6dcd98f1638347d, matching the official filename metadata. Video-LLaVA and both Python environments remain in progress.

### 2026-09-09 Follow-through: Maven mirror clarification

- Observation: user-provided Artifactory mirror is a Maven repository (`maven-public`) for Java/Gradle artifacts. Current blocked downloads are Python wheels and Hugging Face LFS blobs, so this mirror does not apply to the active `uv pip` or HF downloader commands.
- Action: retained the verified company HTTP proxy and existing resumable routes; did not substitute the Maven URL for a Python index.
- Result: Video-LLaVA ranged downloader advanced to ranges around 2.98 GB and continues retrying HTTP errors; both uv installers remain active.

### 2026-09-09 Follow-through: Basemind Python mirror installation

- Motivation: replace stalled public PyPI downloads with the company mirror requested by the user.
- Method: verified mirror package indexes, then ran both pinned environment installs with `--index-strategy unsafe-best-match`, `--index-url`, `--extra-index-url`, trusted hosts, and MemoryMax=2G.
- Result: VideoAgent environment installed torch 2.1.2/torchvision 0.16.2/transformers 4.27.0/decord 0.6.0; Video-LLaVA environment installed torch 2.0.1/torchvision 0.15.2/transformers 4.31.0/decord 0.6.0. Fixed-revision CLIP source installed after adding setuptools with `--no-build-isolation`. CPU import smoke passed; model constructors require CUDA and remain scheduled for H200 worker validation.

### 2026-09-09 Follow-through: Artifactory Hugging Face endpoints

- Motivation: prefer the company Hugging Face proxy before falling back to the public mirror.
- Method: probed both `huggingface-mirror` and `huggingface-remote` through the company proxy. Pinned Video-LLaVA `config.json` and `model.safetensors.index.json` returned HTTP 200 quickly on both endpoints. A 1 MiB range request for `model-00001-of-00002.safetensors` timed out without headers on both endpoints.
- Action: stopped the old `hf-mirror.com` downloader and started the pinned downloader with `HF_ENDPOINT=https://artifactory.stepfun-inc.com/artifactory/api/huggingfaceml/huggingface-mirror`, 86400-second HF timeouts, XET disabled, and an endpoint-specific cache path via `TVCACHE_HF_CACHE`.
- Result: metadata is available; large LFS ranges currently retry with `ReadTimeout`, so no large-file success is claimed. If this route remains stalled, switch the same isolated cache to `huggingface-remote` and retain final SHA-256 validation.

### 2026-09-09 Follow-through: official Hugging Face fallback

- Motivation: use the documented official route after both company Artifactory endpoints failed to return large LFS ranges.
- Method: verified the official pinned shard with a proxied 1 MiB Range request: HTTP 206 and 1,048,576 bytes. Reused the existing 4.9 GiB resumable cache after updating its generated manifest URL from `hf-mirror.com` to the official pinned URL; no task-created assets were deleted.
- Result: official downloader is active through the company proxy. The existing parts directory is growing (1235 to 1240 parts during observation), so the fallback is making incremental progress. Final size and SHA-256 remain pending.

### 2026-09-09 Follow-through: official download progress checkpoint

- Observation: official proxied downloader remains alive and the main Video-LLaVA parts directory increased from 1235 to 1313 completed 4 MiB parts; cache size is approximately 5.2 GiB.
- Result: fallback route is working incrementally despite retry noise. The 9.98 GB shard and remaining pinned assets are not complete yet; model validation and rollout remain pending.

### 2026-09-09 Follow-through: official downloader resumed

- Observation: after restart, the official proxied downloader remains alive for 8+ minutes and completed parts increased from 1564 to 1590; cache is 6.3 GiB with 88 GiB free.
- Result: download is progressing slowly and remains incomplete. No model integrity or rollout claim is made yet.

### 2026-09-09 Follow-through: downloader checkpoint

- Observation: official downloader has remained alive for 19 minutes; completed main-shard parts increased to 1626 (an additional 36 parts since the previous checkpoint).
- Result: route continues to make slow progress. Disk monitoring remains active at approximately 88 GiB free; asset completion and SHA-256 verification are pending.

### 2026-09-09 Follow-through: downloader checkpoint

- Observation: official downloader remains alive for 35 minutes; main-shard parts increased to 1658.
- Result: incremental progress continues, but the shard remains incomplete and the 88 GiB free-space margin is unchanged at this checkpoint.

### 2026-09-09 Follow-through: downloader concurrency control

- Motivation: main-shard throughput fell to one new part in roughly 20 minutes.
- Method: added `TVCACHE_DOWNLOAD_WORKERS` with default 8, stopped the stalled worker, and restarted the official fallback with `TVCACHE_DOWNLOAD_WORKERS=32` against the same cache.
- Result: after the first minute the process is alive in I/O wait but the part count remains 1659; the upstream route remains the bottleneck. Existing parts are preserved.

### 2026-09-09 Follow-through: 32-worker progress

- Observation: official downloader with `TVCACHE_DOWNLOAD_WORKERS=32` has run for about 6 minutes and increased completed parts from 1659 to 1703.
- Result: concurrency adjustment improved throughput; the main shard remains incomplete, but the official fallback is actively progressing. Disk remains approximately 88 GiB free.

### 2026-09-09 Follow-through: 32-worker progress

- Observation: official downloader has run about 24 minutes; completed parts increased to 1828 and cache size reached 7.2 GiB.
- Result: main shard continues progressing. A transient `du` race saw a worker temporary part disappear during inspection; the downloader remains alive and disk is approximately 88 GiB free.

### 2026-09-09 Follow-through: exact download accounting and runtime paths

- Motivation: replace directory-entry estimates with completed-part bytes and unblock runtime preparation during the download.
- Method: counted only `part-<numeric index>` files whose sizes match the manifest range; excluded manifest and temporary files.
- Result: 1,829 complete parts, 7,671,382,016 / 9,976,576,392 bytes (76.89%) for the first shard. Previous entry-count checkpoints included transient files and are approximate, not verified completed-part counts. SHA-256 remains pending.
- Motivation: the verified LaViLa checkpoint was absent from the selected runtime model directory.
- Expectation: the model wrapper resolves the existing checkpoint without downloading or duplicating it.
- Method: created the missing runtime symlink from `/data/ycfeng/tmp/videoagent_small/LaViLa/` to the completed checkpoint in `/data/ycfeng/tmp/videoagent_small_clean/LaViLa/`.
- Result: runtime path resolves to 1,325,978,405 bytes. Prepared `/data/ycfeng/tmp/tvcache-real-rollout-20260909/{sandboxes,egoschema-cache,videollava-runtime}`. CPU wrapper import check remains active (session 50995); observed `lock_page_killable` wait is evidence of a file-page wait, not proof of a network bottleneck or successful import.

### 2026-09-09 Follow-through: exact progress checkpoint

- Observation: strict completed-part accounting increased to 1,909 parts, 8,006,926,336 / 9,976,576,392 bytes (80.26%). The official downloader remains alive.
- Observation: the CPU wrapper import probe is still blocked in `wait_on_page_bit_common` after 5+ minutes; it has produced no PASS/FAIL output. This is recorded as incomplete evidence, not a pass.

### 2026-09-09 Follow-through: first Video-LLaVA shard complete

- Result: main shard assembled at exactly 9,976,576,392 bytes and SHA-256 `0e342ae2c6d40d6ebba3328904310a00a2b82e57c728e0e4f5059fe6f7774a03`, matching pinned metadata.
- Observation: downloader advanced to the second shard (`4,957,139,888` bytes); its parts directory grew from 2 to 40 parts during observation. Snapshot and offline loader remain pending until all three repositories finish.

### 2026-09-10 Tracking import and H200 constructor validation

- Motivation: complete the outstanding Tracking import and validate already-available VideoAgent weights during the independent Video-LLaVA download.
- Expectation: import all wrappers; load each real model on CUDA with positive allocated memory and preserve measured times.
- Method: direct Tracking import with faulthandler, 180 s deadline, and MPLCONFIGDIR under task temporary storage. Observed font-cache building and a stack inside PyTorch import.
- Result: Tracking import PASS in 80.402 s, exit 0. Prior 60 s checks did not allow enough startup time; no Tracking source change was required.
- GPU method: verified launcher surface; predict-only 1 H200/8 CPU/65536 MiB step_main reported 3 candidates. Submitted `tvcache-constructors-20260910-a` using the specified StepCast image and new `tests/e2e/videoagent_constructor_probe.py`. Node gpu-h200-0301 reached Ready; results pending. Logs: `/data/ycfeng/tmp/tvcache-constructors-20260910{,-launch}.log`. The probe records per-wrapper seconds and allocated/peak CUDA memory.
- Asset snapshot: second Video-LLaVA shard reached 1,283,457,024 / 4,957,139,888 bytes; first shard remains verified. Download PID 3177879 was alive.

- Launcher correction: job `tvcache-constructors-20260910-a` produced only START Captioning. The local 60 s timeout returned 124 and launcher explicitly logged `Stopping rjob reason=interrupt`; platform Succeeded does not establish a constructor pass. Re-submitted as `tvcache-constructors-20260910-b` with a 1200 s launcher limit and 900 s worker-command limit. It was scheduled on gpu-h200-0301. Result and logs remain pending; session 72065 monitors the live launcher.

- Job b reached Ready and emitted CAPTIONING MODEL LOADING; constructor execution is active. Keep launcher session 72065 alive; all model PASS rows and JSON are still pending.

### 2026-09-10 Follow-through: H200 VideoAgent constructors passed

- Motivation: validate all selected VideoAgent wrappers with real local weights on the target GPU before service startup.
- Method: submitted `tvcache-constructors-20260910-b` on H200 `step_main` using the specified StepCast image and `videoagent_constructor_probe.py`; used a 1200 s launcher limit after the first 60 s interrupt.
- Result: RJob Succeeded and `PASS constructors=3`. Captioning 101.813625 s / 1,326,561,280 B; SegmentFeature 102.358984 s / 1,712,142,848 B; Tracking 30.771758 s / 448,610,304 B. Report: `test_report_2026-09-10_videoagent_constructors.md`.

### 2026-09-10 Follow-through: second shard checkpoint

- Observation: first Video-LLaVA shard remains complete and verified. Second shard increased to 3,137,339,392 / 4,957,139,888 bytes (63.29%, 748 complete parts); downloader PID 3177879 remains alive.
- Result: remaining pinned assets are still downloading; offline loader and VQA service remain pending.

### 2026-09-10 Follow-through: second shard checkpoint

- Observation: second shard increased to 3,531,603,968 / 4,957,139,888 bytes (71.24%, 842 complete parts); downloader remains alive for 1h11m.
- Disk: free space decreased to approximately 71 GiB as additional model parts accumulated; this remains sufficient for the remaining 1.43 GiB second-shard data plus pinned tower assets, but monitoring remains required.

### 2026-09-10 Follow-through: second shard checkpoint

- Observation: second shard increased to 4,135,583,744 / 4,957,139,888 bytes (83.43%, 986 complete parts); downloader remains alive for 1h23m.
- Disk: free space approximately 70 GiB.

### 2026-09-10 Follow-through: second shard near completion

- Observation: second shard reached 4,948,751,280 / 4,957,139,888 bytes (99.83%, 1180 complete parts); downloader remains alive.
- Result: only 8,388,608 bytes remain in the second shard. LanguageBind tower downloads have not started yet; disk free approximately 69 GiB.

### 2026-09-10 Follow-through: Video-LLaVA shards verified

- Result: second shard assembled at exactly 4,957,139,888 bytes; SHA-256 `fb5c47457569d61be0d2b2d5739f1e30985acc5a61160406880fee64d2c8e111` matched pinned metadata. Together with shard 1, both Video-LLaVA model shards are complete.
- Observation: downloader advanced to `LanguageBind_Image/pytorch_model.bin`, currently 998,244,352 / 1,710,619,975 bytes (58.36%).

### 2026-09-10 Follow-through: LanguageBind Image complete

- Observation: `LanguageBind_Image/pytorch_model.bin` reached exactly 1,710,619,975 / 1,710,619,975 bytes (100%).
- Result: downloader advanced to `LanguageBind_Video_merge/pytorch_model.bin`; its pinned manifest is now present. Both Video-LLaVA shards and the Image tower are complete; final tower completion, SHA-256 and offline loader remain pending.

### 2026-09-10 Offline loader preparation and H200 submission

- Motivation: finish the pinned asset gate and exercise the production four-bit loader.
- Expectation: resolve all assets offline, construct both towers on CUDA, and record numeric memory/time values.
- Method: verified 8 Video-LLaVA, 8 Image tower, and 7 Video tower files against pinned metadata; checked all three main refs. The prior claim that empty `find -type f` output proved missing snapshots was unsupported: HF snapshot entries are symlinks. The resumed downloader reported existing complete blobs and all three completed snapshots; no snapshot-loss root cause is established.
- Result: 23 required files exist and match metadata sizes. Video merge blob is 2,114,828,105 bytes with SHA-256 ef677a2ffe018ff22021dd166bc26ffe9196eb414626cbd9a2ac7231308bd52d (previous direct checksum). Prepared runtime/cache_dir symlink to reuse the cache through upstream LanguageBind's explicit relative cache path. HF and Transformers global cache variables cover the tokenizer path.
- Method: added direct `tests/e2e/videollava_offline_probe.py`; submitted `tvcache-videollava-offline-20260910-a`, 1 H200 / 8 CPU / 65536 MiB, step_main, specified StepCast image. Prediction reported two candidate nodes. Scheduled node: gpu-h200-0264.lgcm.sh.istep.fun. Worker command deadline: 1200 seconds. Output: videollava_offline_20260910.json; log: /data/ycfeng/tmp/tvcache-videollava-offline-20260910-a.log.
- Result: GPU loader execution pending. Disk free: approximately 51 GiB. Real rollouts remain pending.

- Launcher correction: job a was interrupted by the local 60-second launcher timeout at 14:00:58 +08:00, exit 124. Platform phase Succeeded with an empty loader log is not a loader PASS. The current CLI maintained an attached session despite --detach; this repeats the constructor-a timeout trap already recorded above.
- Method: submitted job `tvcache-videollava-offline-20260910-b` with the previously verified foreground launcher pattern, 1800-second launcher deadline and 1200-second worker command deadline. Launcher session 1129; logs /data/ycfeng/tmp/tvcache-videollava-offline-20260910-b{,-launch}.log. Awaiting allocation and loader output.

- Authorized resource migration: H200 job b remained Pending with reason `RJob is queuing` at 14:03:46 +08:00. H800 codesign predict-only returned 10 candidate nodes. Applied the user's explicit H200-unavailable -> H800 instruction: intentionally stopped the pending H200 job with reason `other:Authorized H800 migration`, then submitted `tvcache-videollava-offline-h800-20260910`. This is an intentional migration, not an unexpected worker failure or model error. Launcher session 46253; same 1 GPU/8 CPU/65536 MiB, 1800 s launcher, 1200 s command. Output videollava_offline_h800_20260910.json; logs /data/ycfeng/tmp/tvcache-videollava-offline-h800-20260910{,-launch}.log.

### 2026-09-10 H800 loader dependency failure

- Motivation: exercise the real loader after asset validation.
- Method: H800 job tvcache-videollava-offline-h800-20260910 ran on gpu-h800-0268.host.platform.shaipower.com; command exited 1 although the platform phase is Succeeded. Full log: /data/ycfeng/tmp/tvcache-videollava-offline-h800-20260910.log.
- Result: FAIL before weight loading: bitsandbytes/functional.py imports scipy.stats, but scipy was absent. Installed bitsandbytes 0.41.0 metadata has no Requires-Dist declaration for scipy. Also observed a Torch sm_90 compatibility warning; CUDA kernel behavior remains unverified and is not inferred from the warning alone.
- Fix motivation: supply the directly imported dependency using the existing compatible VideoAgent version. Expectation: loader import advances past scipy.stats.
- Method: installed scipy==1.15.3 from Basemind mirrors into the Video-LLaVA venv while pinning existing numpy==1.26.2. SciPy declares Python >=3.10 and numpy>=1.23.5,<2.5. Result: installer exit 0, one package installed, 35.9 MiB downloaded; Torch unchanged. Direct loader import verification is running.

- Verification result: direct loader import PASS after SciPy installation, Python command exit 0. Versions: SciPy 1.15.3, Torch 2.0.1+cu117 / CUDA build 11.7. Log /data/ycfeng/tmp/tvcache-videollava-import-20260910.log. CPU-only bitsandbytes warnings are not a GPU pass.
- Next direct GPU execution: `tvcache-videollava-offline-h800-20260910-b`, launcher session 14195, same resource allocation and deadlines. Output remains videollava_offline_h800_20260910.json (no successful prior result exists). Logs /data/ycfeng/tmp/tvcache-videollava-offline-h800-20260910-b{,-launch}.log.

- GPU revalidation b result: FAIL at first shard quantization, command exit 1, CUDA `no kernel image is available for execution on the device` at torch.zeros. The actual venv is Torch 2.0.1+cu117 (architectures through sm_86), unlike the separately verified image Torch. All GPU probe commands have ended; no complete offline-loader JSON exists. Identified CUDA-build mismatch; investigating same-version CUDA 11.8 wheel availability.

- CUDA-build repair route: official PyTorch CUDA 11.8 index direct access returned the exact torch 2.0.1+cu118 and torchvision 0.15.2+cu118 cp310 Linux wheels; proxied TLS timed out. URLs with official hashes are stored in /data/ycfeng/tmp/tvcache-cu118-wheel-manifest-20260910.json. Installing exactly these two wheels with uv --no-deps, preserving other packages, under a 2 GiB master memory cap. Session 56098. Torch wheel 2.1 GiB; torchvision 5.8 MiB. Disk free approximately 50 GiB. GPU revalidation is pending.
- Evidence report: test_report_2026-09-10_videollava_offline.md records the 23-file asset PASS and loader failures separately, with commands, pinned revisions, hashes and failure logs.

- Transfer optimization: direct official wheel Range probe returned HTTP 206, exactly 1,048,576 bytes, Content-Range bytes 0-1048575/2267321259. Stopped the task-owned single-stream uv preparation before installation; no Torch replacement was reported. Reused `download_ranged_asset.download` with 16 workers/4 MiB parts and the official index SHA-256. Session 58245; /data/ycfeng/tmp/tvcache-cu118-ranged-20260910.log; output /data/ycfeng/tmp/tvcache-cu118-wheels-20260910. Plan: install verified local wheels with uv --no-deps --offline, then rerun the GPU loader.

- Download checkpoint: reused completed ranges and resumed with 64 workers, session 10367, log /data/ycfeng/tmp/tvcache-cu118-ranged64-20260910.log. At the checkpoint, 38 complete 4 MiB parts = 159,383,552 / 2,267,321,259 bytes (7.03%); temporary bytes are excluded. Two ranges logged first-attempt ReadTimeout and entered the existing bounded retry path. Environment remains Torch cu117 until a verified cu118 wheel is installed.
- Alternative public route measurement: mirror.sjtu.edu.cn returned HTTP 206 for a 1 MiB wheel range with matching total size 2,267,321,259 bytes, but took 24.413 seconds. Kept the official route; no faster replacement was demonstrated. The official download.pytorch.org domain took 59.955 seconds for 1 MiB; downloader uses the official index's download-r2.pytorch.org URLs.
- Remaining chain: finish cu118 wheel download/hash -> offline wheel installation -> real GPU loader PASS -> launch VQA/sandbox/cache with controlled provider environment -> tool smoke -> no-cache x2 -> TVCache x2 -> metrics, teardown, review and final summary. No real rollout has run; no performance or cache-hit claim is supported yet.

### 2026-09-10 Continuation: runtime wheel resume and executable service preparation

- Motivation: resume the incomplete cu118 wheel and use download time to prepare the already-planned local tool/service execution.
- Expectation: reuse complete parts, finish official SHA-256 verification, then install locally before the next GPU loader.
- Method: previous download process had ended; resumed the same manifest with 64 workers and a 1800 s deadline. New session 70765, PID 278197, log /data/ycfeng/tmp/tvcache-cu118-resume-20260910.log.
- Result: start checkpoint 297 parts / 1,245,708,288 bytes (54.94%); latest checkpoint 308 parts / 1,291,845,632 bytes (56.98%) of 2,267,321,259. The downloader reports transient ReadTimeout retries. The environment still uses cu117 until wheel installation.
- Preparation motivation: proceed directly to services and real tools once the offline loader passes.
- Method: added tests/e2e/videoagent_tool_smoke.py to execute start, five real video commands, and stop with per-call HTTP status/results/durations; added tests/e2e/run_real_video_rollouts.sh to configure the two-GPU worker, inject the existing key into environment without logging its value, start VQA/sandbox/cache, record GPU memory, invoke the tool smoke and the existing no-cache x2 / TVCache x2 driver, and terminate owned service process groups on exit.
- Result: Python AST and bash -n syntax checks passed. Confirmed flask/httpx are available in the controller venv. These are prepared execution scripts, NOT live-passed tool/service/rollout evidence. No code commit is claimed for this unfinished substep. Loader compatibility remains the prerequisite for GPU execution.

- Download checkpoint: 346 complete parts, 1,451,229,184 / 2,267,321,259 bytes (64.01%). Official torch cu118 SHA-256: a7a49d459bf4862f64f7bc1a68beccf8881c2fa9f3e0569608e16ba6f85ebf7b. torchvision cu118 SHA-256: 19ca4ab5d6179bbe53cff79df1a855ee6533c2861ddc7389f68349d8b9f8302a. Hashes are expected values from the official index; completed wheel verification is still pending.

### 2026-09-10 Continuation: cu118 Torch wheel verified

- Motivation: finish the authorized same-version CUDA-build repair after the real Hopper loader failure.
- Expectation: install only verified local Torch/torchvision cu118 wheels, then revalidate the production loader.
- Method: retained the running resumable download and complete parts. Torch assembled at 2,267,321,259 bytes; official SHA-256 a7a49d459bf4862f64f7bc1a68beccf8881c2fa9f3e0569608e16ba6f85ebf7b matched. Log: /data/ycfeng/tmp/tvcache-cu118-resume-20260910.log.
- Result: Torch wheel VERIFIED; torchvision wheel finishing. H200 step_main 1-GPU predict-only returned 7 candidate nodes at 15:35 +08:00. Installation and GPU loader remain pending; real rollouts 0/4.

- Installation result: torchvision also VERIFIED, 6,070,123 bytes / SHA-256 19ca4ab5d6179bbe53cff79df1a855ee6533c2861ddc7389f68349d8b9f8302a. Local uv --no-deps --offline installation exited 0 and replaced exactly two packages: torch 2.0.1+cu118 and torchvision 0.15.2+cu118, Python 3.10.20.
- GPU revalidation: submitted tvcache-videollava-cu118-h200-20260910 on H200 step_main, 1 GPU / 8 CPU / 65536 MiB, specified image, 1800 s launcher / 1200 s probe. Scheduled gpu-h200-0819.lgcm.sh.istep.fun. Launcher session 42842; logs /data/ycfeng/tmp/tvcache-videollava-cu118-h200-20260910{,-launch}.log; output videollava_offline_cu118_h200_20260910.json. Loader result pending.

### 2026-09-10 cu118 runtime library discovery repair

- Observation: H200 cu118 probe exited 1 during bitsandbytes import: libcusparse.so.11 could not be found. CUDA_VERSION=118 and compute capability 9.0 were detected; the CUDA zeros check did not execute. The earlier commentary claiming CUDA compatibility passed was premature.
- Motivation: expose the existing CUDA libraries to bitsandbytes dynamic loading. Expectation: proceed beyond import and execute the actual CUDA and full-model checks.
- Method: located libcusparse.so.11 in the venv nvidia/cusparse/lib; added torch/lib, nvidia/cuda_runtime/lib, and nvidia/cusparse/lib to process LD_LIBRARY_PATH. Local ldd now resolves every required shared library. No new package installed.
- Result: submitted H200 step_main probe tvcache-videollava-cu118-h200-20260910-b; session 7457, same image/resources/deadlines. Actual GPU validation pending.

- Observed H200 b CUDA result: zeros sum=0.0, expected 0.0, torch=2.0.1+cu118. Import now succeeds and the production loader entered checkpoint shard loading (0/2 initially). Full loader remains pending.
- Service preparation modification: applied the verified library search paths only to the VQA process in run_real_video_rollouts.sh, preserving the separate VideoAgent environment. Added wall-clock start/finish fields to provider_cache_rollout.py to associate each rollout with sampled GPU memory. Motivation: carry the environment fix into the real service and make GPU records attributable. Result: bash syntax and Python AST pass; live service/rollout validation pending.

- Full offline loader PASS on H200: 382.0911647360772 s, allocated/peak 5,408,568,320 bytes, context 2048, tokenizer 32000, 4-bit true, both towers true, both processors checked. CUDA zeros 0.0. Artifact: videollava_offline_cu118_h200_20260910_b.json. The CUDA-build/library discovery repair is verified; real service/tool execution is next.

### 2026-09-10 Real services and rollout worker submitted

- Motivation: proceed from the completed offline-loader gate to the agreed real local tools and cache comparison.
- Expectation: services -> tool smoke -> no-cache x2 -> TVCache x2 -> numeric artifacts and teardown.
- Method: H200 step_main predict-only returned 10 candidates for 2 GPU / 16 CPU / 131072 MiB. Submitted tvcache-real-rollout-h200-20260910 with the specified image and run_real_video_rollouts.sh; scheduled gpu-h200-0494.lgcm.sh.istep.fun. Launcher deadline 14400 s; worker command 12600 s; session 23206. Logs /data/ycfeng/tmp/tvcache-real-rollout-h200-20260910/.
- Result: worker starting. Offline loader code/report/artifact committed as 6521d11. Real tool and rollout PASS remain pending.

- Real worker started with two NVIDIA H200 devices and STEPCODE_API_KEY=SET (value unlogged). TVCache is listening on 127.0.0.1:8001; VQA and sandbox initializing. GPU CSV records 143771 MiB total per device.
- Local startup fix: the real sandbox import warned that the default Ultralytics config directory was unwritable. Added YOLO_CONFIG_DIR=$LOG_DIR/ultralytics for subsequent launches to follow the tmp storage rule; the already-running process keeps its original environment. Live tool smoke remains pending.

- Pre-tool baseline: sandbox directory has 0 entries; shared EgoSchema preprocessing cache has 0 entries. The live smoke therefore starts from raw video without prepared preprocessing artifacts. Sandbox Captioning constructor completed in 60.449 s; remaining constructors and VQA tower initialization are active.

- Real service attempt a: VQA ready, sandbox listening 5000, TVCache /get returned 200, credential SET. The shell then exited 127 with `line 67: t: command not found`. Root cause: the agent edited earlier lines of the still-running shell script, shifting its read position. This is an execution error, not a service compatibility failure. All four owned service processes exited in the EXIT trap (143,143,143,0); zero tools/rollouts executed.
- Fix motivation: make the launched shell input stable. Method: allow explicit REPO_DIR and create a unique immutable execution snapshot at /data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-b.sh, loaded from the current syntax-passed source. Launch the snapshot with REPO_DIR set; keep it unchanged during execution. Subsequent launches include YOLO_CONFIG_DIR under task logs. Result: snapshot ready; attempt b pending.

- Attempt b service readiness passed and tool smoke is executing. Real /start HTTP 200 in 0.022912354208528996 s; load_video_into_sandbox HTTP 200 in 0.22444507014006376 s. Sandbox id tool-smoke-8b4d2222395541fd9fd3555fe640a5d0. LaViLa generated actual captions describing drawing/painting; complete preprocessing and subsequent tools are pending.

- Tool smoke PASS (7 HTTP 200 requests): start 0.0229123542 s; load 0.2244450701 s; preprocess 144.4232299067 s; caption 0.6344481488 s; localization 2.1142926929 s; real VQA 17.3319152980 s; stop 0.0512400423 s. VQA returned a painting description and answer; sandbox disappearance asserted. Video has 90 segments. Existing 300 s sandbox timeout exceeds measured preprocessing; no timeout change required. Artifact: tvcache-real-rollout-h200-20260910-b-tool-smoke.json. Four-rollout driver now starting.

- Tool smoke substep committed as 43d6661. Four-rollout run id provider-271169d4ba5f4a1b8988c5e0f79bafb7; first no-cache rollout is executing actual preprocessing. Worker clock explicitly reports +0000 (UTC), allowing GPU CSV timestamps to be joined with rollout Unix start/finish values.

### 2026-09-10 First real rollout failed at provider JSON boundary

- Observed: first no-cache rollout executed local preprocessing and query tools, then Response.model_validate_json rejected trailing DSML calls at line 16. Provider usage/full invalid response were not persisted by the original driver on failure. Real completed rollout records remain 0/4.
- Cleanup: failing rollout /stop HTTP 200; worker EXIT trap stopped VQA/sandbox/cache/monitor (143/143/143/0); launcher exited 1.
- Investigation: local loop requests JSON actions, then serializes them into native assistant.tool_calls plus role=tool history; ProviderChatClient requests json_object but leaves native tool selection unspecified. Testing whether explicit tool_choice=none preserves the JSON action contract while retaining local role=tool history.
- Method: added a direct provider_tool_history_probe.py replay using the fixed question and actual tool-smoke results, recording full request/response without credential headers. This is protocol replay, not a new real rollout. Original request probe session 53323.

- Protocol replay evidence: original request HTTP 200 / 2.7503469851 s reproduced JSON + DSML calls and failed schema parsing. Explicit tool_choice=none on the same tool history returned HTTP 200 / 1.8190864681 s and pure schema-valid JSON actions (prompt 2513, completion 231, total 2744 tokens). Original raw response: /data/ycfeng/tmp/tvcache-provider-history-original-20260910.json; corrected response: /data/ycfeng/tmp/tvcache-provider-history-none-20260910.json.
- Root-cause fix: ProviderChatClient now sets tool_choice=none because local code executes JSON actions; native tool-call history remains intact. Added a focused assertion and per-response recording in the rollout driver before schema validation. Expected: remove native output-format ambiguity and preserve complete failure evidence. Controller env lacked pytest; switched the test command to existing tvcache/client/.venv. An overly broad temporary-file search hit unrelated permissions and was stopped; it did not affect runtime state.

- Provider fix committed as 87eed3d after 8/8 focused checks passed. Restarted H200 attempt c, session 44222, same 2-GPU resources and deadlines. Snapshot /data/ycfeng/tmp/tvcache-real-rollout-h200-20260910-c.sh resumes directly at four-rollout execution after service readiness; the already-passed tool smoke is not repeated. Existing repository shell remains the complete end-to-end recipe.


### 2026-09-10 Actual failing-history diagnosis and protocol decision pending

- Attempt c: first no-cache rollout failed again with JSON followed by DSML. Full raw provider exchanges are saved in `tvcache-real-rollout-h200-20260910-c-rollouts/no-cache-0-provider.jsonl`. Three responses consumed 6786 prompt / 802 completion / 7588 total tokens before failure; no completed reward record exists. Five local tools executed before the malformed third response. Sandbox stop returned 200 and all four service processes exited; no GPU service is left running.
- Correction to prior conclusion: commit 87eed3d's tool_choice=none setting passed one protocol sample but did not solve the real failure. Its unit tests prove payload construction only. Treat the mixed-protocol issue as OPEN.
- Exact-history probes: valid JSON native arguments still produced DSML (HTTP 200, 2.591786147 s); thinking disabled still produced DSML (HTTP 200, 2.475934667 s, reasoning_tokens=0). Forced agent_response under thinking was rejected HTTP 400; disabling thinking made the request succeed but returned other tool names, so the forced-function contract failed.
- Candidate protocol A, JSON actions with textual result history: remove synthetic assistant.tool_calls and encode each observed tool output as an ordinary message. Three same-history requests passed full Response schema in 2.201208508, 2.470019207, 1.754977859 s. This changes the recorded role=tool wire-history design; local execution/cache/metrics can remain the same.
- Candidate protocol B, native tools: declare the six local functions plus submit_answer, provide JSON arguments, and request native calls. Actual response HTTP 200 in 2.097947476 s, finish_reason=tool_calls, three caption_retrieval calls with valid inputs objects, 2506/300/2806 tokens. Requires provider decoding, prompt and local history alignment; tools still execute locally. This is one successful protocol probe, not an end-to-end rollout pass.
- Recommendation for this bounded four-rollout acceptance: candidate A has the smallest implementation scope and removes the proven native-history trigger; three protocol probes passed. Candidate B preserves standard native tool-call wire semantics but changes more of the adapter and final-answer path.
- Approval boundary: both viable candidates revise design.md's JSON-actions + native-history decision. Production protocol changes are held for explicit agreement under the user's Approval Gate. The grill-me/grilling protocol is active. No candidate implementation or workaround has been applied.
- Remaining: approve protocol adjustment -> implement it and verify against recorded failing history -> same-question no-cache x2 -> TVCache x2 -> all numeric metrics / exact-hit validation -> teardown and final review/report/summary. Real completed rollout records remain 0/4.


### 2026-09-11 H800 Real Rollout Acceptance

- Motivation: H200 is disabled; continue the approved real inference-driven agent rollout on H800 `codesign` with the company StepCast vLLM image.
- Method: ran `/kubebrain/rlaunch --detach` with `--charged-group=codesign --private-machine=group --positive-tags=h800 --gpu=2 --cpu=16 --memory=131072 --enable-sshd=false --image=hub.stepfun-inc.com/stepcast/stepcast:vllm-openai-v0.19.0`, mounted `/data`, and used the pinned H800 Hugging Face cache. Provider credential was read in memory from the controlled StepCode config path and the worker logged only `STEPCODE_API_KEY=SET`.
- H800 asset gate: offline Video-LLaVA probe passed on NVIDIA H800 with Python 3.10.20, Torch 2.0.1+cu118, four-bit loader, tokenizer vocabulary 32,000, image/video towers loaded, and 3,525,137,920 allocated bytes. LanguageBind image/video local loaders also passed; pinned snapshots and refs are under `/data/ycfeng/tmp/tvcache-videollava-hf-cache-h800`.
- Tool gate: Captioning, viCLIP SegmentFeature, Tracking, sandbox `/start`, and `load_video_into_sandbox` all passed.
- Rollout result: four artifacts and `summary.json` were produced under `tvcache-real-rollout-h800-20260911-b-rollouts`. All four rewards are `1.0`, all final answers are index `1`, and `remaining_run_sandboxes=[]`.
- Metrics: no-cache-0 `235.0006 s`, 26 calls/executions, misses 26, tokens `31971/4419/36390`; no-cache-1 `168.4909 s`, 15/15, misses 15, tokens `14804/1990/16794`; tvcache-0 `195.1357 s`, 20 calls, 20 executions, prefix hits 19, misses 1, forks 2, puts 20, tokens `20331/2122/22453`; tvcache-1 `65.5046 s`, 18 calls, 13 executions, exact hits 5, prefix hits 13, misses 0, forks 1, puts 13, tokens `21577/2258/23835`.
- Teardown: worker reached `Succeeded`; rollouts log shows TVCache drain/stop operations and no residual run sandboxes. GPU memory CSV was retained at `/data/ycfeng/tmp/tvcache-real-rollout-h800-20260911-b/gpu-memory.csv`.
- Status: Phase 4 real rollout acceptance **completed** for the fixed one-video/four-rollout scope; RL optimizer update remains intentionally excluded.

### 2026-09-11 H800 Reproduction Documentation

- Motivation: make the successful H800 run repeatable after the worker is reclaimed and `/data/ycfeng/tmp` execution logs expire.
- Changes: added `h800_reproduction.md`, durable `tests/e2e/run_real_video_rollouts_h800.sh`, and parameterized `tests/performance/complete_hf_cache_h800.py`; documented pinned revisions, offline loader settings, H800 launch flags, secret-path handling, output inventory, acceptance assertions, and known runtime requirements.
- Verification: `bash -n tests/e2e/run_real_video_rollouts_h800.sh` and `python3 -m py_compile tests/performance/complete_hf_cache_h800.py` pass. The recipe points to the already accepted H800 artifacts and uses a fresh `JOB_ID` for each rerun.
