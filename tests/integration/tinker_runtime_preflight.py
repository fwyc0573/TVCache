from __future__ import annotations

import asyncio
import importlib
import inspect
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

import tinker
from tinker_cookbook.completers import TokensWithLogprobs
from tinker_cookbook.rl.data_processing import trajectory_to_data
from tinker_cookbook.rl.types import Trajectory, Transition


REPO_ROOT = Path(__file__).resolve().parents[2]
TRAIN_ROOT = REPO_ROOT / "train"
DRIVER_MODULES = [
    "train_without_cache",
    "train_with_stateless_cache",
    "train_with_tvcache",
]


def _assert_close_list(
    observed: list[float],
    expected: list[float],
    *,
    tolerance: float = 1e-6,
) -> None:
    assert len(observed) == len(expected)
    for actual, target in zip(observed, expected):
        assert abs(actual - target) <= tolerance


def _validate_converter() -> dict[str, Any]:
    trajectory = Trajectory(
        transitions=[
            Transition(
                ob=tinker.ModelInput.from_ints(tokens=[10, 11]),
                ac=TokensWithLogprobs(
                    tokens=[20],
                    maybe_logprobs=[-0.2],
                ),
                reward=0.0,
                episode_done=False,
            ),
            Transition(
                ob=tinker.ModelInput.from_ints(tokens=[90, 91]),
                ac=TokensWithLogprobs(
                    tokens=[30],
                    maybe_logprobs=[-0.3],
                ),
                reward=0.0,
                episode_done=True,
            ),
        ],
        final_ob=tinker.ModelInput.from_ints(tokens=[90, 91, 30]),
    )

    datums = trajectory_to_data(trajectory, traj_advantage=1.5)
    assert len(datums) == 2

    observed_inputs = [datum.model_input.to_ints() for datum in datums]
    observed_targets = [
        datum.loss_fn_inputs["target_tokens"].data
        for datum in datums
    ]
    observed_logprobs = [
        datum.loss_fn_inputs["logprobs"].data
        for datum in datums
    ]
    observed_advantages = [
        datum.loss_fn_inputs["advantages"].data
        for datum in datums
    ]
    observed_masks = [
        datum.loss_fn_inputs["mask"].data
        for datum in datums
    ]

    assert observed_inputs == [[10, 11], [90, 91]]
    assert observed_targets == [[11, 20], [91, 30]]
    _assert_close_list(observed_logprobs[0], [0.0, -0.2])
    _assert_close_list(observed_logprobs[1], [0.0, -0.3])
    _assert_close_list(observed_advantages[0], [0.0, 1.5])
    _assert_close_list(observed_advantages[1], [0.0, 1.5])
    assert observed_masks == [[0.0, 1.0], [0.0, 1.0]]

    return {
        "datum_count": len(datums),
        "input_tokens": observed_inputs,
        "target_tokens": observed_targets,
        "sampled_token_count": int(
            sum(sum(mask) for mask in observed_masks)
        ),
    }


def _validate_entrypoints() -> list[dict[str, Any]]:
    if str(TRAIN_ROOT) not in sys.path:
        sys.path.insert(0, str(TRAIN_ROOT))

    child_environment = os.environ.copy()
    child_environment.pop("TINKER_API_KEY", None)
    child_environment.pop("OPENAI_API_KEY", None)
    child_environment["PYTHONDONTWRITEBYTECODE"] = "1"

    results: list[dict[str, Any]] = []
    for module_name in DRIVER_MODULES:
        module = importlib.import_module(module_name)
        assert module.asyncio is asyncio
        assert inspect.iscoroutinefunction(module.main)

        driver_path = TRAIN_ROOT / f"{module_name}.py"
        completed = subprocess.run(
            [sys.executable, str(driver_path), "--help"],
            cwd=TRAIN_ROOT,
            env=child_environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        # chz 0.4.0 reports EntrypointHelpException with exit status 1.
        assert completed.returncode == 1, (
            f"{module_name} --help returned unexpected exit "
            f"{completed.returncode}: stdout={completed.stdout!r}, "
            f"stderr={completed.stderr!r}"
        )
        assert completed.stderr == ""
        help_output = completed.stdout
        assert "model_name" in help_output
        assert "renderer_name" in help_output

        results.append(
            {
                "module": module_name,
                "imported": True,
                "main_is_async": True,
                "help_exit_code": completed.returncode,
                "help_output_lines": len(help_output.splitlines()),
            }
        )

    return results


def main() -> None:
    assert sys.version_info[:2] == (3, 12)
    assert tinker.__version__ == "0.24.1"

    evidence = {
        "python_version": platform.python_version(),
        "tinker_version": tinker.__version__,
        "converter": _validate_converter(),
        "entrypoints": _validate_entrypoints(),
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
