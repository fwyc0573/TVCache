#!/usr/bin/env bash
# Run the real local visual services, tool smoke, and provider cache comparison on H800.
set -euo pipefail
REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TASK_DIR="$REPO_DIR/task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction"
RUN_NAME="${JOB_ID:?Run this script in the allocated GPU worker}"
LOG_DIR="${LOG_DIR:-/data/ycfeng/tmp/$RUN_NAME}"
TRAIN_PYTHON=/data/ycfeng/tmp/tvcache-train-py312/bin/python
STEPCODE_CONFIG="${STEPCODE_CONFIG:-/data/ycfeng/home_offload/i-fengyicheng/.stepcode/config.json}"
mkdir -p "$LOG_DIR"
test -f "$STEPCODE_CONFIG" || { echo "Missing STEPCODE_CONFIG=$STEPCODE_CONFIG" >&2; exit 2; }
export TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1
if [ -f /data/ycfeng/tmp/issue26-h200-network/company-proxy.sh ]; then source /data/ycfeng/tmp/issue26-h200-network/company-proxy.sh; else eval "$(curl -fsS --max-time 20 http://deploy.i.shaipower.com/httpproxy)"; fi
export HTTP_PROXY="${http_proxy:-}" HTTPS_PROXY="${https_proxy:-}" ALL_PROXY="${all_proxy:-}"
export NO_PROXY="${no_proxy:-},127.0.0.1,localhost" no_proxy="${no_proxy:-},127.0.0.1,localhost"
export HF_HOME="${HF_HOME:-/data/ycfeng/tmp/tvcache-videollava-hf-cache-h800}"
export HF_HUB_CACHE="$HF_HOME" HUGGINGFACE_HUB_CACHE="$HF_HOME" TRANSFORMERS_CACHE="$HF_HOME"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1
export VIDEO_AGENT_MODEL_DIR=/data/ycfeng/tmp/videoagent_small
export VIDEO_AGENT_SANDBOX_DIR=/data/ycfeng/tmp/${JOB_ID}/sandboxes
export EGOSCHEMA_VIDEO_DIR=/data/ycfeng/tvcache_assets/egoschema/run-20260908/videos
export EGOSCHEMA_CACHE_DIR=/data/ycfeng/tmp/${JOB_ID}/egoschema-cache
export VIDEO_LLAVA_RUNTIME_DIR=/data/ycfeng/tmp/${JOB_ID}/videollava-runtime
export VIDEO_LLAVA_CACHE_DIR="${VIDEO_LLAVA_CACHE_DIR:-$HF_HOME}"
export TRANSFORMERS_CACHE="$VIDEO_LLAVA_CACHE_DIR" HF_HUB_CACHE="$VIDEO_LLAVA_CACHE_DIR"
export HUGGINGFACE_HUB_CACHE="$VIDEO_LLAVA_CACHE_DIR" MPLCONFIGDIR="$LOG_DIR/matplotlib"
export YOLO_CONFIG_DIR="$LOG_DIR/ultralytics"
mkdir -p "$VIDEO_AGENT_SANDBOX_DIR" "$EGOSCHEMA_CACHE_DIR" "$VIDEO_LLAVA_RUNTIME_DIR"
ln -sfn "$VIDEO_LLAVA_CACHE_DIR" "$VIDEO_LLAVA_RUNTIME_DIR/cache_dir"
test -x "$TRAIN_PYTHON"
"$TRAIN_PYTHON" -c 'import sys; print(f"TRAIN_PYTHON={sys.executable} {sys.version.split()[0]}", flush=True)'
export STEPCODE_BASE_URL=https://models-proxy.stepfun-inc.com
export STEPCODE_CONFIG
STEPCODE_API_KEY="$($TRAIN_PYTHON -c 'import json, os; from pathlib import Path; value=json.loads(Path(os.environ["STEPCODE_CONFIG"]).read_text())["apiKey"]; assert isinstance(value,str) and value.strip(); print(value,end="")')"
export STEPCODE_API_KEY
echo 'STEPCODE_API_KEY=SET'
IFS=',' read -r -a worker_gpus <<< "${CUDA_VISIBLE_DEVICES:-0,1}"
test "${#worker_gpus[@]}" -eq 2
service_pids=()
cleanup() {
    result=$?
    trap - EXIT
    for pid in "${service_pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then kill -TERM -- "-$pid" || true; fi
    done
    for pid in "${service_pids[@]}"; do
        if wait "$pid"; then code=0; else code=$?; fi
        echo "service_pid=$pid exit_code=$code"
    done
    exit "$result"
}
trap cleanup EXIT
cd "$VIDEO_LLAVA_RUNTIME_DIR"
VIDEOLLAVA_SITE=/data/ycfeng/tmp/tvcache-videollava-20260909/lib/python3.10/site-packages
CUDA_VISIBLE_DEVICES="${worker_gpus[1]}" PYTHONPATH="$REPO_DIR/video-agent-tools/Video-LLaVA" \
    LD_LIBRARY_PATH="$VIDEOLLAVA_SITE/torch/lib:$VIDEOLLAVA_SITE/nvidia/cuda_runtime/lib:$VIDEOLLAVA_SITE/nvidia/cusparse/lib:${LD_LIBRARY_PATH:-}" \
    setsid /data/ycfeng/tmp/tvcache-videollava-20260909/bin/python -u \
    "$REPO_DIR/video-agent-tools/VideoAgent/video-llava.py" > "$LOG_DIR/vqa.log" 2>&1 &
