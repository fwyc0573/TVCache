## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-08 | Updated the live provider contract to `json_object` plus local schema validation and standard OpenAI tool-call message identifiers after H200 protocol verification. |
| 2026-08-17 | Added the approved DeepSeek text and local LaViLa/Video-LLaVA visual provider design. |
| 2026-08-16 | Added production context-exit convergence for uncertain teardown transport responses. |
| 2026-08-16 | Added the retry-safe teardown transaction required by the v7 architecture review. |
| 2026-08-14 | Created the core reproduction design. |

# Core Design

## Confirmed First-Run Architecture

StepCode Codex exposes `deepseek-v4-flash` through its provider API. The specified StepCast vLLM image supplies the OpenAI-compatible adapter/runtime layer and does not load local model weights. The H200 worker connects directly to the provider through value-free environment configuration.

The provider returns a JSON object through the provider-supported `response_format={"type":"json_object"}` mode. The local adapter validates it against the repository's `Response` schema with `Response.model_validate_json()`. The local agent loop emits standard assistant `tool_calls` and matching `role=tool` messages with `tool_call_id` values, executes every action locally, and sends the results into the next request. `AsyncSemanticStatefulExecutor` remains the TVCache boundary; `VideoSandboxEnv` and the VideoAgent sandbox remain the tool backend. A no-cache loop uses the same model, messages, sandbox, and metrics path with cache interception disabled.

The first acceptance case is one fixed EgoSchema question and video, with two no-cache rollouts and two TVCache rollouts. Tinker datums, logprobs, forward/backward calls, optimizer steps, and online RL updates are excluded.

## Runtime Topology

- Tinker performs remote policy sampling and training.
- The local two-H800 worker runs the training driver, TVCache server, VideoAgent sandbox, and Video-LLaVA.
- GPU 0 is assigned to VideoAgent preprocessing and tool models.
- GPU 1 is assigned to Video-LLaVA.
- The sandbox listens on `127.0.0.1:5000`.
- TVCache runs as one Flask process on `127.0.0.1:8001`.
- VideoAgent and Video-LLaVA communicate through a Unix socket in `/data/ycfeng/tvcache_runtime/...`.

## Configuration Flow

Training configuration owns the TVCache URL, sandbox URL, model, renderer, dataset slice, and log directory. The executor receives the TVCache URL and environment-construction arguments. Every directly created, restored, or pre-warmed environment uses the same sandbox configuration.

## Model Provider Flow

- Object-memory ReAct reasoning uses `deepseek-v4-flash` through DeepSeek's OpenAI-compatible endpoint at `https://api.deepseek.com`.
- `DEEPSEEK_API_KEY` is required before any GPU preprocessing component is initialized.
- DeepSeek thinking is explicitly disabled for the ReAct call with `extra_body={"thinking": {"type": "disabled"}}`; there is no text-provider fallback.
- Batch and on-demand captions both use the existing local LaViLa model. On-demand caption generation returns local caption data plus API token counts `0/0`.
- Visual question answering accepts only the local Video-LLaVA path. GPT-4V selection and OpenAI-key propagation are removed from the active `ToolKit` interface.
- Missing credentials, unsupported VQA selection, unreadable frames, and malformed model responses fail immediately.

## Cache Validation Model

The deterministic CPU environment proves exact-hit and partial-prefix semantics independently of model sampling. The real RL smoke then proves that the same integration operates with Tinker and GPU-backed video tools.

## Error Model

Infrastructure failures raise immediately. Invalid configuration, missing files, unavailable services, malformed HTTP responses, and environment-lifecycle inconsistencies are errors rather than cache misses or synthetic tool values.

## Retry-Safe Teardown

- Each task drain uses one stable `drain_id`.
- The cache server atomically detaches the task tree once, retains the detached environment IDs under that `drain_id`, and returns the same IDs when the same drain is retried.
- A different drain ID cannot replace an unacknowledged drain for the same task.
- Each sandbox stop uses one stable operation ID. The sandbox server records completed stops so a lost success response can be retried without treating the already removed sandbox as an unknown deletion.
- The run lifecycle retains the drain, outstanding stop operations, and ACK state. It sends the drain ACK only after every sandbox stop is confirmed.
- Drain and stop completion records are removed only at their explicit ownership-transfer boundary; transport failure alone never discards ownership.
- Production context exit keeps the same lifecycle instance alive and retries an uncertain `httpx.TransportError` until all pending drain, stop, and ACK state converges.
- HTTP status, response-schema, validation, and other semantic errors remain fail-fast. Transport retry has no finite exhaustion while transaction state exists only in process memory.

## Observability

Each rollout records numeric cache calls, exact hits, prefix hits, misses, backend tool executions, cache puts, environment forks, rewards, tokens, and elapsed time. Test reports also record GPU memory and residual sandbox state.
