## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Initialize issue and blocker log |
| 2026-08-31 | Add sandbox/train runtime blockers and correct inventory |
| 2026-08-31 | Add client port, rerun counter, and GPU assignment findings |
| 2026-08-31 | Resolve documentation consistency items after explicit authorization |
| 2026-08-31 | Resolve server lock drift against declared dependency |

# Issues

## Open Issues

- The process currently listening on TCP port 8000 is not yet identified; smoke tests will use an isolated port until its ownership is known.
- `httpx` is imported by the async client but is absent from `tvcache/client/pyproject.toml` and the synced environment.
- The checked-in server smoke script can report `Passed: 1/1` while its enabled `test_multiple_updates` sends incompatible payloads and receives 500 responses; its assertions do not fail on those intermediate responses.
- The manual smoke server uses port `18001`, but `AsyncSemanticStatefulExecutor` constructs `AsyncTVCacheClient()` with its hard-coded default `http://localhost:8001`; `train_with_tvcache.py` has no TVCache URL config field. A training run launched against only `18001` therefore receives swallowed connection errors and behaves as cache-miss-only. The guide must either run the training server on `8001` or document and verify a reviewed URL-injection code change.

## Newly Confirmed Blockers

- `video-agent-tools/VideoAgent` is present; the earlier “directory absent” note was an inventory error and is superseded.
- The VideoAgent runtime assets (`cache_dir/`, `tool_models/`, and `train/EgoSchema/videos/`) are absent. A sandbox startup attempt fails before Flask with `RuntimeError: operator torchvision::nms does not exist` under the system Python stack.
- `SandboxManager.load_video_into_sandbox()` resolves videos from the literal `path/to/train/EgoSchema/videos`, which is not a path in this checkout. Full sandbox E2E needs either the expected external path or a reviewed source-path correction.
- `train/.venv` contains no project dependencies; importing `train_with_tvcache` fails on missing `pydantic`. Full training also requires a Tinker API key and a live Tinker service.
- `train/tvc_agent_loop.py` passes `sandbox_base_url` into `VideoAgentLoop` but constructs `VideoSandboxEnv` with a hardcoded `http://localhost:5000`; a non-default sandbox URL cannot be selected solely through the documented config flag.
- `train/pyproject.toml` declares only `tinker`, while `train/train_with_tvcache.py` imports `chz`, `datasets`, and the sibling `tinker_cookbook` package. A normal `uv sync --locked` installs the Tinker transitive packages but cannot make those undeclared cookbook imports available; the guide must include an explicit cookbook installation step or document the resulting import failure.
- TVCache server auto-save paths diverge: the periodic worker writes under `~/susRL/tv-cache/data/runs/auto-saved`, while the shutdown handler writes under `~/tv-cache/data/runs/auto-saved`. The guide must use the absolute path printed by the server and account for both code paths.

## Resolved in This Session

- **Manual duplication:** The second copy of sections 8-14 was removed exactly from lines 732-1052 after explicit user authorization. The current manual has one continuous section sequence.
- **Smoke rerun isolation:** The HTTP example derives `TVCACHE_TASK` and `TVCACHE_ENV` from a timestamp, so repeated runs do not reuse the prior tree path.
- **Terminal-local training URL:** The training block exports `TVCACHE_BASE=http://127.0.0.1:8001` in T4 and performs a health request against that endpoint.
- **GPU documentation:** The manual assigns Video-LLaVA to GPU 0 and the sandbox to GPU 1, and labels one-GPU reuse as constrained smoke.
- **Server lock drift:** `tvcache/server/uv.lock` now contains the declared `gunicorn 26.2.0` entry; `uv lock --check` and locked sync dry-run both pass.
