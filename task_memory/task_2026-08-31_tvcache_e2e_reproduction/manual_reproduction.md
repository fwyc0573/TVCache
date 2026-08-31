## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-08-31 | Add evidence-backed Chinese manual for TVCache server/client/video training reproduction |
| 2026-08-31 | Isolate reruns, document training port and GPU assignment, and close the guide sequence |
| 2026-08-31 | Align the five-terminal map and record the fresh isolated-port verification |

# TVCache E2E 人工复现手册

本文面向需要在本机或 GPU worker 上手动复现 TVCache 的读者。命令均以当前仓库为基准，先建立最小的 server/client protocol smoke，再逐步连接 Video-LLaVA、VideoAgent sandbox、EgoSchema 和 Tinker training。

本文把“源码 README 中写的流程”和“当前 checkout 实际能运行的流程”分开记录。当前 checkout 已经真实验证了 TVCache server/client smoke；完整 VideoAgent/Tinker training 因运行时依赖、模型权重、视频数据和 credentials 未就绪而停在 preflight，本文不会把它表述为已通过。

## 1. 当前结论和复现边界

### 1.1 已经验证的路径

在 `127.0.0.1:18001` 上启动 server 后，下面的调用真实返回 HTTP 200：

- `PUT /put`：使用 `values` 和 `tool_exec_times` 数组写入一条路径。
- `GET /get`：精确取回 `env_id`、`value` 和 `tool_exec_time`。
- `POST /prefix_match`：取回最长已缓存前缀。
- `GET /visualize`：看到 `cache_hits`、`prefix_hits` 和节点值。
- `GET /get_all_envs`：列出 task 下的环境 ID。
- async client 的 `exact_match`、`put`、`get`、`prefix_match`、`unref`、`get_test_result` 等调用。

观测记录：

```text
manual smoke: PUT=200, GET=200, PREFIX_MATCH=200, GET_ALL_ENVS=200
GET value=ready, tool_exec_time=0.875
visualize cache_hits=1, prefix_hits=1
async probe: exact_before=False, exact_after=True
async probe: get=('env-async', 'result-x', 0.125)
async probe: test_result=(True, 'PASS')
```

原始日志位于：

- `/data/ycfeng/tmp/tvcache_manual_smoke.log`
- `/data/ycfeng/tmp/tvcache_async_client_probe.log`

### 1.2 当前没有通过的路径

完整路径需要以下进程和资源同时可用：

```text
TVCache server
    -> train AsyncSemanticStatefulExecutor
        -> VideoSandboxEnv/SandboxClient
            -> VideoAgent sandbox HTTP server :5000
                -> Video-LLaVA Unix socket tmp/vqa.sock
                    -> GPU model/tool weights + EgoSchema videos
        -> Tinker sampling/training service + TINKER_API_KEY
```

本次 preflight 的实际阻塞如下：

- `sandbox_server.py` 在系统 Python 下于 Flask 绑定前退出，错误为 `RuntimeError: operator torchvision::nms does not exist`，说明当前 Torch/Torchvision binary 不匹配。
- `video-agent-tools/VideoAgent/cache_dir/`、`tool_models/`、`egoschema_cache/` 和 `train/EgoSchema/videos/` 不存在。
- `train/.venv` 是约 `68 KiB` 的裸环境，导入 `train_with_tvcache` 时报告 `ModuleNotFoundError: No module named 'pydantic'`。
- `train/pyproject.toml` 只声明 `tinker`，而入口还导入 `chz`、`datasets` 和 sibling `tinker-cookbook`；正常 train sync 后仍需显式安装 cookbook。
- `EgoSchema/download.py` 需要 `gdown`，当前 train manifest 没有声明它。
- `SandboxManager.load_video_into_sandbox()` 使用字面路径 `path/to/train/EgoSchema/videos/<video_name>`，该路径不在当前 checkout。

完整 preflight 报告：`test_report_2026-08-31_train_sandbox_preflight.md`。读者可以先完成 server/client smoke，再按后文的 prerequisites 修复环境，最后重新尝试 training。

## 2. 环境检查

### 2.1 统一仓库和日志变量

在每个 terminal 先执行以下命令。 `TVCACHE_LOG_DIR` 指向持久 workspace 下的临时日志目录，避免把大日志写入 memory-backed `/tmp`。

```bash
export TVCACHE_ROOT=/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache
export TVCACHE_LOG_DIR=/data/ycfeng/tmp/tvcache_e2e_reproduction
mkdir -p "$TVCACHE_LOG_DIR"
cd "$TVCACHE_ROOT"
```

建议使用五个 terminal，并保持各 terminal 的工作目录明确。T4 只在运行完整 training 时启用；只做 server/client smoke 时使用 T1-T3 即可：

| Terminal | 工作目录 | 角色 | 主要输出 |
| --- | --- | --- | --- |
| T1 | `tvcache/server` | smoke 用 TVCache HTTP server（例如 `18001`） | Flask access log、server traceback |
| T2 | `video-agent-tools/Video-LLaVA` 后切到 `VideoAgent` | Video-LLaVA VQA socket | model loading、`ready for connection!` |
| T3 | `video-agent-tools/VideoAgent` | VideoAgent sandbox HTTP server | Flask log、tool traceback、`sandboxes/` |
| T4 | `tvcache/server` | training 专用 TVCache HTTP server（`8001`） | training server access log、cache traceback |
| T5 | `train` | Tinker training + agent rollouts | `logs.log`、`metrics.jsonl`、`rollouts/*.log` |

