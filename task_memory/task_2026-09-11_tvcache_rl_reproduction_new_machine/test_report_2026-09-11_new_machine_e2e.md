## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-11 | Recorded successful H800 end-to-end reproduction on the new machine. |

# Test Report

## Execution

- Host: `kun-workspace-vgen2`; GPU worker: H800, 2 GPUs, RJob `exp-0911-180851-903367`, terminal phase `Succeeded`.
- Submission: `/data/ycfeng/tmp/stepmind-env/bin/python tests/e2e/submit_tvcache_reproduction_rjob.py` with `STEPMIND_BACKEND=rjob`, personal `i-fengyicheng` credentials, and `codesign` quota.
- Worker command: `tests/e2e/run_real_video_rollouts_h800.sh`.
- Provider: StepCode `deepseek-v4-flash`; model cache and VideoAgent assets were mounted from local `/data/ycfeng`.

## Criteria and Evidence

- Tool smoke: PASS. All load, preprocess, caption retrieval, segment localization, VQA, and stop calls returned HTTP 200.
- Rollout completion: PASS. `summary.json` reports `completed_rollouts=4`, `no_cache_rollouts=2`, `tvcache_rollouts=2`, `remaining_run_sandboxes=[]`, and `tvcache_exact_hits=6`.
- Per-rollout correctness: PASS. `no-cache-0`, `no-cache-1`, `tvcache-0`, and `tvcache-1` each have `reward=1.0`, `final_answer=1`, non-empty tool calls, and non-empty provider token totals.
- Cache behavior: PASS. no-cache variants have 18 and 13 misses; TVCache variants have respectively 10 prefix hits plus 1 miss, and 6 exact hits plus 10 prefix hits.
- Retained artifacts: PASS. Tool smoke JSON, four rollout JSON files, provider JSONL traces, `summary.json`, `gpu-memory.csv`, and VQA/sandbox/cache/rollout logs are present under the task and `/data/ycfeng/tmp/exp-0911-180851-903367/`.

Observed elapsed times were 278.92s, 210.66s, 159.24s, and 45.62s for no-cache-0, no-cache-1, tvcache-0, and tvcache-1 respectively. These are runtime observations for this worker allocation and are not acceptance thresholds.
