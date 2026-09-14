## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the ten-task W1 candidate cohort and four-task smoke subset. |
| 2026-09-15 | Resolved final image tags and registry digests, and linked each task to its build and verifier evidence. |

# ReJoin W1 Pilot Cohort Selection

- Source: `harbor-framework/terminal-bench-1`
- Pinned source revision: `d28711d0da2675d0bb1d56de45ae5df6082438a3`
- Target: ReJoin v3 P03/P04 observation-only filesystem workload
- Selected: 10 primary tasks; Excluded examples: 4

## Image-digest status

At selection time the candidate manifest left `image_digest` as `null`. On 2026-09-15, all ten images were built through StepBPS because the CPU master has no usable Docker runtime. The manifest now records the private registry `Docker-Content-Digest` for each final image tag, together with the build pipeline, Dockerfile fingerprint, and H200 verifier evidence. The authoritative digest query snapshot is `/data/ycfeng/tmp/rejoin_p03_runtime_digests.json`.

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

## Resolved runtime metadata

| Task | Final image tag | `image_digest` | Verifier result |
|---|---|---|---|
| `wasm-pipeline` | `terminal-bench-wasm-pipeline-rejoin-v3-d28711d0da26-v3` | `sha256:a57a8486a3a2b0082dbf3dd98c96262c699253e587b9a95865c141ffd8a54faa` | PASS (3) |
| `polyglot-c-py` | `terminal-bench-polyglot-c-py-rejoin-v3-d28711d` | `sha256:8055ca32d2f789a904dc541dfd738b2c3ddc299eaec16e6560db18645abc30fc` | PASS (1) |
| `extract-elf` | `terminal-bench-extract-elf-rejoin-v3-d28711d0da26` | `sha256:9695e51af59a1f1355825eb1707ee0ac9e33f14c9fd930300befda8029bb6e0f` | PASS (2) |
| `multi-source-data-merger` | `terminal-bench-multi-source-data-merger-rejoin-v3-d28711d0da26-v2` | `sha256:11122a8a51c97ad466ba793c98d04d620db6b80ac6dfc667e3f3e28bdcd3dc40` | PASS (3) |
| `recover-accuracy-log` | `terminal-bench-recover-accuracy-log-rejoin-v3-d28711d0da26-v2` | `sha256:cff1441dc2937aa431d57a43fc343dd30e1e5efe9d30937156984424f78c9c97` | PASS (3) |
| `log-summary-date-ranges` | `terminal-bench-log-summary-date-ranges-rejoin-v3-d28711d0da26` | `sha256:2c33f28e0da5e281dea2aecd246f9d5a7200225eb3d8d702a5eaa8677a94cf1f` | PASS (2) |
| `jq-data-processing` | `terminal-bench-jq-data-processing-rejoin-v3-d28711d0da26-v2` | `sha256:c35deeaf65d00112283ff15e37d6c767cf38c3ccebc3bd5cf591147806dd4881` | PASS (14) |
| `pandas-etl` | `terminal-bench-pandas-etl-rejoin-v3-d28711d0da26-v2` | `sha256:52451b768b01905639f18fbac53d030ebf16419741522641e2cc797298bda94b` | PASS (3) |
| `jsonl-aggregator` | `terminal-bench-jsonl-aggregator-rejoin-v3-d28711d0da26` | `sha256:03beb2d2cf4d7c566f5208782e04e5c3e0806be042a6936d4b1085d7a4257bad` | PASS (1) |
| `gcode-to-text` | `terminal-bench-gcode-to-text-rejoin-v3-d28711d0da26-v8` | `sha256:5cb7f47842c3f83e3299f720f1abe10a0f08a6076e90c6e7379a9621202d7e65` | PASS (2) |

All ten rows also carry `solution_exit_code=0`, `verifier_exit_code=0`, worker status `succeeded`, and evidence paths in `rejoin_w1_candidate_manifest.jsonl`.

## Metadata contract for Codex

For every selected task, P03 should copy the JSONL entry into the repository cohort file and then fill only the runtime-resolved fields:

```text
image_digest
build_timestamp
optional base_image_repo_digest
```

The runtime fields are now filled. Do not rewrite `source_revision`, instruction, task root, stratum, or include reason after observing rollout/cache results.