### 2.2 读取版本和硬件状态

```bash
cd "$TVCACHE_ROOT"
python3 --version
uv --version
conda --version
ffmpeg -version | head -n 1
nvidia-smi
```

接受标准：

- server 和 client 要求 Python `>=3.10`；train 要求 Python `>=3.12`。
- VideoAgent README 要求 Ubuntu 20.04+、两张 NVIDIA GPU 和 FFmpeg。
- Video-LLaVA README 要求 Python `>=3.10`、CUDA `>=11.7`。
- `nvidia-smi` 输出为空或命令不存在时，先把 full video workflow 视为未满足硬件前置条件，不要把 server smoke 的通过结果外推到 training。

### 2.3 检查仓库资源和 lock 文件

```bash
cd "$TVCACHE_ROOT/tvcache/server" && uv lock --check
cd "$TVCACHE_ROOT/tvcache/client" && uv lock --check
cd "$TVCACHE_ROOT/train" && uv lock --check
cd "$TVCACHE_ROOT"
for path in \
  video-agent-tools/VideoAgent/cache_dir \
  video-agent-tools/VideoAgent/tool_models \
  video-agent-tools/VideoAgent/egoschema_cache \
  train/EgoSchema/videos; do
  test -e "$path" && printf 'FOUND  %s\n' "$path" || printf 'MISSING %s\n' "$path"
done
```

本次观测：server、client、train 的 `uv lock --check` 均通过；server lock 在本任务中补齐了 `pyproject.toml` 已声明但原 lock 缺失的 `gunicorn 26.2.0` 条目，随后 `uv sync --locked --dry-run` 报告 `Would make no changes`。client lock 输出约 `22` 个 package，train lock 输出约 `39` 个 package；上述模型和视频目录均缺失。metadata 文件仍然存在：

```text
train/EgoSchema/processed_videos.json  137543 bytes
train/EgoSchema/questions.json         4562127 bytes
train/EgoSchema/subset_answers.json    21500 bytes
```

## 3. 启动 TVCache server

### 3.1 安装 server 依赖

`tvcache/server/` 是命令的工作目录；从仓库根目录直接执行 `uv run tvcache_server.py` 会得到 `No such file or directory`。

```bash
cd "$TVCACHE_ROOT/tvcache/server"
uv sync --locked
uv run tvcache_server.py --help
```

当前 CLI help 的核心参数：

```text
--host HOST
--port PORT
--debug
--auto-save
--save-interval SAVE_INTERVAL
```

### 3.2 显式固定 host 和 port

代码存在三个默认值来源，人工复现时始终显式传入端口：

| 来源 | 默认值 | 位置/影响 |
| --- | --- | --- |
| `run_server()` | `0.0.0.0:8000` | `tvcache_server.py:696-715` |
| `__main__` CLI | `0.0.0.0:8001` | `tvcache_server.py:721-731` |
| README 和同步 client | `localhost:8000` | 文档及 `tvcache_client.py` |
| async client | `localhost:8001` | `async_tvcache_client.py:10`；training executor 默认使用它 |

选择一个没有被占用的端口，例如 `18001`：

```bash
export TVCACHE_HOST=127.0.0.1
export TVCACHE_PORT=18001
cd "$TVCACHE_ROOT/tvcache/server"
set -o pipefail
uv run tvcache_server.py \
  --host "$TVCACHE_HOST" \
  --port "$TVCACHE_PORT" \
  2>&1 | tee "$TVCACHE_LOG_DIR/server_${TVCACHE_PORT}.log"
```

server 正常运行时，终端会显示 Flask development server 的 bind 信息。另开 terminal 检查监听状态：

```bash
ss -ltnp | rg ":${TVCACHE_PORT}\b"
curl -fsS "http://${TVCACHE_HOST}:${TVCACHE_PORT}/get?task_name=health"
```

`/get` 对不存在的 task 仍应返回 HTTP 200 和 `found:false`。server 进程重启会清空 module-level `cache`，每次新进程都要重新 PUT 数据。

### 3.3 可选的 auto-save

```bash
cd "$TVCACHE_ROOT/tvcache/server"
set -o pipefail
uv run tvcache_server.py \
  --host 127.0.0.1 \
  --port 18001 \
  --auto-save \
  --save-interval 60 \
  2>&1 | tee "$TVCACHE_LOG_DIR/server_18001_autosave.log"
```

CLI 的 `--save-interval` 默认是 `3000` 秒，`run_server()` 的函数默认是 `300` 秒。周期 worker 写入 `~/susRL/tv-cache/data/runs/auto-saved/`，shutdown handler 却写入 `~/tv-cache/data/runs/auto-saved/`；以 server 输出的 `[Auto-save]` 绝对路径为准，并检查两处目录。

### 3.4 查看实际注册路由

```bash
cd "$TVCACHE_ROOT/tvcache/server"
uv run flask --app tvcache_server:app routes
```

当前实现没有 `/lock` 和 `/unlock` 路由，虽然 `tvcache/server/README.md` 仍然列出它们。实际可见的 cache control 路由包括 `/put`、`/get`、`/prefix_match`、`/intel_prefix_match`、`/mark_stateless`、`/remove`、`/can_extend`、`/should_fork`、`/visualize`、`/get_hot_nodes`、`/check_env_marked`、`/store_test_result`、`/get_test_result`、`/unref` 和 `/get_all_envs`。

