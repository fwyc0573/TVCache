## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-10 | Marked pinned assets complete, recorded the cu118 runtime repair prerequisite, and prepared real service/tool execution. |
| 2026-09-11 | Switched the disabled H200 route to H800 `codesign` and completed the four-rollout acceptance. |
| 2026-09-09 | Resumed full local-tool assets after disk space was freed; use H200 step_main first, with authorized H800 codesign fallback. |
| 2026-09-08 | Injected `STEPCODE_API_KEY` from local StepCode config into an H200 worker and verified `/v1/models`, `json_object`, and standard `role=tool` protocol success; changed the adapter to local schema validation because upstream rejects `json_schema`. |
| 2026-09-08 | Ran the H200 `step_main` provider smoke through the specified StepCast image; platform startup passed, but the worker had no injected `STEPCODE_API_KEY`, so live provider execution is blocked. |
| 2026-08-17 | Reopened CPU TDD and implementation for the approved DeepSeek plus local-vision provider migration. |
| 2026-08-17 | Added official API-key acquisition and secure-injection research to the Phase 4 credential gate. |
| 2026-08-16 | Blocked Phase 4 before worker allocation because both required API-key environment variables are unset. |
| 2026-08-16 | Closed I-047 after v9 architecture CLEAR and code/spec/security APPROVE, and opened Phase 4 GPU preparation. |
| 2026-08-16 | Recompleted Phase 3 after production teardown convergence remediation and the fresh 175-test Python 3.12 gate. |
| 2026-08-16 | Completed the v8 production-entrypoint RED gate and moved transport-only teardown convergence into root-cause implementation. |
| 2026-08-16 | Reopened Phase 2 and held Phase 3 pending after the v8 architecture review found that the production entrypoint does not drive the retry-safe teardown state machine to convergence. |
| 2026-08-16 | Recompleted Phase 3 after I-047 retry-safe teardown remediation and the fresh 173-test Python 3.12 gate. |
| 2026-08-16 | Completed the I-047 response-loss RED gate and moved retry-safe teardown remediation into implementation. |
| 2026-08-16 | Reopened Phases 2 and 3 after the v7 architecture review found response-loss ownership gaps in destructive teardown RPCs. |
| 2026-08-16 | Recompleted Phase 3 after I-046 run-level teardown remediation and the fresh 160-test Python 3.12 gate. |
| 2026-08-16 | Completed the I-046 RED gate and moved task-level cache teardown remediation into implementation. |
| 2026-08-16 | Reopened Phases 2 and 3 after the v6 architecture review confirmed missing task-level ownership for successfully published cache environments. |
| 2026-08-16 | Recompleted Phases 2 and 3 after I-044/I-045 remediation and the fresh 149-test Python 3.12 gate. |
| 2026-08-16 | Reopened Phases 2 and 3 after the v5 architecture review found two reachable cleanup ownership blockers. |
| 2026-08-16 | Recompleted Phases 2 and 3 after I-042/I-043 remediation and the fresh 149-test Python 3.12 gate. |
| 2026-08-16 | Reopened Phases 2 and 3 after the v4 code/spec/security review found two fork-ownership cleanup blockers. |
| 2026-08-16 | Recompleted Phases 2 and 3 after I-035 through I-040 remediation and the fresh 145-test Python 3.12 gate. |
| 2026-08-16 | Reopened Phases 2 and 3 after both v3 pre-GPU reviews found lifecycle and startup blockers. |
| 2026-08-16 | Completed Phases 2 and 3 after the real Tinker preflight and fresh 128-test Python 3.12 gate. |
| 2026-08-16 | Recorded the real Tinker preflight RED caused by an incorrect chz help-exit expectation. |
| 2026-08-16 | Recorded successive verified Python 3.12 artifact completions and frozen sync interruptions. |
| 2026-08-16 | Reopened CPU TDD and implementation after the v2 architecture review returned BLOCK. |
| 2026-08-16 | Completed the reopened CPU phases after the fresh 89-test gate; independent review is next. |
| 2026-08-16 | Reopened CPU TDD and implementation after the independent architecture review returned BLOCK. |
| 2026-08-16 | Marked CPU TDD and root-cause implementation complete after a fresh 37-test gate. |
| 2026-08-16 | Recorded the resumed source-map lookup error and retained the remaining CPU TDD gates. |
| 2026-08-16 | Marked setup complete and resumed the interrupted TDD audit. |
| 2026-08-14 | Created the implementation and validation plan. |

