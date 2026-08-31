## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Record direct AsyncSemanticStatefulExecutor smoke evidence |
| 2026-08-31 | Record fresh executor rerun on the isolated smoke server |

# Executor Smoke Test Report

## 1. Test Script Information

- Test type: inline direct probe using a fake `ToolCallEnv` and the repository's `AsyncSemanticStatefulExecutor`; no repository source file was changed.
- Exact command (run from `train/`; the server must already listen on port 18001):

```bash
mkdir -p rollouts
PYTHONPATH=../tvcache/client python - <<'PY'
import asyncio, json, uuid
from tvclient.tools.tool_call_env import ToolCall, ToolCallEnv
from tvclient.tools.async_semantic_stateful_executor import AsyncSemanticStatefulExecutor
from tvclient.utils.async_tvcache_client import AsyncTVCacheClient

events = []
class Call(ToolCall):
    def __init__(self, name='read', arg=''):
        self.name, self.arg = name, arg
    def to_dict(self):
        return {'name': self.name, 'arg': self.arg}
    @staticmethod
    def from_dict(data):
        return Call(data['name'], data.get('arg', ''))
    def will_mutate_state(self):
        return self.name == 'mutate'

class Env(ToolCallEnv):
    def __init__(self, env_id=None, task_name='default'):
        self.task_name = task_name
        self.env_id = env_id or f'{task_name}-env-{uuid.uuid4().hex[:8]}'
        self.state = 0
        events.append(('new', self.env_id, env_id is not None))
    async def execute(self, call, **kwargs):
        self.state += 1
        events.append(('execute', self.env_id, call.name, self.state))
        return f'{call.name}:{call.arg}:state={self.state}'
    async def fork(self, **kwargs):
        child = Env(task_name=self.task_name)
        child.state = self.state
        events.append(('fork', self.env_id, child.env_id, self.state))
        return child
    async def stop(self, **kwargs):
        events.append(('stop', self.env_id))
    async def get_state(self, **kwargs):
        return self.state
    def get_id(self, **kwargs):
        return self.env_id
    async def test(self):
        return 'ok'
    async def hash(self):
        return str(self.state)

class NullBank:
    def get_forked_env(self, task_name, parent_env_id):
        return None

async def main():
    task = 'executor-smoke-20260831-b'
    ex = AsyncSemanticStatefulExecutor(Env, Call, task)
    ex.client = AsyncTVCacheClient('http://127.0.0.1:18001')
    ex.set_fork_bank(NullBank())
    ex.set_rollout_id('executor-smoke-1')
    c1 = [Call('mutate', 'a')]
    r1 = await ex.execute(c1)
    r2 = await ex.execute(c1)
    await ex.close()
    ex2 = AsyncSemanticStatefulExecutor(Env, Call, task)
    ex2.client = AsyncTVCacheClient('http://127.0.0.1:18001')
    ex2.set_fork_bank(NullBank())
    ex2.set_rollout_id('executor-smoke-2')
    r3 = await ex2.execute([Call('mutate', 'a'), Call('read', 'b')])
    await ex2.close()
    cli = AsyncTVCacheClient('http://127.0.0.1:18001')
    envs = await cli.get_all_envs(task)
    await cli.close()
    print(json.dumps({'r1': r1, 'r2': r2, 'r3': r3, 'envs': envs, 'events': events}, sort_keys=True))

asyncio.run(main())
PY
```
- Server process: `uv run tvcache_server.py --host 127.0.0.1 --port 18001`, with access log `/data/ycfeng/tmp/tvcache_e2e_reproduction/server_18001.log`.
- Environment: system `Python 3.12.3`; `uv 0.11.14`; `httpx` and `requests` imported from the user Python 3.12 site packages; TVCache client source loaded from `tvcache/client`.
- Runtime files: `train/rollouts/executor-smoke-1.log` and `train/rollouts/executor-smoke-2.log`.

## 2. Validation Criteria

- Initial one-call history must take the cache-miss path, execute exactly one fake environment command, and issue a successful `PUT`.
- Repeating the same serialized history must return the stored value through `CACHE HIT, type 1` without another fake environment execution.
- A fresh executor with a cached prefix plus a read-only suffix must log prefix lookup, environment fork, `POST /unref`, suffix execution, and a second successful `PUT`.
- The server must return HTTP 200 for all expected `/get`, `/prefix_match`, `/put`, `/unref`, and `/get_all_envs` requests.
- Numeric observations to retain: fake execution durations were approximately `4.234025254845619e-06 s` for `mutate` and `4.12308145314455e-06 s` for `read`; cache-store logging took `0.010160426027141511 s` and `0.01841046300251037 s` in the two paths.

## 3. Test Results and Evidence

**PASS** — The direct probe exited with status `0` and printed:

```text
{"envs": ["executor-smoke-20260831-b-env-9a2cbd0c"],
 "r1": "mutate:a:state=1",
 "r2": "mutate:a:state=1",
 "r3": "read:b:state=1"}
```

Evidence in `train/rollouts/executor-smoke-1.log`:

- `CACHE MISS` -> `[TOOL EXEC]` -> `PUT` -> `Stored ... in cache`.
- Repeated history: `CACHE HIT, type 1` with saved tool call time `4.234025254845619e-06`.

Evidence in `train/rollouts/executor-smoke-2.log`:

- `Found cached env` for the one-call prefix.
- `Extended environment` after a fork, followed by suffix `[TOOL EXEC]`.
- The server access log records HTTP 200 for prefix lookup, `unref`, exact lookup, and `PUT`.

The first attempt from the repository root failed with:

```text
FileNotFoundError: .../TVCache/rollouts/executor-smoke-1.log
```

This failure confirms that `set_rollout_id()` uses a relative `./rollouts` path and that the training command must run from `train/` with that directory present.

## Interpretation

The smoke closes the client -> server protocol chain without requiring Tinker or the video backend. It does not validate model sampling, real VideoAgent execution, GPU kernels, or the production sandbox; those remain blocked by the environment prerequisites recorded in `issues.md` and `test_report_2026-08-31_train_sandbox_preflight.md`.

## 4. Fresh rerun evidence

- Server: `uv run tvcache_server.py --host 127.0.0.1 --port 18001`.
- Exact probe shape: the heredoc command in section 1, run from `train/` with `PYTHONPATH=../tvcache/client`, using task `executor-final-20260831-162642`, rollout IDs `executor-final-1` and `executor-final-2`, and client base URL `http://127.0.0.1:18001`.
- Captured output: `/data/ycfeng/tmp/tvcache_e2e_reproduction/final_executor_18001.log`.
- Result: exit `0`; `r1="mutate:a:state=1"`, `r2="mutate:a:state=1"`, `r3="read:b:state=1"`; `envs=["executor-final-20260831-162642-env-1dc31466"]`.
- Control-flow evidence: the log contains `CACHE MISS`, a successful `PUT`, `CACHE HIT, type 1`, `Found cached env`, `Extended environment`, `POST /unref` HTTP `200`, suffix `[TOOL EXEC]`, and a second successful `PUT`. The server session was interrupted after the probe and port `18001` was released.
