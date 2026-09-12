## Modification History

| Date | Summary of Changes |
|------|--------------------|
| 2026-09-11 | Archived H800 real rollout deliverables and validation metrics. |
| 2026-08-14 | Created completion-summary placeholder. |

# Task Overview

This task measured a real inference-driven VideoAgent loop on a fixed EgoSchema video, comparing two no-cache rollouts with two TVCache rollouts. StepCode `deepseek-v4-flash` supplied inference; the local loop parsed JSON actions, executed VideoAgent tools in a local sandbox, and recorded cache/lifecycle metrics. RL optimizer updates and Tinker were excluded. Because H200 was disabled, the accepted run used an H800 `codesign` worker and the company StepCast vLLM image.

# Deliverables Inventory

- [test_report_2026-09-11_h800_real_rollouts.md](test_report_2026-09-11_h800_real_rollouts.md) — final execution, criteria, evidence, and metrics.
- [h800_reproduction.md](h800_reproduction.md) — durable H800 cache, loader, launch, monitoring, and acceptance recipe.
- [../../tests/e2e/run_real_video_rollouts_h800.sh](../../tests/e2e/run_real_video_rollouts_h800.sh) — reusable worker entrypoint with controlled secret loading and teardown.
- [../../tests/performance/complete_hf_cache_h800.py](../../tests/performance/complete_hf_cache_h800.py) — pinned HF snapshot assembly through the company mirror.
- [tvcache-real-rollout-h800-20260911-b-rollouts/summary.json](tvcache-real-rollout-h800-20260911-b-rollouts/summary.json) — four-rollout completion and residue summary.
- [tvcache-real-rollout-h800-20260911-b-rollouts/no-cache-0.json](tvcache-real-rollout-h800-20260911-b-rollouts/no-cache-0.json), [no-cache-1.json](tvcache-real-rollout-h800-20260911-b-rollouts/no-cache-1.json) — baseline rollout records.
- [tvcache-real-rollout-h800-20260911-b-rollouts/tvcache-0.json](tvcache-real-rollout-h800-20260911-b-rollouts/tvcache-0.json), [tvcache-1.json](tvcache-real-rollout-h800-20260911-b-rollouts/tvcache-1.json) — TVCache rollout records.
- [tvcache-real-rollout-h800-20260911-b-tool-smoke.json](tvcache-real-rollout-h800-20260911-b-tool-smoke.json) — sandbox start and local video-tool smoke.
- `/data/ycfeng/tmp/videollava-offline-probe-h800.json` — H800 four-bit offline loader evidence.
- `/data/ycfeng/tmp/h800_cache_probe_20260911.md` — pinned LanguageBind cache and local-loader evidence.
- `/data/ycfeng/tmp/tvcache-real-rollout-h800-20260911-b/gpu-memory.csv` — 1,016 samples per H800 GPU.

# Validation Status

PASS for the fixed one-video acceptance scope. All four rewards were `1.0` and all final answers were the correct option index `1`.

| Variant | Elapsed (s) | Calls / executions | Exact / prefix / misses | Forks / puts | Prompt / completion / total tokens |
|---------|------------:|-------------------:|------------------------:|-------------:|-----------------------------------:|
| no-cache-0 | 235.0006 | 26 / 26 | 0 / 0 / 26 | 0 / 0 | 31971 / 4419 / 36390 |
| no-cache-1 | 168.4909 | 15 / 15 | 0 / 0 / 15 | 0 / 0 | 14804 / 1990 / 16794 |
| tvcache-0 | 195.1357 | 20 / 20 | 0 / 19 / 1 | 2 / 20 | 20331 / 2122 / 22453 |
| tvcache-1 | 65.5046 | 18 / 13 | 5 / 13 / 0 | 1 / 13 | 21577 / 2258 / 23835 |

The H800 loader passed with Torch `2.0.1+cu118`, four-bit model loading, both vision towers, and 3,525,137,920 allocated bytes. Captioning, SegmentFeature, Tracking, and tool smoke passed. The worker reached `Succeeded`; lifecycle logs recorded stop/drain activity; `remaining_run_sandboxes=[]`. GPU memory peaked at 6,350 MiB on GPU 0 and 9,756 MiB on GPU 1 (81,559 MiB total each).

# Open Items/Future Extensions

- Repeat on additional EgoSchema videos or more seeds if broader statistical confidence is needed.
- Investigate the benign TVCache warning for withdrawing a task absent from `warmed_environments`.
- RL optimizer update and Tinker-backed training remain explicitly deferred.
