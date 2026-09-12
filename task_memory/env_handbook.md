## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-10 | Documented the verified bitsandbytes SciPy dependency and loader import repair. |
| 2026-08-16 | Added the verified Python 3.12 CPU test-runner and frozen-restoration recipe. |
| 2026-08-16 | Added the verified frozen-offline PEP 517 source-build recipe. |
| 2026-08-16 | Added verified resource-scoped training-lock and CPU-only Torch recipes. |
| 2026-08-16 | Recorded the verified TVCache client unit-test environment recipe. |

# Environment Handbook

## TVCache Client Unit Tests

- Root cause addressed: `tvcache/client/pyproject.toml` must declare `httpx` at runtime and `pytest-asyncio` in its `dev` dependency group.
- Recreate and run the locked environment from the repository root:

  ```bash
  mkdir -p /data/ycfeng/tmp
  TMPDIR=/data/ycfeng/tmp uv lock --project tvcache/client
  TMPDIR=/data/ycfeng/tmp uv run --project tvcache/client --group dev python -m pytest -q tests/unit
  ```

- Verified environment on 2026-08-16: CPython 3.10.20, `httpx==0.28.1`, `pytest-asyncio==1.4.0`.

## Resource-Scoped Heavy Commands

- On this CPU master, system scopes require interactive authentication and `--wait` cannot be combined with `--scope`.
- The verified non-interactive form is a user scope:

  ```bash
  timeout 600s systemd-run --user --scope -p MemoryMax=2G <command>
  ```

## Training Lock

- The active Tinker rollout driver performs only CPU tensor construction; GPU-backed video tools run in separate environments.
- Pin Torch to the official CPU index so the training lock does not install a CUDA runtime newer than the H800 platform contract.
- Reproduce the lock:

  ```bash
  TMPDIR=/data/ycfeng/tmp \
  UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
  UV_HTTP_TIMEOUT=30 \
  timeout 600s systemd-run --user --scope -p MemoryMax=2G \
    uv lock --project train
  ```

- Verified result on 2026-08-16: 139 packages; `torch==2.13.0+cpu`; zero `cuda-*`, `nvidia-*`, or `triton` runtime packages.

## Frozen-Offline PEP 517 Source Builds

- Root cause addressed: an installed build requirement is not visible inside an isolated PEP 517 build environment, and `--no-index` also hides cached registry metadata for the source package.
- Keep the source package in uv's registry cache, place the exact lock-verified build-requirement wheel in `/data/ycfeng/tmp`, and install by package name:

  ```bash
  TMPDIR=/data/ycfeng/tmp \
  UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
  timeout 600s systemd-run --user --scope -p MemoryMax=2G \
    uv pip install \
      --offline \
      --find-links /data/ycfeng/tmp \
      --no-deps \
      --python /data/ycfeng/tmp/tvcache-train-py312/bin/python \
      'chess==1.11.2'
  ```

- Do not add `--no-index` unless the source archive itself is also in the flat directory.
- Verified result on 2026-08-16: Chess built in 1.14 s with locked `setuptools==84.0.0`; the following plain frozen offline sync installed 97 remaining packages, and `uv pip check` reported all 138 installed packages compatible.

## Python 3.12 CPU Test Runner

- Root cause addressed: `train/uv.lock` intentionally excludes pytest, while a separate frozen client environment may require a canonical wheel cache entry even when the same verified wheel exists in a flat directory.
- Download and verify the exact pytest, pytest-asyncio, pluggy, and iniconfig wheels recorded by `tvcache/client/uv.lock`. Install them temporarily by package name into the complete training environment:

  ```bash
  TMPDIR=/data/ycfeng/tmp \
  UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
  uv pip install \
    --offline \
    --no-index \
    --find-links /data/ycfeng/tmp \
    --no-deps \
    --python /data/ycfeng/tmp/tvcache-train-py312/bin/python \
    'pytest==8.4.2' \
    'pytest-asyncio==1.4.0' \
    'pluggy==1.6.0' \
    'iniconfig==2.3.0'
  ```

- Run the CPU suite, then restore the exact training environment:

  ```bash
  TMPDIR=/data/ycfeng/tmp \
  PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/tmp/tvcache-train-py312/bin/python \
    -m pytest -q tests/unit tests/integration

  TMPDIR=/data/ycfeng/tmp \
  UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache \
  UV_PROJECT_ENVIRONMENT=/data/ycfeng/tmp/tvcache-train-py312 \
  uv sync --project train --frozen --offline
  ```

- Verified result on 2026-08-16: 128/128 tests passed in 1.62 s on Python 3.12.3; frozen sync then removed exactly four test-only packages and restored 138 compatible distributions.

## Video-LLaVA bitsandbytes 0.41.0 SciPy dependency (2026-09-10)

- The real H800 loader failed at `bitsandbytes/functional.py:12` (`from scipy.stats import norm`). The installed bitsandbytes metadata does not declare SciPy.
- Install `scipy==1.15.3` in the Video-LLaVA Python 3.10 environment, keeping `numpy==1.26.2`. This matches the working VideoAgent SciPy version and satisfies SciPy's NumPy range `>=1.23.5,<2.5`.
- Verified via the actual loader import: `PASS loader_import 1.15.3 2.0.1+cu117 11.7`, process exit 0. GPU loading remains a separate check.
- Use the Basemind indexes documented in `/data/ycfeng/stepfun-env-handbook/python-package-mirror.md`; keep UV_CACHE_DIR and TMPDIR under `/data/ycfeng/tmp`.


## Video-LLaVA CUDA 11.8 library discovery on Hopper (2026-09-10)

- Actual H200 verification: `torch==2.0.1+cu118`, `torchvision==0.15.2+cu118`, `bitsandbytes==0.41.0`; CUDA zeros/sum returned 0.0 and both main checkpoint shards loaded (221.78 s). The full tower check is tracked separately in the task report.
- The cu118 Torch wheel bundles cuBLAS in `torch/lib`, while bitsandbytes also dynamically requires CUDA runtime and cuSPARSE libraries in the venv's existing NVIDIA packages. Without a process-local library path it fails with `libcusparse.so.11: cannot open shared object file`.
- Set this for the Video-LLaVA process only, preserving the independent VideoAgent process environment:

```bash
VIDEOLLAVA_SITE=/data/ycfeng/tmp/tvcache-videollava-20260909/lib/python3.10/site-packages
export LD_LIBRARY_PATH="$VIDEOLLAVA_SITE/torch/lib:$VIDEOLLAVA_SITE/nvidia/cuda_runtime/lib:$VIDEOLLAVA_SITE/nvidia/cusparse/lib:${LD_LIBRARY_PATH:-}"
```

- `ldd` resolves every dependency of `bitsandbytes/libbitsandbytes_cuda118.so` with this setting. No library download or binary substitution was needed.
