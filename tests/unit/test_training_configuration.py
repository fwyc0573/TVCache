from __future__ import annotations

import ast
from pathlib import Path

import pytest


TRAIN_ROOT = Path(__file__).resolve().parents[2] / "train"
DRIVERS = [
    "train_without_cache.py",
    "train_with_stateless_cache.py",
    "train_with_tvcache.py",
]
DRIVER_VARIANTS = {
    "train_without_cache.py": "no_cache",
    "train_with_stateless_cache.py": "stateless_cache",
    "train_with_tvcache.py": "tvcache",
}


def _config_defaults(tree: ast.Module) -> dict[str, object]:
    config_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Config"
    )
    defaults: dict[str, object] = {}
    for node in config_class.body:
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        ):
            defaults[node.target.id] = ast.literal_eval(node.value)
    return defaults


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_uses_approved_model_and_renderer(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    defaults = _config_defaults(tree)
    recommended_renderer_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get_recommended_renderer_name"
    ]
    configured_renderer_uses = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "config"
        and node.attr == "renderer_name"
    ]

    assert defaults["model_name"] == "Qwen/Qwen3.6-35B-A3B"
    assert defaults["renderer_name"] == "qwen3_disable_thinking"
    assert recommended_renderer_calls == []
    assert configured_renderer_uses


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_imports_asyncio_for_entrypoint(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    imported_modules = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    asyncio_run_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "asyncio"
        and node.func.attr == "run"
    ]

    assert len(asyncio_run_calls) == 1
    assert "asyncio" in imported_modules


def test_tvcache_driver_propagates_explicit_cache_url() -> None:
    tree = ast.parse((TRAIN_ROOT / "train_with_tvcache.py").read_text())
    defaults = _config_defaults(tree)
    agent_loop_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "VideoAgentLoop"
    ]

    assert defaults["tvcache_base_url"] == "http://localhost:8001"
    assert len(agent_loop_calls) == 1
    keyword = next(
        keyword
        for keyword in agent_loop_calls[0].keywords
        if keyword.arg == "tvcache_base_url"
    )
    assert isinstance(keyword.value, ast.Attribute)
    assert isinstance(keyword.value.value, ast.Name)
    assert keyword.value.value.id == "config"
    assert keyword.value.attr == "tvcache_base_url"


def test_tvcache_driver_owns_run_level_cache_teardown() -> None:
    tree = ast.parse((TRAIN_ROOT / "train_with_tvcache.py").read_text())
    lifecycle_imports = [
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "utils.tvcache_run_lifecycle"
        for alias in node.names
    ]
    main_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "main"
    )
    lifecycle_contexts = [
        node
        for node in ast.walk(main_function)
        if isinstance(node, ast.AsyncWith)
        and any(
            isinstance(item.context_expr, ast.Call)
            and isinstance(item.context_expr.func, ast.Name)
            and item.context_expr.func.id == "TVCacheRunLifecycle"
            for item in node.items
        )
    ]
    register_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "register_task"
    ]

    assert lifecycle_imports == ["TVCacheRunLifecycle"]
    assert len(lifecycle_contexts) == 1
    assert len(register_calls) == 1


def test_training_manifest_pins_required_tinker_sdk() -> None:
    manifest = (TRAIN_ROOT / "pyproject.toml").read_text()

    assert '"tinker==0.24.1"' in manifest
    assert '"tinker>=0.6.3"' not in manifest


def test_training_manifest_declares_rollout_dependencies() -> None:
    manifest = (TRAIN_ROOT / "pyproject.toml").read_text()

    for requirement in [
        "chz",
        "datasets",
        "httpx",
        "pydantic",
        "tinker-cookbook",
        "tvclient",
    ]:
        assert f'"{requirement}"' in manifest
    assert '"torch==' in manifest

    assert (
        'tinker-cookbook = { path = "tinker-cookbook", editable = true }'
        in manifest
    )
    assert (
        'tvclient = { path = "../tvcache/client", editable = true }'
        in manifest
    )


def test_training_manifest_pins_cpu_only_torch() -> None:
    manifest = (TRAIN_ROOT / "pyproject.toml").read_text()

    assert '"torch==2.13.0+cpu"' in manifest
    assert 'torch = { index = "pytorch-cpu" }' in manifest
    assert 'name = "pytorch-cpu"' in manifest
    assert 'url = "https://download.pytorch.org/whl/cpu"' in manifest
    assert "explicit = true" in manifest


def test_training_lock_contains_no_cuda_runtime() -> None:
    lock = (TRAIN_ROOT / "uv.lock").read_text()

    assert 'name = "torch"\nversion = "2.13.0+cpu"' in lock
    assert '\nname = "nvidia-' not in lock
    for package_name in [
        "cuda-bindings",
        "cuda-pathfinder",
        "cuda-toolkit",
        "triton",
    ]:
        assert f'\nname = "{package_name}"' not in lock