# Implementation Plan

## Goal

Measure TVCache in a real inference-driven agent rollout using StepCode Codex's `deepseek-v4-flash` provider through the specified StepCast vLLM OpenAI-compatible layer on the available H800 `codesign` worker (H200 is disabled). The local agent loop owns action parsing, tool execution, VideoAgent sandbox lifecycle, and TVCache/no-cache comparison; online RL optimizer updates are outside this round.

## Phases

| Phase | Status | Exit Criteria |
|-------|--------|---------------|
| 1. Task setup and baseline audit | Complete | Isolated worktree and task records exist; baseline behavior and failures are recorded. |
| 2. TDD regression coverage | Complete | Provider, lifecycle, and runtime regression tests pass. |
| 3. Root-cause implementation | Complete | DeepSeek text protocol and local VideoAgent paths pass focused and full CPU verification. |
| 4. H800 environment and provider preparation | Complete | Pinned assets, provider protocol, and H800 Video-LLaVA offline loader are verified. |
| 5. Real tool-chain validation | Complete | H200 services and all seven real smoke HTTP calls pass, including VQA and sandbox removal. Preprocessing 144.42 s; VQA 17.33 s. |
| 6. Rollout baseline and TVCache smoke | Complete | Two no-cache and two TVCache rollouts finished with complete numeric evidence; RL optimizer updates are excluded. |
| 7. Review and completion | Complete | Final report, task-memory archive, verification, and committed source/test changes are complete. |

## Ordered Work

1. Record the current commit, environment, known documentation gaps, and baseline failures.
2. Add failing tests for URL propagation, fail-fast HTTP behavior, fork-bank reuse, cache statistics, current server schema, and empty-advantage batches.
3. Implement only the behavior needed to make those tests pass.
4. Pin the training environment to Tinker `0.24.1`, the replacement model, and the non-thinking renderer.
5. Run CPU unit and integration gates before allocating GPUs.
6. Verify official acquisition paths for both required API keys and document a non-logging injection procedure.
7. Add RED tests requiring `DEEPSEEK_API_KEY`, exact `deepseek-v4-flash`/base-URL/non-thinking configuration, and zero OpenAI state in the active sandbox/toolkit path.
8. Add RED tests requiring local LaViLa on-demand captions with API token counts `0/0` and Video-LLaVA-only VQA.
9. Implement the minimal provider migration in `runtime_config.py`, `sandbox_manager.py`, `captioning.py`, and `tools.py`.
10. Run focused provider tests, affected VideoAgent tests, the complete Python 3.12 CPU gate, and source/credential hygiene checks.
11. Launch an H200 `step_main` worker using its authoritative `rlaunch` recipe after provider endpoint, value-free credential presence, and external assets are ready.
12. Prepare the smallest authorized VideoAgent local-weight bundle, Video-LLaVA, TVCache server, and training environments without storing secrets.
13. Add and validate an inference adapter that requests provider-supported `json_object` output, validates the repository `Response` schema locally, and leaves tool execution and sandbox lifecycle local.
14. Run a deterministic provider/tool-chain test, then no-cache rollout, then TVCache rollout.
14. Record numeric metrics, inspect cleanup state, run code review, and archive the final evidence.

## Acceptance Criteria

