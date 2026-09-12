from __future__ import annotations

from typing import Any, Sequence


async def apply_training_update(
    training_client: Any,
    training_datums: Sequence[Any],
    adam_params: Any,
    metrics: dict[str, float],
) -> bool:
    metrics["optim/training_datums"] = float(len(training_datums))

    if not training_datums:
        metrics["optim/skipped_empty_batch"] = 1.0
        return False

    metrics["optim/skipped_empty_batch"] = 0.0
    forward_backward_future = await training_client.forward_backward_async(
        training_datums,
        loss_fn="importance_sampling",
    )
    optimizer_future = await training_client.optim_step_async(adam_params)
    await forward_backward_future
    await optimizer_future
    return True