## 4. Server protocol smoke

这一节不需要 Tinker、GPU、VideoAgent 或真实视频。它是判断 server/client 基础协议是否工作的最小案例。

### 4.1 使用当前实现兼容的 PUT payload

`ImmutableEnvPrefixTreeCache.put()` 在 `values` 和 `tool_exec_times` 被提供时按 history 下标读取数组。README 和旧 helper 使用单值 `value` 字段，在当前实现会导致 `TypeError: 'NoneType' object is not subscriptable`（`immutable_env_prefix_tree.py:225-230`）。使用以下数组格式：

```bash
export TVCACHE_BASE=http://127.0.0.1:18001
export TVCACHE_TASK="manual-$(date +%Y%m%d-%H%M%S)"
export TVCACHE_ENV="env-${TVCACHE_TASK}"

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X PUT "$TVCACHE_BASE/put" \
  -H 'Content-Type: application/json' \
  -d @- <<JSON
{
  "task_name": "${TVCACHE_TASK}",
  "history": ["load", "preprocess"],
  "env_id": "${TVCACHE_ENV}",
  "values": ["loaded", "ready"],
  "tool_exec_times": [0.125, 0.875],
  "start_idx": 0
}
JSON
```

期望：HTTP `200`，JSON 中 `success:true` 和 `removed_env_ids:[]`。

### 4.2 exact GET、prefix match 和 tree inspection

```bash
curl -sS -w '\nHTTP=%{http_code}\n' --get "$TVCACHE_BASE/get" \
  --data-urlencode "task_name=$TVCACHE_TASK" \
  --data-urlencode 'tool_calls=load' \
  --data-urlencode 'tool_calls=preprocess'

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$TVCACHE_BASE/prefix_match" \
  -H 'Content-Type: application/json' \
  -d "{\"task_name\":\"$TVCACHE_TASK\",\"tool_calls\":[\"load\",\"preprocess\",\"next\"]}"

curl -sS "$TVCACHE_BASE/visualize" > "$TVCACHE_LOG_DIR/tree_$TVCACHE_TASK.json"
curl -sS -w '\nHTTP=%{http_code}\n' --get "$TVCACHE_BASE/get_all_envs" \
  --data-urlencode "task_name=$TVCACHE_TASK"
```

期望值：

```text
GET: found=true, env_id=$TVCACHE_ENV, value=ready, tool_exec_time=0.875
prefix_match: found=true, history=["load", "preprocess"]
visualize: cache_hits=1, prefix_hits=1 on the final node
get_all_envs: ["$TVCACHE_ENV"]
```

### 4.3 test result、unref 和环境计数

```bash
curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$TVCACHE_BASE/store_test_result" \
  -H 'Content-Type: application/json' \
  -d "{\"task_name\":\"$TVCACHE_TASK\",\"history\":[\"load\",\"preprocess\"],\"test_result\":\"PASS\"}"

curl -sS --get "$TVCACHE_BASE/get_test_result" \
  --data-urlencode "task_name=$TVCACHE_TASK" \
  --data-urlencode 'tool_calls=load' \
  --data-urlencode 'tool_calls=preprocess'

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$TVCACHE_BASE/unref" \
  -H 'Content-Type: application/json' \
  -d "{\"task_name\":\"$TVCACHE_TASK\",\"env_id\":\"$TVCACHE_ENV\"}"
```

async probe 中 `get_test_result` 真实返回 `(True, 'PASS')`。`AsyncTVCacheClient.store_test_result()` 收到 HTTP 200 后的 Python 返回值曾为 `None`，原因是 immutable server 的 `store_test_result()` 没有显式 `return`；判断持久化结果时读取 `get_test_result()`。

### 4.4 保存和浏览运行记录

手动把当前内存 tree 保存到运行目录：

```bash
curl -sS -X POST "$TVCACHE_BASE/api/save" \
  -H 'Content-Type: application/json' \
  -d "{\"run_name\":\"manual-guide\",\"epoch\":0,\"data\":$(curl -sS \"$TVCACHE_BASE/visualize\")}" \
  | tee "$TVCACHE_LOG_DIR/api_save_response.json"
```

响应中的 `path` 是绝对文件路径，`relative_path` 可用于后续查看。运行列表和 web 页面：

```bash
curl -sS "$TVCACHE_BASE/api/runs"
```

浏览器地址：

```text
http://127.0.0.1:18001/runs
http://127.0.0.1:18001/visualizer.html
http://127.0.0.1:18001/visualize?path=<relative_path_without_.json>
```

`/api/runs` 只扫描 `~/susRL/tv-cache/data/runs`。当目录不存在时它会返回 HTTP 404 和 `base_dir`，这表示还没有保存记录，不表示 server protocol 失败。

### 4.5 旧 helper 的使用边界

README 推荐的命令是：

```bash
cd "$TVCACHE_ROOT/tvcache/server"
uv run tests/simple_test_server.py
```

当前 helper 的 `TVCacheTestClient.put()` 仍发送单值 `value` 字段，并且 `test_multiple_updates()` 不检查中间 HTTP status；它曾在大量 500 的情况下打印 `Passed: 1/1`。把这个输出当作非权威结果，优先使用本节的数组 payload 和逐请求 HTTP 状态。

