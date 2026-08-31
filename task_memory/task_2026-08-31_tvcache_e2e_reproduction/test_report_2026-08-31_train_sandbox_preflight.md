## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-08-31 | Record sandbox and training E2E preflight checks |
| 2026-08-31 | Add final train-import and server-lock gate evidence |

# Test Report: Sandbox and Training Preflight

## 1. Test Script Information

- Persistent task directory: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/task_memory/task_2026-08-31_tvcache_e2e_reproduction/`
- No new test script was required. Checks exercised the repository entrypoints and source contracts directly.
- Commands:

  ```bash
  python -m compileall -q train video-agent-tools/VideoAgent video-agent-tools/Video-LLaVA/videollava
  cd video-agent-tools/VideoAgent
  timeout 20s python sandbox_server.py
  cd train
  uv lock --check
  uv run --no-sync python --version
  uv run --no-sync python -c 'import importlib.util; ...'
  uv run --no-sync python -c 'import train_with_tvcache'
  ```

- Environment: system Python `3.12.3`; `uv 0.11.14`; `train/.venv` Python `3.12.3`; no usable `nvidia-smi` result in this shell. The sandbox startup command used the system interpreter because the required VideoAgent Conda environment is not installed.

## 2. Validation Criteria

- `compileall` must exit `0`; this detects syntax/import-bytecode errors that would prevent any entrypoint from loading.
- `sandbox_server.py` must remain alive beyond the timeout and bind its documented HTTP port `5000`; an early traceback is a failed backend prerequisite.
- `uv lock --check` must pass without rewriting lock files.
- The train interpreter must import `pydantic`, `chz`, `datasets`, `tinker`, `tinker_cookbook`, `httpx`, and `tvclient` before `train_with_tvcache.py` can reach its CLI/configuration path.
- Required runtime assets must exist: `video-agent-tools/VideoAgent/cache_dir/`, `tool_models/`, `egoschema_cache/`, and `train/EgoSchema/videos/`.

## 3. Test Results and Evidence

| Check | Result | Observed evidence |
| --- | --- | --- |
| Python bytecode compile | PASS | Exit `0`; two non-fatal `SyntaxWarning` messages in `LaViLa/lavila/utils/evaluation_ek100mir.py`. |
| Sandbox startup | FAIL | Exit `1` before Flask bind. Traceback ends with `RuntimeError: operator torchvision::nms does not exist` while importing `torchvision` from `captioning.py`. Full log: `/data/ycfeng/tmp/tvcache-sandbox-startup.log`. |
| Train lock integrity | PASS | `cd train && uv lock --check` printed `Resolved 39 packages in 1ms` and exited `0`. |
| Client lock integrity | PASS | `cd tvcache/client && uv lock --check` printed `Resolved 22 packages in 2ms` and exited `0`. |
| Train no-sync interpreter | PASS | `uv run --no-sync python --version` printed `Python 3.12.3`. |
| Train dependency import | FAIL | `uv run --no-sync` reported `pydantic=False`; direct import exited `1` with `ModuleNotFoundError: No module named 'pydantic'`. |
| Dataset download import | FAIL | `cd train/EgoSchema && ../.venv/bin/python download.py` exited `1` with `ModuleNotFoundError: No module named 'gdown'`; the train manifest does not declare this import. Log: `/data/ycfeng/tmp/tvcache-download-import.log`. |
| Dataset processing | FAIL | `cd train/EgoSchema && ../.venv/bin/python process_videos.py` read metadata, then exited `1` with `FileNotFoundError: [Errno 2] No such file or directory: 'videos'`. Log: `/data/ycfeng/tmp/tvcache-process-import.log`. |
| Required data/assets | FAIL | `cache_dir`, `tool_models`, `egoschema_cache`, `sample_videos`, and `train/EgoSchema/videos` are absent. Metadata files are present: `processed_videos.json` size `137543` bytes, `questions.json` size `4562127` bytes, `subset_answers.json` size `21500` bytes. |
| Server lock alignment | PASS | The initial `uv lock --check` exposed a missing declared `gunicorn` entry; after applying the generated `gunicorn==26.2.0` lock delta, `uv lock --check` and `uv sync --locked --dry-run` both exited `0` (`15` packages, `Would make no changes`). |

### Root-cause interpretation

1. The system interpreter has incompatible Torch/Torchvision binaries (`torchvision::nms` is not registered). The documented VideoAgent Conda environment and pinned dependencies are required before retrying startup.
2. The repository does not ship model weights or downloaded videos. Even after dependency setup, `SandboxManager.load_video_into_sandbox()` looks for the literal path `path/to/train/EgoSchema/videos/<video_name>` (`video-agent-tools/VideoAgent/sandbox_manager.py:96-109`), which is not present in this checkout.
3. `train/.venv` is a bare virtual environment. A full `cd train && uv sync --locked` is required, plus an installed editable client (`uv pip install -e ../tvcache/client`) and a valid `TINKER_API_KEY` before training can start.

### Current verdict

The complete video/Tinker E2E is **BLOCKED** by missing external runtime assets, incompatible system dependencies, and credentials. The TVCache server/client protocol smoke remains independently reproducible and is recorded in the companion server/client report.

## 4. Completion-gate train import rerun

- Command: `cd train && uv run --no-sync python -c 'import train_with_tvcache'`.
- Environment: train `.venv` Python `3.12.3`; `uv 0.11.14`.
- Result: exit `1`; traceback ends at `train/tool_schema.py:2` with `ModuleNotFoundError: No module named 'pydantic'`.
- Asset probe: `video-agent-tools/VideoAgent/cache_dir`, `tool_models`, `egoschema_cache`, and `train/EgoSchema/videos` all reported `MISSING`.
