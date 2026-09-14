## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the pinned Terminal-Bench source checkout and runtime build readiness. |
| 2026-09-15 | Added final StepBPS build records, registry manifest digests, and H200 verifier results for all ten selected tasks. |

# P03 Terminal-Bench Source Pin

## Source

- Repository: `https://github.com/harbor-framework/terminal-bench-1.git`
- Revision: `d28711d0da2675d0bb1d56de45ae5df6082438a3`
- Local checkout: `/data/ycfeng/tmp/terminal-bench-1-d28711d0da2675d0bb1d56de45ae5df6082438a3`
- Checkout state: detached HEAD at the exact revision, with no local edits.

The ten selected task directories each contain the pinned Dockerfile and `run-tests.sh`. All ten verifier shell scripts passed `bash -n` syntax validation.

## Runtime image status

The CPU master has no usable Docker-compatible runtime (`docker`, `podman`, `nerdctl`, `buildah`, or `/var/run/docker.sock`). Following the approved machine guidance, final images were built with the StepBPS path and verified on an H200 worker using quota group `step_main`, creator `i-fengyicheng`, and the pinned source checkout mounted through the local NFS path `100.96.128.193:/data/ycfeng/tmp`.

The `image_digest` values in the manifest are the private registry `Docker-Content-Digest` values for the final tags. The query snapshot is `/data/ycfeng/tmp/rejoin_p03_runtime_digests.json`; build metadata is retained in each `build_result_path` field in the manifest.

| Task | Final image tag | Registry digest | Build pipeline | Verifier job | Result |
|---|---|---|---|---|---|
| `wasm-pipeline` | `terminal-bench-wasm-pipeline-rejoin-v3-d28711d0da26-v3` | `sha256:a57a8486a3a2b0082dbf3dd98c96262c699253e587b9a95865c141ffd8a54faa` | `bf-df-swe-openhands-20260915-034528-718821973-dmmuns` | `exp-0915-042621-073453` | 3 passed |
| `polyglot-c-py` | `terminal-bench-polyglot-c-py-rejoin-v3-d28711d` | `sha256:8055ca32d2f789a904dc541dfd738b2c3ddc299eaec16e6560db18645abc30fc` | `bf-df-swe-openhands-20260915-030042-609698100-jfrxqg` | `exp-0915-042702-548718` | 1 passed |
| `extract-elf` | `terminal-bench-extract-elf-rejoin-v3-d28711d0da26` | `sha256:9695e51af59a1f1355825eb1707ee0ac9e33f14c9fd930300befda8029bb6e0f` | `bf-df-swe-openhands-20260915-030544-678812670-2r1qhk` | `exp-0915-042738-970432` | 2 passed |
| `multi-source-data-merger` | `terminal-bench-multi-source-data-merger-rejoin-v3-d28711d0da26-v2` | `sha256:11122a8a51c97ad466ba793c98d04d620db6b80ac6dfc667e3f3e28bdcd3dc40` | `bf-df-swe-openhands-20260915-040342-465235232-4g1de3` | `exp-0915-041241-577015` | 3 passed |
| `recover-accuracy-log` | `terminal-bench-recover-accuracy-log-rejoin-v3-d28711d0da26-v2` | `sha256:cff1441dc2937aa431d57a43fc343dd30e1e5efe9d30937156984424f78c9c97` | `bf-df-swe-openhands-20260915-040342-526323594-1lzo7p` | `exp-0915-041324-275817` | 3 passed |
| `log-summary-date-ranges` | `terminal-bench-log-summary-date-ranges-rejoin-v3-d28711d0da26` | `sha256:2c33f28e0da5e281dea2aecd246f9d5a7200225eb3d8d702a5eaa8677a94cf1f` | `bf-df-swe-openhands-20260915-031201-951461781-htwyfh` | `exp-0915-042820-109873` | 2 passed |
| `jq-data-processing` | `terminal-bench-jq-data-processing-rejoin-v3-d28711d0da26-v2` | `sha256:c35deeaf65d00112283ff15e37d6c767cf38c3ccebc3bd5cf591147806dd4881` | `bf-df-swe-openhands-20260915-040342-582468253-y9zfrp` | `exp-0915-041357-298827` | 14 passed |
| `pandas-etl` | `terminal-bench-pandas-etl-rejoin-v3-d28711d0da26-v2` | `sha256:52451b768b01905639f18fbac53d030ebf16419741522641e2cc797298bda94b` | `bf-df-swe-openhands-20260915-040342-644988992-zdxdqg` | `exp-0915-041425-871357` | 3 passed |
| `jsonl-aggregator` | `terminal-bench-jsonl-aggregator-rejoin-v3-d28711d0da26` | `sha256:03beb2d2cf4d7c566f5208782e04e5c3e0806be042a6936d4b1085d7a4257bad` | `bf-df-swe-openhands-20260915-031202-223804128-sqfygg` | `exp-0915-042901-387245` | 1 passed |
| `gcode-to-text` | `terminal-bench-gcode-to-text-rejoin-v3-d28711d0da26-v8` | `sha256:5cb7f47842c3f83e3299f720f1abe10a0f08a6076e90c6e7379a9621202d7e65` | `bf-df-swe-openhands-20260915-042319-366061160-rsbfxu` | `exp-0915-042450-505362` | 2 passed |

Each verifier record has `solution_exit_code=0`, `verifier_exit_code=0`, and worker status `succeeded`. Full logs and `nvidia-smi` captures are under `/data/ycfeng/tmp/rejoin-verifier-logs/`.

## Current decision

P03 source pinning, runtime preparation, verifier execution, and tool-surface implementation are complete. The four smoke tasks have verified images and may enter P04; provider selection and the real smoke rollout remain pending.