## 5. 启动 Video-LLaVA

完整 video workflow 需要 GPU 和下载的 weights。以下命令来自 `video-agent-tools/Video-LLaVA/README.md` 与 `video-agent-tools/VideoAgent/README.md`，尚未在本环境成功跑通。

### 5.1 创建独立环境

```bash
cd "$TVCACHE_ROOT/video-agent-tools/Video-LLaVA"
uv venv --python 3.10 .venv
source .venv/bin/activate
uv pip install -e .
uv pip install flash-attn --no-build-isolation
uv pip install decord opencv-python \
  git+https://github.com/facebookresearch/pytorchvideo.git@28fe037d212663c6a24f373b94cc5d478c8c1a1d
```

### 5.2 准备 model cache

把 Zenodo 的 `cache_dir.zip` 解压到 `video-agent-tools/VideoAgent/`，把 `tool_models.zip` 也解压到同一目录：

```bash
cd "$TVCACHE_ROOT/video-agent-tools/VideoAgent"
wget https://zenodo.org/records/11031717/files/cache_dir.zip
wget https://zenodo.org/records/11031717/files/tool_models.zip
unzip cache_dir.zip
unzip tool_models.zip
test -d cache_dir
test -d tool_models
```

`video-llava.py` 固定从 `cache_dir` 加载 `LanguageBind/Video-LLaVA-7B`，并在 `VideoAgent/tmp/vqa.sock` 建立 Unix socket。

### 5.3 启动并确认 VQA ready

```bash
cd "$TVCACHE_ROOT/video-agent-tools/Video-LLaVA"
source .venv/bin/activate
cd ../VideoAgent
set -o pipefail
CUDA_VISIBLE_DEVICES=0 python video-llava.py \
  2>&1 | tee "$TVCACHE_LOG_DIR/video_llava.log"
```

等到日志出现：

```text
ready for connection!
```

只看到进程存在或 HTTP sandbox 端口打开，不能证明 VQA ready；`tmp/vqa.sock` 和上述 ready 行都要检查。

本次失败证据：

```text
RuntimeError: operator torchvision::nms does not exist
```

完整日志：`/data/ycfeng/tmp/tvcache-sandbox-startup.log`。这次错误发生在导入 `captioning.py` 的 torchvision 阶段，Flask 尚未绑定 5000。

## 6. 启动 VideoAgent sandbox

### 6.1 创建 Conda 环境

```bash
cd "$TVCACHE_ROOT/video-agent-tools/VideoAgent"
conda env create -f environment.yaml -p ./cenv
conda activate ./cenv
ffmpeg -version | head -n 1
```

`environment.yaml` 当前固定 Python `3.9.18`，而 Video-LLaVA 使用独立 Python 3.10 venv；两个 process 不要混用环境。

### 6.2 设置变量并启动

`run_sandbox.sh` 当前内容会把 `OPENAI_API_KEY` 直接设为字面量 `your_key`，并固定 `CUDA_VISIBLE_DEVICES=0`。手动复现时直接运行 Python，确保 key 真正来自当前 shell。建议把 Video-LLaVA 放在 GPU `0`、sandbox 放在 GPU `1`；只有一张 GPU 时才复用同一 ID，并将其标为受限 smoke：

```bash
cd "$TVCACHE_ROOT/video-agent-tools/VideoAgent"
conda activate ./cenv
export OPENAI_API_KEY='<your-openai-key>'
export CUDA_VISIBLE_DEVICES=1
set -o pipefail
python3 sandbox_server.py \
  2>&1 | tee "$TVCACHE_LOG_DIR/video_agent_sandbox.log"
```

正常情况下 Flask 监听 `0.0.0.0:5000`。sandbox API 的所有请求都使用 POST JSON，`sandbox_id` 必填：

```bash
export SANDBOX_BASE=http://127.0.0.1:5000
export SANDBOX_ID=manual-sandbox-20260831

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$SANDBOX_BASE/start" \
  -H 'Content-Type: application/json' \
  -d "{\"sandbox_id\":\"$SANDBOX_ID\"}"

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$SANDBOX_BASE/execute" \
  -H 'Content-Type: application/json' \
  -d "{\"sandbox_id\":\"$SANDBOX_ID\",\"command\":\"load_video_into_sandbox\",\"argument\":\"<video-file>.mp4\"}"

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$SANDBOX_BASE/execute" \
  -H 'Content-Type: application/json' \
  -d "{\"sandbox_id\":\"$SANDBOX_ID\",\"command\":\"preprocess\",\"argument\":\"\"}"

curl -sS -w '\nHTTP=%{http_code}\n' \
  -X POST "$SANDBOX_BASE/stop" \
  -H 'Content-Type: application/json' \
  -d "{\"sandbox_id\":\"$SANDBOX_ID\"}"
```

`/execute` 支持 `load_video_into_sandbox`、`preprocess`、`object_memory_querying`、`segment_localization`、`caption_retrieval` 和 `visual_question_answering`。长时间 `preprocess` 在 `SandboxClient` 中使用 300 秒 timeout。

### 6.3 sandbox 路径前置检查

当前 `sandbox_manager.py:96-109` 使用：

```python
source_path = os.path.join('path/to/train/EgoSchema/videos', video_name)
```

