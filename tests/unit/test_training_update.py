from __future__ import annotations

import asyncio
import ast
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "train"
    / "utils"
    / "training_update.py"
)
TRAIN_ROOT = MODULE_PATH.parents[1]


def _load_training_update_module() -> ModuleType:
    assert MODULE_PATH.is_file(), f"Missing training update module: {MODULE_PATH}"
    spec = importlib.util.spec_from_file_location(
        "training_update_under_test",
        MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RejectingTrainingClient:
    async def forward_backward_async(self, *args: Any, **kwargs: Any) -> None:
        raise AssertionError("empty batch reached forward_backward_async")

    async def optim_step_async(self, *args: Any, **kwargs: Any) -> None:
        raise AssertionError("empty batch reached optim_step_async")


@pytest.mark.asyncio
async def test_empty_training_batch_records_skip_without_optimizer_calls() -> None:
    module = _load_training_update_module()
    metrics: dict[str, float] = {}

    updated = await module.apply_training_update(
        training_client=RejectingTrainingClient(),
        training_datums=[],
        adam_params=object(),
        metrics=metrics,
    )

    assert updated is False
    assert metrics["optim/training_datums"] == 0.0
    assert metrics["optim/skipped_empty_batch"] == 1.0


@pytest.mark.asyncio
async def test_nonempty_training_batch_submits_one_optimizer_update() -> None:
    module = _load_training_update_module()

    class RecordingTrainingClient:
        def __init__(self):
            self.forward_batches: list[list[str]] = []
            self.optimizer_calls = 0

        async def forward_backward_async(
            self,
            training_datums: list[str],
            *,
            loss_fn: str,
        ):
            self.forward_batches.append(training_datums)
            assert loss_fn == "importance_sampling"
            return asyncio.sleep(0, result="forward-complete")

        async def optim_step_async(self, adam_params: object):
            self.optimizer_calls += 1
            return asyncio.sleep(0, result="optimizer-complete")

    client = RecordingTrainingClient()
    metrics: dict[str, float] = {}

    updated = await module.apply_training_update(
        training_client=client,
        training_datums=["datum-1"],
        adam_params=object(),
        metrics=metrics,
    )

    assert updated is True
    assert client.forward_batches == [["datum-1"]]
    assert client.optimizer_calls == 1
    assert metrics["optim/training_datums"] == 1.0
    assert metrics["optim/skipped_empty_batch"] == 0.0


@pytest.mark.parametrize(
    "driver_name",
    [
        "train_without_cache.py",
        "train_with_stateless_cache.py",
        "train_with_tvcache.py",
    ],
)
def test_training_driver_uses_guarded_update_boundary(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    direct_client_calls = [
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and node.attr in {"forward_backward_async", "optim_step_async"}
    ]
    guarded_update_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "apply_training_update"
    ]

    assert direct_client_calls == []
    assert len(guarded_update_calls) == 1