- Infrastructure errors raise immediately instead of becoming cache misses or tool-result strings.
- A controlled repeated tool sequence returns the same value and performs zero backend tool executions on the second exact hit.
- A partial prefix reuses the cached environment and executes only the suffix.
- The server integration test fails on HTTP 500 and uses the current `values`/`tool_exec_times` schema.
- The no-cache and TVCache runs each complete two rollouts on the same fixed question.
- Rewards, token counts, tool counts, hit/miss counts, fork counts, latency, and GPU memory are recorded numerically.
- Zero-variance rewards produce an explicit optimizer-skip metric instead of an empty Tinker update.
- Lost responses after committed drain or sandbox-stop operations preserve ownership, and retrying the same operation converges without duplicate destructive work.
- No unexpected sandbox directories or worker processes remain after teardown.
- The active sandbox requires `DEEPSEEK_API_KEY`, constructs `deepseek-v4-flash` against `https://api.deepseek.com`, and disables thinking explicitly.
- Active caption and VQA calls use LaViLa and Video-LLaVA only; OpenAI keys, endpoints, GPT models, and fallback branches are absent from the active path.
- On-demand local caption calls return `(captions, 0, 0)` and fail fast on invalid video/range/frame state.

## Verification Strategy

- `pytest` for unit and CPU integration tests.
- HTTP health and schema checks for TVCache and sandbox services.
- Direct tool-chain calls for load, preprocess, query, fork, and cleanup.
- Reproducible Tinker smoke commands for baseline and TVCache variants.
- Fresh full verification before any completion claim.

## Current Execution Status (2026-09-08)

- Completed: fixed EgoSchema sample download, `ffprobe`/SHA-256 verification, persistent asset placement, sample manifest, StepCode provider protocol gate, controlled H200 credential injection, and H200 worker reachability.
- In progress (2026-09-09): the user authorized the smallest compatible local weights and freed disk space. CLIP is verified; DINOv2-S and RT-DETR files are available; ViCLIP and Video-LLaVA downloads are running; LaViLa remains pending. Separate legacy tool runtime environments are being installed. Full VQA remains in scope.
- Pending after the blocker is resolved: sandbox service smoke, TVCache service smoke, deterministic local tool-chain, two no-cache rollouts, two TVCache rollouts, numeric metrics, teardown verification, and final review.
- Dependency chain: `video/runtime assets -> sandbox service -> TVCache service -> deterministic tool-chain -> {no-cache rollouts, TVCache rollouts} -> metrics/review`; the two rollout variants run in parallel after the deterministic tool-chain passes.
- Current continuation chain (2026-09-09): `{clean model downloads, runtime preparation} -> model constructors -> sandbox/Video-LLaVA/TVCache services -> deterministic tool-chain -> no-cache rollouts -> TVCache rollouts -> metrics/review`. Downloads and runtime preparation may proceed in parallel. H200 step_main is preferred; H800 codesign is authorized if H200 has no resources. Keep VQA enabled.

## Errors Encountered

