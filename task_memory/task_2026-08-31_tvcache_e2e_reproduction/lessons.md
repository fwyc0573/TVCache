## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Initialize reusable lessons log |
| 2026-08-31 | Record verified reproduction and debugging lessons |

# Lessons

## Verified Lessons

- **Make the endpoint explicit at every process boundary.** This checkout has `8000` in the synchronous client/README path, `8001` in the CLI and async client, and `18001` was required for an isolated smoke because `8000` was already occupied. A fresh health request from each terminal prevents a successful request from being attributed to the wrong server.
- **Reproduce the wire protocol before diagnosing the client.** The immutable server requires `values` and `tool_exec_times` arrays aligned with `history`; the legacy singular `value` payload reaches `immutable_env_prefix_tree.py:229` and raises `TypeError`. Raw `curl` status plus the server traceback separates schema errors from async-client error swallowing.
- **Treat relative output paths as part of the runtime contract.** `set_rollout_id()` opens `./rollouts/<id>.log`; running the same executor probe from the repository root failed with `FileNotFoundError`, while `cd train && mkdir -p rollouts` passed. Record the working directory in every reproduction command.
- **Gate expensive E2E on dependency and asset probes.** `compileall` passed, but sandbox startup stopped at `torchvision::nms`, and the bare train environment stopped at missing `pydantic`; missing model/video directories and Tinker credentials are separate gates. A port listener alone cannot establish backend readiness.
- **Correlate cache counters with a fresh task and saved tree.** A timestamped task isolates `cache_hits`/`prefix_hits`; `/visualize` and `/api/save` provide the observable tree, while a server restart clears the in-memory cache. Keep the returned absolute save path as the run record.