def test_training_lock_targets_gpu_worker_platform() -> None:
    manifest = (TRAIN_ROOT / "pyproject.toml").read_text()

    assert (
        "environments = [\"sys_platform == 'linux' and "
        "platform_machine == 'x86_64'\"]"
        in manifest
    )


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_propagates_sandbox_teardown_failure(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    swallowed_stop_blocks = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        and node.handlers
        and any(
            isinstance(child, ast.Attribute)
            and child.attr == "stop_sandbox"
            for child in ast.walk(node)
        )
    ]

    assert swallowed_stop_blocks == []


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_uses_structured_rollout_execution(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    structured_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "run_agent_loops"
    ]
    unstructured_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"gather", "start_sandbox", "stop_sandbox"}
    ]

    assert len(structured_calls) == 1
    assert unstructured_calls == []


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_uses_explicit_dataset_slice(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    defaults = _config_defaults(tree)
    dataset_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "get_video_dataset"
    ]
    selector_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "select_dataset_slice"
    ]

    assert defaults["dataset_start"] == 0
    assert defaults["dataset_count"] == 100
    assert len(dataset_calls) == 1
    assert len(dataset_calls[0].args) == 2
    assert len(selector_calls) == 1


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_derives_run_specific_rollout_log_directory(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    assignments = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "rollout_log_dir"
            for target in node.targets
        )
    ]
    agent_loop_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"VideoAgentLoop", "CachedVideoAgentLoop"}
    ]

    assert len(assignments) == 1
    assert ast.unparse(assignments[0].value) == (
        "os.path.join(config.log_path, 'rollouts')"
    )
    assert len(agent_loop_calls) == 1
    rollout_keyword = next(
        keyword
        for keyword in agent_loop_calls[0].keywords
        if keyword.arg == "rollout_log_dir"
    )
    assert isinstance(rollout_keyword.value, ast.Name)
    assert rollout_keyword.value.id == "rollout_log_dir"


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_namespaces_sandbox_ids_by_run_and_variant(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    run_id_assignments = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "run_id"
            for target in node.targets
        )
    ]
    namespaced_sandbox_id_assignments = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "sandbox_id"
            for target in node.targets
        )
        and "run_id" in ast.unparse(node.value)
    ]

    assert len(run_id_assignments) == 1
    assert DRIVER_VARIANTS[driver_name] in ast.unparse(
        run_id_assignments[0].value
    )
    assert len(namespaced_sandbox_id_assignments) == 1


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_consumes_structured_rollout_output(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    structured_output_accesses = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr == "output"
    ]
    elapsed_time_accesses = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr == "elapsed_seconds"
    ]

    assert structured_output_accesses
    assert elapsed_time_accesses


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_uses_transition_aware_training_data(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    trajectory_conversion_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "trajectory_to_data"
    ]

    assert trajectory_conversion_calls


@pytest.mark.parametrize("driver_name", DRIVERS)
def test_training_driver_preserves_dataset_identity(
    driver_name: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    dataset_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "get_video_dataset"
    )
    dataset_records = [
        node
        for node in ast.walk(dataset_function)
        if isinstance(node, ast.Dict)
        and {
            key.value
            for key in node.keys
            if isinstance(key, ast.Constant)
        }
        >= {"question", "answer", "dataset_index", "video_id"}
    ]

    assert len(dataset_records) == 1
    record = dataset_records[0]
    record_values = {
        key.value: value
        for key, value in zip(record.keys, record.values)
        if isinstance(key, ast.Constant)
    }
    assert ast.unparse(record_values["dataset_index"]) == "dataset_index"
    assert ast.unparse(record_values["video_id"]) == "point['video_id']"


@pytest.mark.parametrize(
    ("driver_name", "variant"),
    [
        ("train_without_cache.py", "no_cache"),
        ("train_with_stateless_cache.py", "stateless_cache"),
        ("train_with_tvcache.py", "tvcache"),
    ],
)
def test_training_driver_persists_per_rollout_metrics(
    driver_name: str,
    variant: str,
) -> None:
    tree = ast.parse((TRAIN_ROOT / driver_name).read_text())
    record_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "build_rollout_record"
    ]
    write_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "write_rollout_records"
    ]

    assert len(record_calls) == 1
    keywords = {
        keyword.arg: ast.unparse(keyword.value)
        for keyword in record_calls[0].keywords
    }
    assert keywords == {
        "variant": repr(variant),
        "batch_index": "batch_idx",
        "dataset_index": "data['dataset_index']",
        "rollout_index": "rollout_index",
        "sandbox_id": "sandbox_id",
        "video_id": "data['video_id']",
        "agent_loop": "agent_loop",
        "execution_result": "rollout_result",
    }

    assert len(write_calls) == 1
    assert [ast.unparse(argument) for argument in write_calls[0].args] == [
        "config.log_path",
        "batch_rollout_records",
    ]
