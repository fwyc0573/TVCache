## Modification History

| Date       | Summary of Changes                         |
| ---------- | ------------------------------------------ |
| 2026-09-13 | Recorded P02 local harness smoke evidence. |

# P02 Minimal Research Harness Verification

## Execution

Environment:

- Host Python: `Python 3.10.6` from `/usr/bin/python3`.
- Package requirement: `requires-python = ">=3.10"` in `research/rejoin/pyproject.toml`.
- No API key, network service, GPU, TVCache server, or video sandbox was used.
- Temporary artifacts were written under `/data/ycfeng/tmp`.

Commands:

```bash
python3 -m compileall -q research/rejoin/src research/rejoin/scripts
smoke_root=$(mktemp -d /data/ycfeng/tmp/rejoin-p02-final.XXXXXX)
python3 research/rejoin/scripts/collect.py \
  --workspace "$smoke_root/workspace" \
  --output "$smoke_root/trace.jsonl"
python3 research/rejoin/scripts/analyze.py \
  --trace "$smoke_root/trace.jsonl"
```

Observed temporary artifact root:

`/data/ycfeng/tmp/rejoin-p02-final.Zh6sUO`

## Criteria

The P02 acceptance requires one scripted local rollout to write JSONL, reload that JSONL, and record workspace state before and after each tool call. The harness must remain independent from API, TVCache, GPU, snapshot, and serving code.

## Evidence

PASS — `compileall` completed with exit status 0.

PASS — `collect.py` completed with exit status 0 and reported:

```json
{"events": 3, "run_id": "32c0f2c1cf7a40edb841d23c3e6d914c", "trace": "/data/ycfeng/tmp/rejoin-p02-final.Zh6sUO/trace.jsonl"}
```

PASS — `analyze.py` reloaded all three JSONL events and reported:

```json
{
  "changed_paths": ["src/input.txt"],
  "events": 3,
  "tools": ["write_file", "read_file", "list_dir"],
  "reload": "implicit by successful load_jsonl",
  "manifest_pairs": [
    ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "951c7bcc0e8f8587abc31e2214fe9a2a0d090f2ef77d4bcffcc5d59efed126d3"],
    ["951c7bcc0e8f8587abc31e2214fe9a2a0d090f2ef77d4bcffcc5d59efed126d3", "951c7bcc0e8f8587abc31e2214fe9a2a0d090f2ef77d4bcffcc5d59efed126d3"],
    ["951c7bcc0e8f8587abc31e2214fe9a2a0d090f2ef77d4bcffcc5d59efed126d3", "951c7bcc0e8f8587abc31e2214fe9a2a0d090f2ef77d4bcffcc5d59efed126d3"]
  ]
}
```

The first event changed `src/input.txt`; the two read-only events preserved the same before and after manifest digest. Each trace event contains normalized arguments, timing, result digest, and before/after workspace digest. This check establishes local harness behavior only; it does not establish API rollout behavior or any ReJoin opportunity class.
