from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import runpy
import sys
from types import ModuleType

import pytest


VIDEO_AGENT_ROOT = (
    Path(__file__).resolve().parents[2]
    / "video-agent-tools"
    / "VideoAgent"
)
CONFIG_MODULE_PATH = VIDEO_AGENT_ROOT / "runtime_config.py"


def _load_runtime_config() -> ModuleType:
    assert CONFIG_MODULE_PATH.is_file(), (
        f"Missing runtime configuration module: {CONFIG_MODULE_PATH}"
    )
    spec = importlib.util.spec_from_file_location(
        "video_agent_runtime_config_under_test",
        CONFIG_MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_video_directory_configuration_is_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_runtime_config()
    monkeypatch.delenv("EGOSCHEMA_VIDEO_DIR", raising=False)

    with pytest.raises(
        RuntimeError,
        match="EGOSCHEMA_VIDEO_DIR is required",
    ):
        module.resolve_required_directory("EGOSCHEMA_VIDEO_DIR")


def test_video_directory_configuration_must_be_a_directory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_runtime_config()
    file_path = VIDEO_AGENT_ROOT.parents[1] / "train" / "pyproject.toml"
    monkeypatch.setenv("EGOSCHEMA_VIDEO_DIR", str(file_path))

    with pytest.raises(
        NotADirectoryError,
        match="EGOSCHEMA_VIDEO_DIR must reference an existing directory",
    ):
        module.resolve_required_directory("EGOSCHEMA_VIDEO_DIR")


def test_runtime_directory_configuration_must_be_absolute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_runtime_config()
    monkeypatch.setenv("VIDEO_LLAVA_RUNTIME_DIR", "relative/runtime")

    with pytest.raises(
        ValueError,
        match="VIDEO_LLAVA_RUNTIME_DIR must be absolute",
    ):
        module.resolve_required_directory("VIDEO_LLAVA_RUNTIME_DIR")


def test_sandbox_manager_uses_configured_video_directory() -> None:
    source = (VIDEO_AGENT_ROOT / "sandbox_manager.py").read_text()

    assert "path/to/train/EgoSchema/videos" not in source
    assert (
        "self.video_dir = "
        'resolve_required_directory("EGOSCHEMA_VIDEO_DIR")'
        in source
    )
    assert "os.path.join(self.video_dir, video_name)" in source


def test_required_environment_value_rejects_missing_or_blank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_runtime_config()
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY is required"):
        module.resolve_required_environment_value("DEEPSEEK_API_KEY")

    monkeypatch.setenv("DEEPSEEK_API_KEY", "   ")
    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY is required"):
        module.resolve_required_environment_value("DEEPSEEK_API_KEY")


def test_sandbox_manager_uses_fixed_module_relative_prompt_asset() -> None:
    source = (VIDEO_AGENT_ROOT / "sandbox_manager.py").read_text()

    assert "hub.pull" not in source
    assert (
        'Path(__file__).with_name("react_prompt_cache.pkl")'
        in source
    )
    assert "open(CACHE_FILE, 'wb')" not in source


def test_active_video_agent_runtime_paths_are_explicit() -> None:
    manager_source = (VIDEO_AGENT_ROOT / "sandbox_manager.py").read_text()
    server_source = (VIDEO_AGENT_ROOT / "sandbox_server.py").read_text()
    toolkit_source = (VIDEO_AGENT_ROOT / "tools.py").read_text()
    videollava_source = (VIDEO_AGENT_ROOT / "video-llava.py").read_text()
    launch_source = (VIDEO_AGENT_ROOT / "run_sandbox.sh").read_text()

    assert "VIDEO_AGENT_SANDBOX_DIR" in server_source
    assert "EGOSCHEMA_CACHE_DIR" in manager_source
    assert "VIDEO_LLAVA_RUNTIME_DIR" in manager_source
    assert "VIDEO_LLAVA_RUNTIME_DIR" in videollava_source
    assert "VIDEO_LLAVA_CACHE_DIR" in videollava_source
    assert '"tmp/vqa.sock"' not in toolkit_source
    assert "'tmp/content.pkl'" not in toolkit_source
    assert '"tmp/vqa.sock"' not in videollava_source
    assert "'tmp/content.pkl'" not in videollava_source
    assert "your_key" not in launch_source


def test_video_agent_module_path_is_independent_of_caller_cwd(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _load_runtime_config()
    monkeypatch.chdir(tmp_path)

    resolved_path = module.resolve_video_agent_path(
        "captioning_prompt.txt"
    )

    assert resolved_path == (
        VIDEO_AGENT_ROOT / "captioning_prompt.txt"
    ).resolve()
    assert resolved_path.is_absolute()


@pytest.mark.parametrize(
    "relative_path",
    [
        "captioning.py",
        "segment_feature.py",
        "tracking.py",
        "tools.py",
    ],
)
def test_active_model_assets_have_no_cwd_relative_literals(
    relative_path: str,
) -> None:
    tree = ast.parse((VIDEO_AGENT_ROOT / relative_path).read_text())
    cwd_relative_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and (
            node.value.startswith("tool_models/")
            or node.value.startswith("./captioning_prompt")
            or node.value == "LaViLa/"
        )
    }

    assert cwd_relative_literals == set()


def test_sandbox_entrypoint_binds_loopback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_calls: list[dict[str, object]] = []

    class FakeApplication:
        def route(self, *args, **kwargs):
            return lambda function: function

        def run(self, **kwargs) -> None:
            run_calls.append(kwargs)

    flask_module = ModuleType("flask")
    flask_module.Flask = lambda name: FakeApplication()
    flask_module.request = object()
    flask_module.jsonify = lambda *args, **kwargs: None
    runtime_module = ModuleType("runtime_config")
    runtime_module.resolve_required_directory = (
        lambda variable_name: VIDEO_AGENT_ROOT
    )
    manager_module = ModuleType("sandbox_manager")
    manager_module.SandboxManager = lambda **kwargs: object()

    monkeypatch.setitem(sys.modules, "flask", flask_module)
    monkeypatch.setitem(sys.modules, "runtime_config", runtime_module)
    monkeypatch.setitem(sys.modules, "sandbox_manager", manager_module)

    runpy.run_path(
        str(VIDEO_AGENT_ROOT / "sandbox_server.py"),
        run_name="__main__",
    )

    assert run_calls == [{"host": "127.0.0.1", "port": 5000}]
