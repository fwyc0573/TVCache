## Modification History

| Date | Summary of Changes |
| --- | --- |
| 2026-09-15 | Recorded the provider, collection policy, execution environment, and smoke checks. |

# P04 provider smoke

Required user inputs: none. The existing authorized StepCode configuration passed a fresh HTTP 200 preflight. The selected tasks and image digests are already recorded in the W1 manifest.

| Setting | Value |
| --- | --- |
| Tasks | wasm-pipeline; polyglot-c-py; multi-source-data-merger; recover-accuracy-log |
| Rollouts | Four per task, each in a fresh image instance |
| Provider | `https://models-proxy.stepfun-inc.com` |
| Model | `deepseek-v4-flash` |
| Sampling | temperature 0.8, top_p 0.95, seed 20260915 + rollout index |
| Seed behavior | Request accepted; deterministic replay has not been established |
| Response | One JSON action per turn; json_object; tool_choice none |
| Limits | 32 tool steps; 8192 output tokens per request; 120 seconds per exec |
| GPU allocation | H200, step_main, local personal Python RJobBackend |
| Storage | `cloud_storage.md` defines the shared root and folders |

Execution order: staging -> {cloud image transfer, first complete rollout} -> remaining smoke rollouts -> aggregate checks. Transfer and the first rollout can run in parallel because each writes its own artifacts. The full smoke uses at most four concurrent task workers. This phase records tool timing; it makes no uncontended performance claim.

The collector copies the task image runtime into temporary worker storage. The actor runs as UID 65534 inside that filesystem with privilege elevation disabled. Only task inputs and system runtime are present; controller credentials, cloud mounts, source solutions, and hidden verifiers are absent. System packages are read-only. The actor can create a virtual environment under `/app` using the company mirror. Each task uses the same policy.

Tools run through the existing seven S0 plus one S1 implementation. Timing covers execution inside the tool process; manifests and provider requests have separate timing records. Full provider responses, tool observations, before/after workspace manifests, and final workspace archives are written under the cloud rollout directory. Temporary files and compiler/package caches stay on worker storage.

After the actor stops, the unchanged upstream `tests/test_outputs.py` and its fixtures are copied into the disposable filesystem. The collector runs the same pytest target as `run-tests.sh`, using CPU-prepared pytest 8.4.1 and the image's task dependencies. This avoids repeating the shell script's system/package installation. P03 already validated that shell setup and reference solution. Verifier status is separate from collection status; a task failure is a recorded outcome.

Smoke checks:

1. All 16 rollout completion records and traces are present and reload successfully.
2. More than half of the rollouts have at least four tool calls.
3. Real file mutations are observed.
4. Every task has at least two different tool-and-argument sequences across its four rollouts.
5. S0 and S1 both occur in model-selected actions.
6. Each rollout has a verifier result, log, and archived workspace.
7. Collection errors are shown explicitly and investigated before treating the dataset as ready.

No caching or reference-solution actions are inserted to meet these checks. A failed smoke check requires a documented policy or cohort adjustment before P05.
