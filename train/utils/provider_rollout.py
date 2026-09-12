from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping, Sequence

from tool_schema import Response


@dataclass(frozen=True)
class ProviderRolloutResult:
    final_answer: int | None
    reward: float
    messages: list[dict[str, Any]]
    tool_calls: list[dict[str, str]]
    stats: dict[str, int]


async def run_provider_turns(
    *,
    messages: list[dict[str, Any]],
    num_turns: int,
    complete: Callable[
        [Sequence[Mapping[str, Any]], Mapping[str, Any]], Awaitable[str]
    ],
    execute: Callable[[str, str], Awaitable[Any]],
    answer: int,
    stats: dict[str, int],
) -> ProviderRolloutResult:
    tool_calls: list[dict[str, str]] = []
    final_answer: int | None = None

    for turn_index in range(num_turns):
        content = await complete(messages, Response.model_json_schema())
        response = Response.model_validate_json(content)
        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": content,
        }
        messages.append(assistant_message)

        if response.final_answer is not None:
            final_answer = response.final_answer
            break

        for action in response.actions:
            tool_name = action.tool
            tool_input = action.inputs
            tool_calls.append({"tool": tool_name, "inputs": tool_input})
            result = await execute(tool_name, tool_input)
            stats["total_calls"] += 1
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Local tool result for {tool_name}: {result}"
                    ),
                }
            )

    reward = -2.0 if final_answer is None else float(final_answer == answer)
    return ProviderRolloutResult(
        final_answer=final_answer,
        reward=reward,
        messages=messages,
        tool_calls=tool_calls,
        stats=dict(stats),
    )
