"""Check provider result accounting with controlled local execution callbacks."""

import asyncio
import json
from types import SimpleNamespace

from agent_loop import VideoAgentLoop
from tvc_agent_loop import VideoAgentLoop as CachedVideoAgentLoop


async def verify(loop_class, cached):
    loop = loop_class(
        training_data_point={"question": "accounting probe", "answer": 1},
        sampling_client=None,
        renderer=None,
        num_turns=2,
    )
    responses = iter([
        '{"thought":"inspect","actions":[{"tool":"preprocess","inputs":""}],"final_answer":null}',
        '{"thought":"answer","actions":[],"final_answer":1}',
    ])

    async def complete(messages, schema):
        return next(responses)

    async def execute(*args):
        if cached:
            loop.executor.total_calls += 1
            loop.executor.total_executions += 1
            loop.executor.cache_misses += 1
            loop.executor.environment_forks += 1
            loop.fork_generator.environment_forks += 2
            return "preprocessed"
        return {"result": "preprocessed"}

    if cached:
        loop.executor.execute = execute
    else:
        loop.sandbox_client.execute = execute
    try:
        result = await loop.run_provider(SimpleNamespace(complete=complete))
        observed = {
            "variant": "tvcache" if cached else "no-cache",
            "result_reward": result.reward,
            "loop_reward": loop.get_reward(),
            "stats": result.stats,
        }
        print(json.dumps(observed, sort_keys=True), flush=True)
        assert result.reward == loop.get_reward() == 1.0, observed
        assert result.stats == loop.get_stats(), observed
        assert result.stats["total_calls"] == 1, observed
        assert result.stats["tool_executions"] == 1, observed
        assert result.stats["cache_misses"] == 1, observed
        assert result.stats["environment_forks"] == (3 if cached else 0), observed
    finally:
        if cached:
            await loop._close_owned_resources()


async def main():
    failures = []
    for loop_class, cached in [(VideoAgentLoop, False), (CachedVideoAgentLoop, True)]:
        try:
            await verify(loop_class, cached)
        except AssertionError as error:
            failures.append(str(error))
    if failures:
        raise AssertionError("; ".join(failures))
    print("PASS provider accounting variants=2")


if __name__ == "__main__":
    asyncio.run(main())