因此即使 `/start` 能返回 200，`load_video_into_sandbox` 仍会在当前 checkout 因找不到 literal path 返回 500。调试时先查看 sandbox 进程工作目录和该路径，再决定是否做经过审查的路径配置修改；不要用一个临时软链接掩盖根因。

## 7. EgoSchema 下载和处理

### 7.1 下载视频

必须从 `train/EgoSchema` 目录运行，因为脚本用相对路径读取 `questions.json` 和 `subset_answers.json`：

```bash
cd "$TVCACHE_ROOT/train/EgoSchema"
uv pip install gdown
set -o pipefail
uv run download.py 2>&1 | tee "$TVCACHE_LOG_DIR/egoschema_download.log"
```

脚本固定 `random.seed(8)`，从有公开答案的 subset 中随机取 250 个视频，并写入 `videos/<q_uid>.mp4`。下载前先确认磁盘容量和 Google Drive 网络可达。

本次直接运行 `../.venv/bin/python download.py` 的结果是 `ModuleNotFoundError: No module named 'gdown'`；`gdown` 没有出现在 `train/pyproject.toml`，所以必须显式安装并记录环境变更。

### 7.2 生成 processed_videos.json

```bash
cd "$TVCACHE_ROOT/train/EgoSchema"
set -o pipefail
uv run process_videos.py 2>&1 | tee "$TVCACHE_LOG_DIR/egoschema_process.log"
```

期望输出包含 `Found <N> videos`、`Processed <N> videos successfully` 和 `Results saved to processed_videos.json`。没有 `videos/` 目录时，脚本在 `os.listdir('videos')` 处报告 `FileNotFoundError`；本次正是该结果。

### 7.3 验证 metadata 与视频文件

```bash
cd "$TVCACHE_ROOT/train"
python3 - <<'PY'
import json
from pathlib import Path

metadata = Path('EgoSchema/processed_videos.json')
data = json.loads(metadata.read_text())
print('metadata_entries=', len(data))
print('first_video_id=', data[0]['video_id'] if data else None)
print('video_dir_exists=', Path('EgoSchema/videos').is_dir())
PY
```

`train_with_tvcache.py:get_video_dataset()` 读取 `./EgoSchema/processed_videos.json`，把 prompt 文件中的问题展开，最后只保留前 100 条；它不会自动下载视频。

## 8. 安装 train 依赖并启动 training

### 8.1 安装和 import probe

从 `train/` 目录同步依赖并安装两个本地 editable package：

```bash
cd "$TVCACHE_ROOT/train"
uv sync --locked
uv pip install -e ./tinker-cookbook
uv pip install -e ../tvcache/client

uv run python - <<'PY'
import importlib.util
names = ["pydantic", "chz", "datasets", "tinker", "tinker_cookbook", "httpx", "tvclient"]
for name in names:
    print(f"{name}={bool(importlib.util.find_spec(name))}")
PY
```

只有这些包全部显示 `True`，才进入训练入口。`train/.venv` 目前是约 `68 KiB` 的裸环境；本次 `uv run --no-sync python train_with_tvcache.py --help` 以退出码 `1` 失败，首个错误是 `ModuleNotFoundError: No module named 'pydantic'`。`train/pyproject.toml` 只声明 `tinker>=0.6.3`，cookbook 的 `chz`、`datasets` 和 `tinker_cookbook` 依赖必须单独核对。

### 8.2 直接运行入口

仓库没有实际存在的 `train/run.sh`（`train/.gitignore` 还会忽略该文件），因此使用 Python 入口并显式设置路径：

training 的 async client 当前默认连接 `http://localhost:8001`。保留 `18001` 上的 smoke server 进行协议检查时，在另一个 terminal 启动一个 training 专用 server，并先确认 `8001` 没有被其他服务占用：

```bash
cd "$TVCACHE_ROOT/tvcache/server"
if ss -ltn | rg -q ':8001\b'; then
  printf 'port 8001 is already occupied\n' >&2
  exit 1
fi
set -o pipefail
uv run tvcache_server.py --host 127.0.0.1 --port 8001 \
  2>&1 | tee "$TVCACHE_LOG_DIR/server_8001_training.log"
```

不要把只监听 `18001` 的 smoke server 当作 training 的 cache endpoint；除非把 URL 注入 executor，否则 async client 会把 `8001` 的连接失败转换成假 miss。

```bash
cd "$TVCACHE_ROOT/train"
mkdir -p rollouts
export TVCACHE_BASE=http://127.0.0.1:8001
curl -fsS "$TVCACHE_BASE/get?task_name=health" >/dev/null
: "${TINKER_API_KEY:?export TINKER_API_KEY with a real key before this block}"
: "${OPENAI_API_KEY:?export OPENAI_API_KEY with a real key before this block}"
export RUN_DIR="$TVCACHE_ROOT/task_memory/task_2026-08-31_tvcache_e2e_reproduction/artifacts/train-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN_DIR"

set -o pipefail
uv run python train_with_tvcache.py \
  --config.log_path="$RUN_DIR" \
  --config.batch_size=2 \
  --config.group_size=2 \
  --config.epochs=1 \
  --config.num_turns=5 \
  --config.max_tokens=1024 \
  --config.sandbox_base_url=http://127.0.0.1:5000 \
  2>&1 | tee "$TVCACHE_LOG_DIR/train_latest.log"
```

