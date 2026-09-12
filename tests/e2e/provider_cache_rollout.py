"""Run the fixed EgoSchema no-cache/TVCache comparison through local agent loops."""

import argparse
import asyncio
from contextlib import AsyncExitStack
from dataclasses import asdict
import json
import os
from pathlib import Path
import time
from uuid import uuid4

from agent_loop import VideoAgentLoop
from tvc_agent_loop import VideoAgentLoop as CachedVideoAgentLoop, VideoSandboxEnv
from tool_schema import Response
from utils.provider_chat_client import ProviderChatClient
from utils.rollout_execution import run_provider_agent_loops
from utils.tvcache_run_lifecycle import TVCacheRunLifecycle


class RecordedProviderClient(ProviderChatClient):
    """Persist each provider exchange before the local loop parses its content."""

    def __init__(self, output):
        super().__init__()
        self.output = output

    async def complete(self, messages, response_schema):
        content = await super().complete(messages, response_schema)
        with self.output.open("a") as stream:
            stream.write(json.dumps({"messages": messages, "content": content,
                                     "usage": self.usage_records[-1]}) + "\n")
        return content


async def run(args):
    manifest = json.loads(args.manifest.read_text())
    question = manifest["question"] + "\n\nOptions:\n" + "\n".join(
        f"{i}: {option}" for i, option in enumerate(manifest["options"])
    )
    template = (Path(__file__).resolve().parents[2] / "train/prompt.txt").read_text()
    prompt = template.replace("{QUESTION}", question).replace(
        "{response_schema}", json.dumps(Response.model_json_schema())
    )
    prompt += f'\nThe associated video name is {manifest["video_id"]}.mp4.'
    args.output.mkdir(parents=True, exist_ok=False)
    run_id = f"provider-{uuid4().hex}"
    records = []
    for variant, loop_class in [("no-cache", VideoAgentLoop), ("tvcache", CachedVideoAgentLoop)]:
        task_id = f'{run_id}-{variant}-{manifest["video_id"]}'
        async with AsyncExitStack() as stack:
            if variant == "tvcache":
                lifecycle = await stack.enter_async_context(TVCacheRunLifecycle(
                    VideoSandboxEnv, args.cache_url,
                    env_kwargs={"sandbox_base_url": args.sandbox_url},
                ))
                lifecycle.register_task(task_id)
            for index in range(2):
                kwargs = {"tvcache_base_url": args.cache_url} if variant == "tvcache" else {}
                loop = loop_class(
                    training_data_point={"question": prompt, "answer": manifest["correct_answer_index"]},
                    sampling_client=None, renderer=None, num_turns=args.turns,
                    sandbox_base_url=args.sandbox_url, task_id=task_id,
                    rollout_log_dir=Path(os.environ["TMPDIR"]) / run_id / "rollouts", **kwargs,
                )
                provider = RecordedProviderClient(
                    args.output / f"{variant}-{index}-provider.jsonl"
                )
                sandbox_id = f"{task_id}-{index}"
                started_at_unix = time.time()
                execution, = await run_provider_agent_loops(
                    [loop], [sandbox_id], provider_client=provider,
                )
                result = execution.output
                record = {
                    "variant": variant, "rollout_index": index,
                    "video_id": manifest["video_id"], "sandbox_id": sandbox_id,
                    "started_at_unix": started_at_unix,
                    "finished_at_unix": time.time(),
                    "model": provider.model, "elapsed_seconds": execution.elapsed_seconds,
                    **asdict(result), "provider_usage": provider.usage_records,
                    "provider_token_totals": {
                        key: sum(row[key] for row in provider.usage_records)
                        for key in ("prompt_tokens", "completion_tokens", "total_tokens")
                    },
                }
                (args.output / f"{variant}-{index}.json").write_text(json.dumps(record, indent=2) + "\n")
                print(json.dumps({k: record[k] for k in (
                    "variant", "rollout_index", "reward", "elapsed_seconds", "stats", "provider_token_totals",
                )}), flush=True)
                assert result.final_answer in range(len(manifest["options"])), record
                assert result.tool_calls, "A real rollout must execute local video tools"
                assert result.stats["total_calls"] == len(result.tool_calls), record
                records.append(record)
        if variant == "tvcache":
            pending = (
                len(lifecycle._pending_task_drains),
                len(lifecycle._pending_environment_stops),
                len(lifecycle._pending_drain_acks),
            )
            assert pending == (0, 0, 0), pending
    sandbox_dir = Path(os.environ["VIDEO_AGENT_SANDBOX_DIR"])
    remaining = [p.name for p in sandbox_dir.iterdir() if p.name.startswith(run_id)]
    summary = {
        "completed_rollouts": len(records), "no_cache_rollouts": 2, "tvcache_rollouts": 2,
        "remaining_run_sandboxes": remaining,
        "tvcache_exact_hits": sum(r["stats"]["exact_hits"] for r in records if r["variant"] == "tvcache"),
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    assert not remaining, summary
    assert summary["tvcache_exact_hits"] > 0, summary
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sandbox-url", default="http://127.0.0.1:5000")
    parser.add_argument("--cache-url", default="http://127.0.0.1:8001")
    parser.add_argument("--turns", type=int, default=10)
    asyncio.run(run(parser.parse_args()))