service_pids+=("$!")
CUDA_VISIBLE_DEVICES="${worker_gpus[0]}" setsid /data/ycfeng/tmp/tvcache-videoagent-20260909/bin/python -u \
    "$REPO_DIR/video-agent-tools/VideoAgent/sandbox_server.py" > "$LOG_DIR/sandbox.log" 2>&1 &
service_pids+=("$!")
setsid "$TRAIN_PYTHON" -u "$REPO_DIR/tvcache/server/tvcache_server.py" > "$LOG_DIR/cache.log" 2>&1 &
service_pids+=("$!")
NVIDIA_SMI="$(command -v nvidia-smi || true)"
if [ -z "$NVIDIA_SMI" ]; then
    NVIDIA_SMI="$(find /usr /opt /bin -type f -name nvidia-smi -perm -u+x -print -quit 2>/dev/null || true)"
fi
test -n "$NVIDIA_SMI" || { echo 'nvidia-smi executable is required but was not found in the worker image' >&2; exit 2; }
echo "NVIDIA_SMI=$NVIDIA_SMI"
setsid "$NVIDIA_SMI" --query-gpu=timestamp,index,name,memory.used,memory.total --format=csv -l 1 > "$LOG_DIR/gpu-memory.csv" &
service_pids+=("$!")
deadline=$((SECONDS + 1200))
last_readiness_diag=0
until test -S "$VIDEO_LLAVA_RUNTIME_DIR/vqa.sock" && \
    grep -q '^ready for connection!' "$LOG_DIR/vqa.log" && \
    curl -fsS 'http://127.0.0.1:8001/get?task_name=runtime-smoke' > "$LOG_DIR/cache-health.json" && \
    curl -sS -o /dev/null http://127.0.0.1:5000/; do
    for pid in "${service_pids[@]}"; do
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "service_pid=$pid exited before readiness" >&2
            for logfile in "$LOG_DIR/vqa.log" "$LOG_DIR/sandbox.log" "$LOG_DIR/cache.log"; do
                if [ -f "$logfile" ]; then
                    echo "===== $logfile (tail) =====" >&2
                    tail -100 "$logfile" >&2 || true
                fi
            done
            exit 1
        fi
    done
    if (( SECONDS - last_readiness_diag >= 60 )); then
        last_readiness_diag=$SECONDS
        echo "===== readiness diagnostics at ${SECONDS}s =====" >&2
        for logfile in "$LOG_DIR/vqa.log" "$LOG_DIR/sandbox.log" "$LOG_DIR/cache.log"; do
            if [ -f "$logfile" ]; then
                echo "--- $logfile (tail) ---" >&2
                tail -40 "$logfile" >&2 || true
            fi
        done
    fi
    test "$SECONDS" -lt "$deadline"
    sleep 2
done
"$TRAIN_PYTHON" "$REPO_DIR/tests/e2e/videoagent_tool_smoke.py" \
    --manifest "$TASK_DIR/egoschema_manifest_2026-09-08.json" \
    --output "$TASK_DIR/$RUN_NAME-tool-smoke.json" > "$LOG_DIR/tool-smoke.log" 2>&1
PYTHONPATH="$REPO_DIR/train:$REPO_DIR/tvcache/client:$REPO_DIR/train/tinker-cookbook" \
    "$TRAIN_PYTHON" -u "$REPO_DIR/tests/e2e/provider_cache_rollout.py" \
    --manifest "$TASK_DIR/egoschema_manifest_2026-09-08.json" \
    --output "$TASK_DIR/$RUN_NAME-rollouts" > "$LOG_DIR/rollouts.log" 2>&1