训练前必须同时满足：TVCache server 在 `8001`、sandbox 在 `5000`、Video-LLaVA 输出 `ready for connection!`、EgoSchema 视频存在，以及 Tinker/OpenAI credentials 有效。`AsyncSemanticStatefulExecutor` 创建 async client 时使用默认 `http://localhost:8001`，所以将 server 运行在 `18001` 不会自动改变 training 的目标地址。

### 8.3 chz 参数和默认值

入口通过 `asyncio.run(chz.nested_entrypoint(main))` 解析 CLI；格式是 `--config.<field>=<value>`。默认值来自 `train/train_with_tvcache.py:24-38`：

| 参数 | 默认值 | 实际影响 |
| --- | --- | --- |
| `base_url` | `None` | Tinker `ServiceClient` 地址，不是 TVCache URL |
| `log_path` | `./tests/rebuttal_cache` | 训练记录目录；建议使用绝对路径 |
| `model_name` | `Qwen/Qwen3-30B-A3B-Instruct-2507` | Tinker base model |
| `batch_size` | `4` | 每个 batch 的 data point 数 |
| `group_size` | `8` | 每个 data point 的 rollout 数 |
| `learning_rate` | `4e-5` | Adam learning rate |
| `max_length` | `32768` | 当前仅声明在 Config；rollout guard 仍硬编码 32768 |
| `lora_rank` | `32` | LoRA rank |
| `save_every` | `5` | 保存 state checkpoint 的 batch 间隔 |
| `max_tokens` | `1024` | 每轮 generation 上限 |
| `num_turns` | `5` | 每个 rollout 最大 agent turn 数 |
| `sandbox_base_url` | `http://localhost:5000` | 设计上的 sandbox 地址；当前环境类仍硬编码该地址 |
| `epochs` | `10` | 数据集重复遍历次数 |

脚本读取 `./prompt.txt` 和 `./EgoSchema/processed_videos.json`，并只使用前 100 条 metadata。`--config.log_path`、`--config.batch_size` 等参数要与 `=` 连写；shell 中包含空格的路径整体加引号。

## 9. 日志、运行记录和输出

| 组件 | 路径或查看方式 | 关键证据 |
| --- | --- | --- |
| TVCache server | `$TVCACHE_LOG_DIR/server_<port>.log`（由 `tee` 创建） | Flask access log、500 traceback、`[Auto-save]` 路径 |
| 内存 TCG | `GET /visualize`；浏览器 `/visualizer.html` | `env_id`、`value`、`cache_hits`、`prefix_hits`、children |
| 手动保存 tree | `POST /api/save` 返回的 `path`/`relative_path` | JSON 运行快照 |
| 运行列表 | `GET /api/runs` 或 `/runs` | `~/susRL/tv-cache/data/runs` 中的文件；目录不存在时返回 404 |
| rollout | `train/rollouts/<sandbox_id>.log` | `CACHE HIT/MISS`、`[ENV]`、`[TOOL EXEC]`、`[SKIPPING]`、`[GEN-TIME]`、`[TOOL-TIME]` |
| fork bank | `fork_cache_server.log`，相对于启动 train 的 cwd | deposit/withdraw 和 fork 数量 |
| train metrics | `$RUN_DIR/metrics.jsonl` | `progress/batch`、`time/total`、`reward/average`、`reward/list` |
| train config/code | `$RUN_DIR/config.json`、`$RUN_DIR/code.diff` | Config 快照和代码状态 |
| train Python log | `$RUN_DIR/logs.log` | logging 输出、异常和 Tinker 请求信息 |
| checkpoints | `$RUN_DIR/checkpoints.jsonl` | checkpoint 名、batch、state/sampler path |
| sandbox | `$TVCACHE_LOG_DIR/video_agent_sandbox.log`、`VideoAgent/sandbox.log` | endpoint 结果、模型错误、traceback |
| 视频沙箱状态 | `video-agent-tools/VideoAgent/sandboxes/`、`tmp/vqa.sock` | sandbox 目录和 VQA socket |

训练日志由 `tinker_cookbook.utils.ml_log.setup_logging()` 创建：`metrics.jsonl`、`config.json`、`code.diff` 和 `logs.log`。`checkpoint_utils.save_checkpoint_async()` 追加 `checkpoints.jsonl`。常用查看命令：

```bash
tail -f "$TVCACHE_LOG_DIR/server_18001.log"
tail -f "$TVCACHE_LOG_DIR/train_latest.log"
rg -n 'CACHE HIT|CACHE MISS|\[ENV\]|\[TOOL EXEC\]|\[SKIPPING\]|GEN-TIME|TOOL-TIME|PARSE-ERROR' \
  "$TVCACHE_ROOT/train/rollouts"
sed -n '1,20p' "$RUN_DIR/metrics.jsonl"
tail -n 20 "$RUN_DIR/checkpoints.jsonl"
```

## 10. 调试和修改 TVCache 核心逻辑

### 10.1 调用链

```text
train/train_with_tvcache.py
  -> train/tvc_agent_loop.py:VideoAgentLoop
    -> tvcache/client/tvclient/tools/async_semantic_stateful_executor.py
      -> tvcache/client/tvclient/utils/async_tvcache_client.py
        -> tvcache/server/tvcache_server.py
          -> tvcache/server/tvcache/immutable_env_prefix_tree.py
```

视频后端链路是：

