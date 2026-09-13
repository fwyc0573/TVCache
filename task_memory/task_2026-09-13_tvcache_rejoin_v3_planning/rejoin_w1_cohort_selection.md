## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the ten-task W1 candidate cohort and four-task smoke subset. |

# ReJoin W1 Pilot Cohort Selection

- Source: `harbor-framework/terminal-bench-1`
- Pinned source revision: `d28711d0da2675d0bb1d56de45ae5df6082438a3`
- Target: ReJoin v3 P03/P04 observation-only filesystem workload
- Selected: 10 primary tasks; Excluded examples: 4

## Important image-digest note

`image_digest` is intentionally left `null` in the candidate manifest. Terminal-Bench task compose files build task-local images; a truthful OCI/local content digest does not exist until the pinned build context is built. Do **not** substitute the Dockerfile Git blob SHA or the base-image tag for the runtime image digest. Before P04, build each selected task at the pinned revision and fill `image_digest` with `docker image inspect ... --format '{{.Id}}'`. The manifest includes an exact resolution command per task.

## Inclusion criteria

Selected tasks keep semantically important persistent state under `/app`, have deterministic Terminal-Bench pytest verifiers, avoid long-lived service state, and cover compilation/code generation, binary/artifact analysis, multi-file ETL/log processing, and structured-data transformation. Task success is not required for opportunity analysis, but the cohort should naturally generate multi-turn read/edit/exec/verify trajectories.

## Selected tasks

| Task | Stratum | Why it fits |
|---|---|---|
| `wasm-pipeline` | `build_test_pipeline` | Self-contained /app artifact task with real compile/runtime tooling, deterministic local inputs, no persistent service, and a pytest verifier. Good build/test-style candidate with likely repeated exec work. |
| `polyglot-c-py` | `compile_test_codegen` | Workspace-local code synthesis with repeated edit/compile/run/test cycles likely to occur naturally. No daemon or external mutable state. |
| `extract-elf` | `binary_analysis_codegen` | Filesystem-local binary-analysis/code-generation task with iterative inspect/edit/run behavior and deterministic verifier. |
| `multi-source-data-merger` | `multi_source_etl` | Multi-input/multi-output deterministic ETL with several file reads and artifact writes. Strong filesystem locality and no service state. |
| `recover-accuracy-log` | `multi_file_log_recovery` | Multi-file log recovery with multiple deterministic outputs. Encourages repeated reads, transforms, writes, and verification while remaining entirely workspace-local. |
| `log-summary-date-ranges` | `multi_file_log_aggregation` | Multi-file read/aggregation task with deterministic local data and explicit output. Useful lower-complexity data-processing stratum. |
| `jq-data-processing` | `structured_data_transform` | Deterministic structured-data transformation with three coupled output artifacts. Fully workspace-local and easy enough for reliable multi-rollout collection. |
| `pandas-etl` | `structured_data_transform` | Simple deterministic ETL task that provides a low-complexity control within W1 while still producing real read/modify/write trajectories. |
| `jsonl-aggregator` | `multi_file_aggregation` | Multi-file aggregation with deterministic output; good for repeated scan/parse/write behavior without hidden process state. |
| `gcode-to-text` | `artifact_analysis` | Filesystem-only artifact-analysis task with no service or network state. Adds reverse-engineering diversity to the pilot. |

## Recommended 4-task smoke subset

Use these first because they span different behavior without starting from the hardest tasks:

1. `wasm-pipeline` — build/run pipeline
2. `polyglot-c-py` — iterative edit/compile/run
3. `multi-source-data-merger` — multi-input/multi-output ETL
4. `recover-accuracy-log` — multi-file log recovery

If these produce too few mutations/tool calls, replace the simplest data task in the full pilot with a harder coding task rather than changing the tool-class definitions.

## Explicit exclusions

| Task | Reason |
|---|---|
| `kv-store-grpc` | Requires installing grpc packages, starting a server on port 5328, and keeping a background process alive. Persistent process/network state is outside the v3 workspace-manifest model. |
| `broken-python` | Core task repairs a system-wide Python/pip installation, so important state mutation occurs outside /app and would not be captured by the W1 workspace manifest. |
| `fix-git` | Task correctness depends on Git history/refs under .git. v3 explicitly proposes ignoring .git in the workspace manifest, so including this task would make state classification unsound. |
| `add-benchmark-lm-eval-harness` | Requires cloning two external repositories, constructing a 93k-row dataset, building/installing a library system-wide, and long external/network-heavy execution. Poor fit for the first observation-only pilot. |

## Metadata contract for Codex

For every selected task, P03 should copy the JSONL entry into the repository cohort file and then fill only the runtime-resolved fields:

```text
image_digest
build_timestamp
optional base_image_repo_digest
```

Do not rewrite `source_revision`, instruction, task root, stratum, or include reason after observing rollout/cache results.