| Date | Error | Attempt | Resolution |
|------|-------|---------|------------|
| 2026-08-17 | Official OpenAI developer/help pages returned HTTP 403, and the current process could not discover the newly configured `openaiDeveloperDocs` MCP server. | 1 | The official MCP configuration is installed successfully, but live server discovery requires a fresh process; query it through a fresh MCP-aware process rather than repeating blocked curl requests. |
| 2026-08-17 | Direct Python retrieval of the public Tinker documentation root returned HTTP 403 although the preceding curl HEAD probe returned HTTP 200. | 1 | Do not repeat the same urllib request; retrieve the official page with curl and a browser user-agent, then parse only its published content. |
| 2026-08-16 | The first v3 RED batch used system Python, so 4 async cases failed on the missing `pytest-asyncio` plugin instead of exercising production behavior. | 2 | Consulted `task_memory/env_handbook.md` and reran the 4 async nodes with the declared locked client dev environment; all 4 then failed for the intended ownership/reference assertions. |
| 2026-08-16 | The v3 root-cause inspection repeated the stale `tvcache/server/immutable_env_prefix_tree.py` path and one bounded read exited nonzero. | 2 | Located the implementation at `tvcache/server/tvcache/immutable_env_prefix_tree.py` before reading it; all further server inspection uses the verified path. |
| 2026-08-16 | All 5 targeted async tests failed before execution because `/usr/bin/python3` lacks `pytest-asyncio`; 5 unknown-mark warnings were emitted. | 1 | Investigating declared dependencies and available environments; no workaround applied. |
| 2026-08-16 | The isolated client `uv` environment collected 0 tests because 4 modules could not import directly used `httpx`. | 2 | Added the missing runtime dependency, regenerated the lock, and verified 5/5 tests pass in 0.25 s. |
| 2026-08-16 | A symbol overview used the recorded basename `tvcache/server/immutable_env_prefix_tree.py`, which is not the actual repository path. | 1 | Treating the path as an unverified finding; locate the file before the next source read rather than repeating the failed lookup. |
| 2026-08-16 | `uv lock --project train` produced no resolver output for over five minutes after selecting Python 3.12.3. | 1 | Interrupted the stalled process; diagnose package-index connectivity before retrying with a changed environment. |
| 2026-08-16 | A 60-second verbose resolver diagnostic timed out after evaluating the cookbook’s large cross-platform dependency graph. | 2 | PyPI connectivity and Tinker `0.24.1` availability are healthy; constrain resolution to the required Linux x86_64 deployment target before the next full attempt. |
| 2026-08-16 | The first platform-marker test string used invalid Python escaping and failed collection. | 1 | Corrected the test string syntax before evaluating the intended RED behavior. |
| 2026-08-16 | A read-only VideoAgent dependency inspection command exited 1 after successfully printing earlier files. | 1 | The final unmatched optional-file probe became the shell loop's exit status; inspect the committed `environment.yaml` directly and do not treat the absent top-level requirements file as a runtime failure. |
| 2026-08-16 | The first structured-cleanup GREEN attempt stopped only the last loop. | 1 | Source inspection showed `started_loops.append` was accidentally outside the start loop; corrected its indentation and reran the focused test successfully. |
| 2026-08-16 | The first warmup-cancellation GREEN assertion did not observe the bank coroutine's cancellation handler. | 1 | The fake sampler returned without yielding, so the newly created task had never entered its coroutine; added one event-loop yield to test the real started-task path, then verified cancellation. |
| 2026-08-16 | The first renderer-test lookup used the guide's stale `tinker_cookbook/tests/test_renderers.py` path and made the combined read-only command exit 2. | 1 | The RL source evidence printed successfully; locate the actual renderer tests with `find` before any further lookup instead of repeating the missing path. |
| 2026-08-16 | The first combined RED-test patch did not apply because its baseline-test tail context was stale. | 1 | No file changed; split the patch by target file and inspect the exact tail before adding the non-append test. |
| 2026-08-16 | The first three-driver trajectory wiring patch used an inexact manual-Datum block and did not apply. | 1 | No driver changed; inspect one exact block, patch it narrowly, then apply the verified shape to the other two files. |
| 2026-08-16 | The first loaded-only fork RED used `list.append` as a test double, which rejected the production keyword argument before the intended assertion. | 1 | Replaced it with a signature-compatible recorder; the corrected test fails because toolkit creation is actually called once. |
| 2026-08-16 | The first run-ID GREEN assertion counted the later metrics lookup assignment as a second sandbox-ID constructor. | 1 | Restricted the AST gate to assignments whose value contains `run_id`; production code was already correct. |
| 2026-08-16 | The first executor lifecycle patch used `elif` after an `except` clause, so the new reference RED test stopped at import-time `SyntaxError`. | 1 | Changed the clause to `else` with an inner identity check, then reran the same node and observed the intended missing-`unref` assertion failure. |
| 2026-08-16 | The first whole-method executor patch did not apply because its copied context contained a mismatched commented line. | 1 | No file changed; reread the exact numbered method body and applied the same bounded replacement against verified context. |
| 2026-08-16 | A broad read-only symbol search expanded into system site-packages and produced no useful output within 10 seconds. | 1 | Interrupted it; the required converter source was already available in the vendored cookbook, so future lookups stay restricted to `train/tinker-cookbook` or the locked train environment. |
| 2026-08-16 | The first resource-scoped `uv sync --project train --frozen` reached its 600-second timeout while downloading the 139-package environment. | 1 | The process exited 124 with no child left; uv's transactional environment contains 0 installed packages, while 850 MiB is safely cached under `/data/ycfeng/tmp`. Diagnose cache completeness offline rather than repeat the network sync unchanged. |
| 2026-08-16 | The offline frozen sync exited 1 because the locked SciPy 1.18.0 CPython 3.12 wheel was not cached. | 1 | This was the intended cache-completeness diagnostic; target the exact canonical artifact rather than rerun the full online resolver. |
| 2026-08-16 | Targeted SciPy installation through the prescribed network proxy exhausted three 46.2-second connection attempts to `https://pypi.org/simple/scipy/`. | 1 | No package changed; compare bounded connectivity to the exact lockfile wheel host before choosing the next download command. |
| 2026-08-16 | Direct `uv pip install --no-deps` of the canonical 33.7 MiB SciPy wheel also reached the 600-second timeout before completing. | 2 | The direct route passes HEAD in 0.63 s but bulk transfer is too slow for uv's non-resumable scoped attempt; inspect partial cache state and use a resumable canonical download rather than repeat uv unchanged. |
| 2026-08-16 | After verified local SciPy installation, the next offline frozen sync exited 1 because the locked PyYAML 6.0.3 CPython 3.12 wheel was not cached. | 1 | Preserve the successful SciPy installation and fetch only the exact PyYAML wheel named by uv before the next offline sync. |
| 2026-08-16 | After verified local PyYAML installation, the next offline frozen sync exited 1 because the locked charset-normalizer 3.5.1 CPython 3.12 wheel was not cached. | 1 | Preserve both installed artifacts and fetch only the exact charset-normalizer wheel named by uv before repeating the offline diagnostic. |
| 2026-08-16 | After verified local charset-normalizer installation, the next offline frozen sync exited 1 because the locked PyArrow 25.0.1 CPython 3.12 wheel was not cached. | 1 | Preserve the three installed artifacts and resumably fetch only the exact 50,102,437-byte PyArrow wheel named by uv. |
| 2026-08-16 | After verified local PyArrow installation, the next offline frozen sync exited 1 because the locked TextArena 0.7.4 wheel was not cached. | 1 | Preserve the four installed artifacts and fetch only the exact 1,073,570-byte universal wheel named by uv. |
| 2026-08-16 | After all five missing wheels were installed from local files, offline sync requested PyArrow again. | 1 | Root cause: local installs carry `file://` provenance while the frozen lock requires registry provenance. A frozen offline `--find-links /data/ycfeng/tmp --dry-run` found all 138 packages with zero missing-artifact errors; use that verified source-reconciliation command for the real sync. |
| 2026-08-16 | The real frozen offline `--find-links` sync exited 1 on missing tokenizers 0.22.2 although its dry run had exited 0. | 1 | `uv sync --dry-run` plans package actions but does not prove every planned artifact is readable. Keep `--find-links`, stop preinstalling file-provenance packages, and add only the exact tokenizers wheel before the next real sync. |
| 2026-08-16 | After adding verified tokenizers to `--find-links`, the next real frozen offline sync exited 1 on missing Textual 8.2.8. | 1 | The environment was not modified; add only the exact 731,418-byte Textual wheel and repeat the same real sync. |
| 2026-08-16 | After adding verified Textual, frozen offline sync requested PyArrow again despite its wheel being present under `--find-links`. | 2 | Frozen sync still resolves the lock's registry URL and does not use the flat wheel as that URL's cache entry. Validate the root-cause fix by installing an exact package *by name* from the offline flat index, which should avoid direct-requirement `file://` provenance and let the installed version satisfy the registry lock. |
| 2026-08-16 | After converting all seven local wheels to ordinary name-based installs, plain frozen offline sync exited 1 on missing Inspect AI 0.3.258. | 1 | The provenance correction worked because none of the seven prior artifacts repeated. Fetch, verify, and install the exact 34,829,837-byte Inspect AI wheel by package name before the next offline sync. |
| 2026-08-16 | After verified name-based Inspect AI installation, plain frozen offline sync exited 1 on missing Transformers 5.4.0. | 1 | Preserve the eight valid installed packages; byte-range download, verify, and name-install only the exact 10,105,556-byte Transformers wheel. |
| 2026-08-16 | After verified name-based Transformers installation, plain frozen offline sync exited 1 on missing NumPy 2.4.3. | 1 | Preserve the nine valid installed packages; byte-range download, verify, and name-install only the exact 16,621,358-byte NumPy wheel. |
| 2026-08-16 | After verified name-based NumPy installation, plain frozen offline sync exited 1 on missing botocore 1.40.61. | 1 | Preserve the ten valid installed packages; byte-range download, verify, and name-install only the exact 14,055,973-byte botocore wheel. |
| 2026-08-16 | After verified name-based botocore installation, plain frozen offline sync exited 1 on missing pandas 3.0.5. | 1 | Preserve the eleven valid installed packages; byte-range download, verify, and name-install only the exact 10,998,091-byte pandas wheel. |
| 2026-08-16 | After verified name-based pandas installation, plain frozen offline sync exited 1 on missing SymPy 1.14.0. | 1 | Preserve the twelve valid installed packages; byte-range download, verify, and name-install only the exact 6,299,353-byte SymPy wheel. |
| 2026-08-16 | After verified name-based SymPy installation, plain frozen offline sync exited 1 on missing pyqwest 0.9.0. | 1 | Preserve the thirteen valid installed packages; byte-range download, verify, and name-install only the exact 5,572,909-byte pyqwest wheel. |
| 2026-08-16 | After verified name-based pyqwest installation, plain frozen offline sync exited 1 on missing zstandard 0.25.0. | 1 | Preserve the fourteen valid installed packages; byte-range download, verify, and name-install only the exact 5,546,993-byte zstandard wheel. |
| 2026-08-16 | After verified name-based zstandard installation, plain frozen offline sync exited 1 on missing joblib 1.5.3. | 1 | Preserve the fifteen valid installed packages; download, verify, and name-install only the exact 309,071-byte joblib wheel. |
| 2026-08-16 | After verified name-based joblib installation, plain frozen offline sync exited 1 on missing safetensors 0.7.0. | 1 | Preserve the sixteen valid installed packages; download, verify, and name-install only the exact 507,152-byte safetensors wheel. |
| 2026-08-16 | After verified name-based safetensors installation, plain frozen offline sync exited 1 on missing lxml 6.1.1. | 1 | Preserve the seventeen valid installed packages; byte-range download, verify, and name-install only the exact 5,240,367-byte lxml wheel. |
| 2026-08-16 | After verified name-based lxml installation, plain frozen offline sync exited 1 on missing hf-xet 1.4.2. | 1 | Preserve the eighteen valid installed packages; byte-range download, verify, and name-install only the exact 4,217,422-byte hf-xet wheel. |
| 2026-08-16 | After verified name-based hf-xet installation, plain frozen offline sync exited 1 on missing debugpy 1.8.21. | 1 | Preserve the nineteen valid installed packages; byte-range download, verify, and name-install only the exact 3,968,900-byte debugpy wheel. |
| 2026-08-16 | After verified name-based debugpy installation, plain frozen offline sync exited 1 on missing pycryptodomex 3.23.0. | 1 | Preserve the twenty valid installed packages; byte-range download, verify, and name-install only the exact 2,272,578-byte pycryptodomex wheel. |
| 2026-08-16 | After verified name-based pycryptodomex installation, plain frozen offline sync exited 1 on missing pydantic-core 2.46.4. | 1 | Preserve the twenty-one valid installed packages; byte-range download, verify, and name-install only the exact 2,094,516-byte pydantic-core wheel. |
| 2026-08-16 | After verified name-based pydantic-core installation, plain frozen offline sync exited 1 on missing NetworkX 3.6.1. | 1 | Preserve the twenty-two valid installed packages; byte-range download, verify, and name-install only the exact 2,068,504-byte NetworkX wheel. |
| 2026-08-16 | After verified name-based NetworkX installation, plain frozen offline sync exited 1 on missing Rich 14.3.3. | 1 | Preserve the twenty-three valid installed packages; download, verify, and name-install only the exact 310,458-byte Rich wheel. |
| 2026-08-16 | After verified name-based Rich installation, plain frozen offline sync exited 1 on missing NLTK 3.10.3. | 1 | Preserve the twenty-four valid installed packages; download, verify, and name-install only the exact 1,798,643-byte NLTK wheel. |
| 2026-08-16 | After verified name-based NLTK installation, plain frozen offline sync exited 1 on missing aiohttp 3.14.3. | 1 | Preserve the twenty-five valid installed packages; download, verify, and name-install only the exact 1,792,122-byte CPython 3.12 aiohttp wheel. |
| 2026-08-16 | After verified name-based aiohttp installation, plain frozen offline sync exited 1 on missing OpenAI 2.54.0. | 1 | Preserve the twenty-six valid installed packages; download, verify, and name-install only the exact 1,660,351-byte OpenAI wheel. |
| 2026-08-16 | After verified name-based OpenAI installation, plain frozen offline sync exited 1 on missing Pygments 2.19.2. | 1 | Preserve the twenty-seven valid installed packages; download, verify, and name-install only the exact 1,225,217-byte Pygments wheel. |
| 2026-08-16 | After verified name-based Pygments installation, plain frozen offline sync exited 1 on missing tiktoken 0.13.0. | 1 | Preserve the twenty-eight valid installed packages; download, verify, and name-install only the exact 1,136,523-byte CPython 3.12 tiktoken wheel. |
| 2026-08-16 | After verified name-based tiktoken installation, plain frozen offline sync exited 1 on missing setuptools 84.0.0. | 1 | Preserve the twenty-nine valid installed packages; download, verify, and name-install only the exact 818,216-byte setuptools wheel. |
| 2026-08-16 | After verified name-based setuptools installation, plain frozen offline sync exited 1 on missing regex 2026.2.28. | 1 | Preserve the thirty valid installed packages; download, verify, and name-install only the exact 802,037-byte CPython 3.12 regex wheel. |
| 2026-08-16 | After verified name-based regex installation, plain frozen offline sync exited 1 on missing huggingface-hub 1.8.0. | 1 | Preserve the thirty-one valid installed packages; download, verify, and name-install only the exact 625,208-byte huggingface-hub wheel. |
| 2026-08-16 | After verified name-based huggingface-hub installation, plain frozen offline sync exited 1 on missing Datasets 5.0.1. | 1 | Preserve the thirty-two valid installed packages; download, verify, and name-install only the exact 559,079-byte Datasets wheel. |
| 2026-08-16 | After verified name-based Datasets installation, plain frozen offline sync exited 1 on missing mpmath 1.3.0. | 1 | Preserve the thirty-three valid installed packages; download, verify, and name-install only the exact 536,198-byte mpmath wheel. |
| 2026-08-16 | After verified name-based mpmath installation, plain frozen offline sync exited 1 on missing Pydantic 2.13.4. | 1 | Preserve the thirty-four valid installed packages; download, verify, and name-install only the exact 472,262-byte Pydantic wheel. |
| 2026-08-16 | After verified name-based Pydantic installation, plain frozen offline sync exited 1 on missing rpds-py 2026.6.3. | 1 | Preserve the thirty-five valid installed packages; download, verify, and name-install only the exact 366,189-byte CPython 3.12 rpds-py wheel. |
| 2026-08-16 | After verified name-based rpds-py installation, plain frozen offline sync exited 1 on missing jiter 0.16.0. | 1 | Preserve the thirty-six valid installed packages; download, verify, and name-install only the exact 343,805-byte CPython 3.12 jiter wheel. |
| 2026-08-16 | After verified name-based jiter installation, plain frozen offline sync exited 1 on missing protobuf 7.35.1. | 1 | Preserve the thirty-seven valid installed packages; download, verify, and name-install only the exact 327,130-byte ABI3 protobuf wheel. |
| 2026-08-16 | After verified name-based protobuf installation, plain frozen offline sync exited 1 on missing multidict 6.7.1. | 1 | Preserve the thirty-eight valid installed packages; download, verify, and name-install only the exact 256,322-byte CPython 3.12 multidict wheel. |
| 2026-08-16 | After verified name-based multidict installation, plain frozen offline sync exited 1 on missing frozenlist 1.8.0. | 1 | Preserve the thirty-nine valid installed packages; download, verify, and name-install only the exact 242,411-byte CPython 3.12 frozenlist wheel. |
| 2026-08-16 | After verified frozenlist installation, plain frozen offline sync reached the cached Chess 1.11.2 source but its isolated build environment could not download setuptools 84.0.0 offline. | 1 | Resolved by installing Chess by exact name with `--offline --find-links /data/ycfeng/tmp --no-deps`; cached registry metadata selected Chess and the flat index supplied locked setuptools to build isolation. |
| 2026-08-16 | Exact-name offline Chess installation with `--no-index --find-links` could not resolve Chess because the flat directory has no Chess source archive. | 1 | Removed only `--no-index` while keeping network disabled; Chess built in 1.14 s, then plain frozen offline sync installed all remaining 97 packages. |
| 2026-08-16 | Real Tinker preflight expected driver `--help` exit 0, but the native driver printed valid help and exited 1. | 1 | chz 0.4.0 deliberately exits 1 for `EntrypointHelpException`, and the official cookbook does the same; correct the preflight to validate code 1, empty stderr, and required help fields without changing production entrypoints. |
| 2026-08-16 | The separate Python 3.12 client-dev frozen sync could not read Pygments 2.19.2 from its canonical offline cache entry. | 1 | Reuse the already lock-verified flat wheel through an exact-name offline installation, verify ordinary provenance, then rerun the plain frozen client sync. |
| 2026-08-16 | The second client-dev sync omitted `--python /usr/bin/python3`, so uv selected Python 3.10.20, automatically replaced the temporary target environment, and repeated the Pygments cache failure. | 2 | Do not reuse or replace that path; create a new target with the interpreter explicitly pinned and `--find-links /data/ycfeng/tmp` present in the one frozen offline sync. |
| 2026-08-16 | A fresh correctly pinned client-dev frozen sync still ignored the flat Pygments wheel and required its absent canonical cache entry. | 3 | Stop frozen client-sync attempts. Temporarily install the client lock's exact pytest packages into the complete Python 3.12 training environment, run the CPU suite, then restore that environment with plain frozen offline sync. |
| 2026-08-16 | Exact pytest installation into the training environment could not resolve pytest 8.4.2 from the selected offline cache. | 1 | Download and lock-verify the four small client-dev wheels (pytest, pytest-asyncio, pluggy, iniconfig), then install exact package names from the offline flat index. |
| 2026-08-16 | The resumed environment probe assumed a nonexistent worktree-local `train/.venv` and exited 127 before later checks. | 1 | Re-read the existing test report and `task_memory/env_handbook.md`; the authoritative frozen environment is `/data/ycfeng/tmp/tvcache-train-py312`, which then passed the complete 173-test gate and restoration checks. |