```text
VideoAgentLoop -> VideoSandboxEnv
  -> train/utils/video_sandbox_client.py
  -> video-agent-tools/VideoAgent/sandbox_server.py
  -> video-agent-tools/VideoAgent/sandbox_manager.py
```

### 10.2 每次修改的验证循环

1. 为实验生成新的 `task_name`，先 `GET /get` 确认 `found:false`。
2. 用 `curl -v` 和 server access log 核对 method、URL、query/body、status code。
3. 用 `GET /visualize` 把 tree 的 `children`、`env_id`、`value`、命中计数与发送的 history 对照。
4. 用 `rg` 查看对应 rollout log，区分 exact hit、prefix hit、fork 和重新执行。
5. 500 时先阅读 server traceback 的最后一个业务 frame；不要让 client 的假 miss 掩盖 HTTP 错误。
6. 修改后执行 `compileall`，再运行 HTTP smoke；executor 修改再运行 fake `ToolCallEnv` probe，最后才运行完整 training。

### 10.3 编辑点和当前已证实的根因

| 目标 | 文件/符号 | 当前观察 |
| --- | --- | --- |
| tree 存储和匹配 | `tvcache/server/tvcache/immutable_env_prefix_tree.py` | `put/get/prefix_match/unref/serialize` 决定 node 状态和数组索引 |
| HTTP contract | `tvcache/server/tvcache_server.py` | endpoint 解析请求并把 tree 异常重新抛出 |
| async client | `tvcache/client/tvclient/utils/async_tvcache_client.py` | 默认端口 8001；部分 HTTPError 被转换成假结果 |
| cache/fork 决策 | `.../async_semantic_stateful_executor.py` | `exact_match`、`prefix_match`、`_execute_and_put`、`unref` |
| rollout/sandbox 适配 | `train/tvc_agent_loop.py` | tool schema、mutation 判断、日志、prompt guard |
| sandbox transport | `train/utils/video_sandbox_client.py` | `/start`、`/execute`、`/fork`、`/stop` 和 timeout |

已确认的代码问题，修改时要针对根因并用上述循环复测：

- `VideoSandboxEnv` 固定 `SandboxClient(base_url="http://localhost:5000")`；`VideoAgentLoop` 收到的 `sandbox_base_url` 没有向下传递，单改 CLI 参数不会切换地址。
- `VideoSandboxEnv.execute()` 调用 `/start` 后没有设置 `started=True`，可能重复启动同一 sandbox。
- `VideoSandboxEnv.stop()` 捕获异常后仍返回可能未赋值的 `result`，停止失败会产生二次 `UnboundLocalError`。
- `VideoAgentLoop.start_sandbox()` 只写 `./rollouts/<id>.log`，第一个 executor cache miss 才真正调用 sandbox `/start`；父目录必须预先存在。
- `SandboxManager.load_video_into_sandbox()` 把源目录写死为 `path/to/train/EgoSchema/videos`，与当前 checkout 的 `train/EgoSchema/videos` 不一致。
- `AsyncSemanticStatefulExecutor` 的 root fork 分支把 fork id 传给 `task_name` 参数；先用 fake env probe 固化期望 contract，再修改。
- immutable cache 的 `intel_prefix_match`、`can_extend`、`remove`、`get_hot_nodes` 和 `check_env_marked` 仍未实现；不要把 README 中的 endpoint 列表当作实现保证。

### 10.4 交互式调试命令

server 可在本地调试环境中使用 `pdb`：

```bash
cd "$TVCACHE_ROOT/tvcache/server"
uv run python -m pdb tvcache_server.py --host 127.0.0.1 --port 18001
```

在 `put_endpoint()`、`prefix_match_endpoint()` 或 tree 的 `put()` 设置断点后，用第 4 节 payload 逐步检查 `history`、`values`、`tool_exec_times`、`start_idx` 和当前 node。训练侧先运行：

```bash
cd "$TVCACHE_ROOT"
python3 -m compileall -q train video-agent-tools/VideoAgent video-agent-tools/Video-LLaVA/videollava
rg -n 'AsyncTVCacheClient|VideoSandboxEnv|_execute_and_put|prefix_match|exact_match' \
  train tvcache/client tvcache/server
```

保留每次修改对应的 task name、server log 和 rollout log；验证完成后再进入下一处逻辑。

## 11. HTTP API 速查和实现差异

| 方法/路径 | 输入 | 成功响应或当前状态 |
| --- | --- | --- |
| `GET /get` | query `task_name`，重复 `tool_calls` | `200`，`found/env_id/value/tool_exec_time` |
| `PUT /put` | JSON `task_name/history/env_id/values/tool_exec_times/start_idx` | `200`，`success/removed_env_ids` |
| `POST /prefix_match` | JSON `task_name/tool_calls` | `200`，最长 prefix 的 `env_id/history` |
| `POST /mark_stateless` | JSON `task_name/history/env_id` | 由 tree node 状态决定 |
| `POST /should_fork` | JSON `task_name/history` | 先查看 immutable tree 实现和 traceback |
| `POST /unref` | JSON `env_id`，可选 `task_name` | `200`，`success=true` |
| `GET /get_all_envs` | query `task_name` | `200`，`env_ids` |
| `GET /visualize` | 可选 `path` | `200`，内存树或保存 JSON |
| `POST /store_test_result` | JSON `task_name/history/test_result` | HTTP 200 后再 GET 验证；async client 方法本身返回 `None` |
| `GET /get_test_result` | query `task_name`，重复 `tool_calls` | `found/test_result` |
| `POST /intel_prefix_match` | JSON `task_name/tool_calls` | 当前 immutable implementation 实测 `500 NotImplementedError` |
| `POST /can_extend` | JSON `task_name/history/suffix` | 当前 immutable implementation 实测 `500 NotImplementedError` |
| `DELETE /remove` | JSON `task_name/history` | 当前 immutable implementation 实测 `500 NotImplementedError` |
| `GET /get_hot_nodes`、`GET /check_env_marked` | query 参数 | 当前 immutable implementation 未实现 |

