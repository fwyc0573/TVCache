## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-09 | Preserved provider usage and verified strict accounting with a live StepCode response. |

# Provider Usage Verification

## Test Script Information

- Script: `/data/ycfeng/stepfun-performance-optimization/new-topic-research/related-work/TVCache/.worktrees/tvcache-rl-reproduction/tests/unit/test_provider_chat_client.py`.
- Unit environment: `tvcache/client/.venv`, Python 3.10.20; no conda environment.
- Live environment: `/data/ycfeng/tmp/tvcache-train-py312`, Python 3.12.3; no conda environment.
- Provider: `deepseek-v4-flash`, `https://models-proxy.stepfun-inc.com/v1/chat/completions`.
- Live evidence: `/data/ycfeng/tmp/tvcache-provider-usage-live-20260909.json`.

From the worktree:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  tvcache/client/.venv/bin/pytest -q -p no:cacheprovider \
  tests/unit/test_provider_chat_client.py
```

Reproduce the live request after loading the company proxy and synchronizing uppercase/lowercase proxy variables:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/train" \
  /data/ycfeng/tmp/tvcache-train-py312/bin/python - <<'PYCODE'
import asyncio, json
from pathlib import Path
from utils.provider_chat_client import ProviderChatClient
async def main():
    config = json.loads((Path.home() / '.stepcode/config.json').read_text())
    client = ProviderChatClient(api_key=config['apiKey'])
    content = await client.complete(
        [{'role': 'user', 'content': 'Return this JSON object: {"ok":true}'}],
        {'type': 'object'},
    )
    assert json.loads(content) == {'ok': True}
    print(json.dumps({'response': json.loads(content), 'usage_records': client.usage_records}))
asyncio.run(main())
PYCODE
```

## Validation Criteria

- Keep `complete()` returning content as a string and preserve the existing request payload.
- Retain the provider's full usage object, including optional token details.
- Require prompt/completion/total counts to be nonnegative integers; reject missing fields, booleans, negative values, and strings.
- Keep credential values out of recorded artifacts.

## Test Results and Evidence

| Check | Observed | Expected | Result |
| --- | --- | --- | --- |
| Unit checks | 8 passed in 0.07 s | All selected checks pass | PASS |
| Controlled usage | prompt 11, completion 7, total 18, reasoning 3 | Exact response values retained | PASS |
| Live JSON | `{"ok": true}` | `{"ok": true}` | PASS |
| Live usage | prompt 113, completion 49, total 162 | Nonnegative integer counts retained | PASS |
| Live token sum | 113 + 49 = 162 | Reported total 162; difference 0 | PASS |
| Live details | cached prompt tokens 0; reasoning tokens 43 | Preserve provider detail fields | PASS |

The initial selected regression run had 6 failures before the fix. Missing/malformed usage now raises explicitly. This verifies provider accounting; video tool execution and the four real rollout runs remain pending.
