## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-15 | Recorded provider budget probe and v19 preparation checks. |

# P04 provider budget probe

## Execution

- Probe script: `/data/ycfeng/tmp/rejoin-p04-control/provider_copy_probe.py`
- Command: `set +x; proxy_script=$(curl --fail --silent --show-error --max-time 15 http://deploy.i.shaipower.com/httpproxy); eval "$proxy_script"; export HTTP_PROXY="$http_proxy" HTTPS_PROXY="$https_proxy" ALL_PROXY="$all_proxy" NO_PROXY="$no_proxy"; /data/ycfeng/tmp/stepmind-env/bin/python /data/ycfeng/tmp/rejoin-p04-control/provider_copy_probe.py`
- Endpoint/model: `https://models-proxy.stepfun-inc.com`, `deepseek-v4-flash`
- Request mode: native `write_file`, `thinking={"type":"disabled"}`, `parallel_tool_calls=false`, temperature 0, top_p 1.
- Config validation: `python3 tests/e2e/run_rejoin_p04.py --stage /data/ycfeng/tmp/rejoin-p04-control --run-id p04-20260915-v19 --prepare-only`
- Code checks: `python3 -m py_compile tests/e2e/run_rejoin_p04.py research/rejoin/scripts/collect_p04.py`; `PYTHONPATH=/data/ycfeng/tmp/rejoin-p04-control/public/verifier_packages python3 -m pytest research/rejoin/tests/test_tools.py -q`.

## Criteria

- A provider response must have a native tool call whose `arguments` value parses as JSON.
- The requested content lengths were 3,500, 5,500, and 7,500 characters. Each length was tested with requested output budgets 2,048, 4,096, and 8,192.
- All 16 v19 configs must contain `max_tokens=4096` and policy `p04-v19-native-tools-4k-cleanup`.

## Evidence

| Requested content | Budget | Result |
| ---: | ---: | --- |
| 3,500 | 2,048 | PASS; parseable native call, 3,338 returned content characters |
| 3,500 | 4,096 | PASS; parseable native call, 3,338 returned content characters |
| 3,500 | 8,192 | PASS; parseable native call, 3,338 returned content characters |
| 5,500 | 2,048 | PASS; parseable native call, 5,228 returned content characters |
| 5,500 | 4,096 | PASS; parseable native call, 5,228 returned content characters |
| 5,500 | 8,192 | PASS; parseable native call, 5,228 returned content characters |
| 7,500 | 2,048 | PASS; parseable native call, 7,118 returned content characters |
| 7,500 | 4,096 | PASS; parseable native call, 7,118 returned content characters |
| 7,500 | 8,192 | PASS; parseable native call, 7,118 returned content characters |

The 1024-token v18 failures are separate evidence: their raw arguments ended mid-string and were rejected by `json.loads`. The probe demonstrates provider parsing capacity for representative long calls; it does not prove that every task trajectory will finish within 4096 tokens. The new smoke run is the required end-to-end check.

The code checks passed: Python compilation succeeded, the eight-tool test file reported `3 passed`, and v19 preparation reported `P04_PREPARED 16` with every config field verified.