README 中的 `/lock` 和 `/unlock` 不在实际 Flask route 列表。以源码和以下命令为准：

```bash
cd "$TVCACHE_ROOT/tvcache/server"
uv run flask --app tvcache_server:app routes
```

## 12. 常见失败、根因和处理

| 表现 | 当前 checkout 已观察的根因 | 处理 |
| --- | --- | --- |
| 根目录运行 `uv run tvcache_server.py` 找不到文件 | 脚本位于 `tvcache/server` | 先切换到 server 目录 |
| `8000` 连接到其他进程 | 8000 已被占用且 sync/async 默认值不同 | smoke 用 18001；training 用 8001，并确认 async client |
| `/put` 返回 500，traceback 在 `values[idx - start_idx]` | 发送单值 `value` 而非数组 | 使用 `values` 和 `tool_exec_times`，长度与 history 对齐 |
| `/intel_prefix_match`、`/can_extend`、`/remove` 返回 500 | immutable implementation 为 `NotImplementedError` | 保存 traceback，不把 client 假结果当成功 |
| async client 返回假 miss | 多个方法捕获 `httpx.HTTPError` 并返回 `False`/空列表 | 直接重放 raw HTTP，结合 server log 判断 |
| sandbox 启动报 `torchvision::nms` | system torch/torchvision binary 不匹配，未使用 pinned Conda env | 激活 `cenv`，重新做 import probe |
| sandbox 找不到视频 | 模型/视频目录缺失，且 source path 硬编码 | 准备数据并做经过审查的 source-path 修复 |
| train 报 `No module named pydantic` | bare `train/.venv` 未同步 | `uv sync --locked`，安装 cookbook/client |
| train 缺 `chz`、`datasets` 或 `tinker_cookbook` | train manifest 只声明 tinker | 安装 `./tinker-cookbook` 后重做 import probe |
| rollout 报 `FileNotFoundError: ./rollouts/...` | cwd 错误或父目录不存在 | 从 `train/` 启动并先 `mkdir -p rollouts` |
| 重启 server 后命中消失 | cache 只在进程内存中 | 用 `/api/save` 或 auto-save 保存 tree，并记录返回路径 |

## 13. 证据文件和最终 checklist

配套证据报告：

```text
task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_http_smoke.md
task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_executor_smoke.md
task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_train_sandbox_preflight.md
task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_doc_command_guards.md
task_memory/task_2026-08-31_tvcache_e2e_reproduction/test_report_2026-08-31_final_verification.md
```

HTTP smoke 最新一轮真实值（task `final-verify-20260831-162642`，port `18003`）：`RESULT=PASS`、`initial_found=False`、`put_success=True`、`exact_value=manual_value_b`、`exact_tool_exec_time=0.25`、`prefix_history_len=2`、`cache_hits=1`、`prefix_hits=1`、`all_env_count=1`。完整 video/Tinker preflight 仍是失败状态：sandbox 退出码 `1`，错误 `RuntimeError: operator torchvision::nms does not exist`；train import 退出码 `1`，错误 `ModuleNotFoundError: No module named 'pydantic'`。

最终 clean-port 运行先使用 `http://127.0.0.1:18002` 和 task `final-clean-20260831-162108`，随后用 `http://127.0.0.1:18003` 和 task `final-verify-20260831-162642` 复核；两轮退出码均为 `0`，并在复核后释放监听端口。保存输出和 lock 修复的细节见配套 test reports 与 `task_memory/env_handbook.md`。

手动执行前逐项确认：

- [ ] `ROOT`、日志目录和运行目录使用绝对路径，临时日志写入 `/data/ycfeng/tmp`。
- [ ] Python、uv、Conda、FFmpeg、GPU 和 API keys 已检查。
- [ ] server/client/train lock 检查通过，cookbook/client editable package 已安装。
- [ ] TVCache 端口已明确：smoke=`18001`，training=`8001`。
- [ ] `GET /visualize` 返回 HTTP 200，HTTP smoke 输出 `RESULT=PASS`。
- [ ] Video-LLaVA 出现 `ready for connection!` 且 `tmp/vqa.sock` 存在。
- [ ] sandbox `/start`、`/stop` 返回 HTTP 200，模型和视频目录存在。
- [ ] 从 `train/` 启动，`rollouts/` 已创建，使用 `--config.<field>=<value>` 和绝对 `log_path`。
- [ ] `$RUN_DIR` 包含 `metrics.jsonl`、`config.json`、`code.diff`、`logs.log`、`checkpoints.jsonl`。
- [ ] rollout 日志与 `/visualize` 的 env id、prefix history 和 hit counters 相互吻合。
- [ ] 结束时只停止本次启动的进程，并确认对应端口和 VQA socket 已释放。
