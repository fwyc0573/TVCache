from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from threading import Lock
from types import ModuleType, SimpleNamespace

import pytest


VIDEO_AGENT_ROOT = (
    Path(__file__).resolve().parents[2]
    / "video-agent-tools"
    / "VideoAgent"
)
SANDBOX_MANAGER_PATH = VIDEO_AGENT_ROOT / "sandbox_manager.py"


class DummyComponent:
    def __init__(self, **kwargs) -> None:
        return None


class DummyToolKit:
    def __init__(self, **kwargs) -> None:
        return None


@pytest.fixture
def sandbox_manager_module(
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    component_modules = {
        "captioning": ("Captioning", DummyComponent),
        "segment_feature": ("SegmentFeature", DummyComponent),
        "tracking": ("Tracking", DummyComponent),
        "reid": ("ReID", DummyComponent),
        "tools": ("ToolKit", DummyToolKit),
    }
    for module_name, (attribute_name, attribute) in component_modules.items():
        module = ModuleType(module_name)
        setattr(module, attribute_name, attribute)
        monkeypatch.setitem(sys.modules, module_name, module)

    langchain_module = ModuleType("langchain")
    langchain_module.hub = SimpleNamespace(
        pull=lambda name: SimpleNamespace(template="")
    )
    agents_module = ModuleType("langchain.agents")
    agents_module.AgentExecutor = object
    agents_module.create_react_agent = lambda *args, **kwargs: object()
    agents_module.tool = lambda function: function
    openai_module = ModuleType("langchain_openai")
    openai_module.ChatOpenAI = object
    core_module = ModuleType("langchain_core")
    exceptions_module = ModuleType("langchain_core.exceptions")
    exceptions_module.OutputParserException = RuntimeError

    monkeypatch.setitem(sys.modules, "langchain", langchain_module)
    monkeypatch.setitem(sys.modules, "langchain.agents", agents_module)
    monkeypatch.setitem(sys.modules, "langchain_openai", openai_module)
    monkeypatch.setitem(sys.modules, "langchain_core", core_module)
    monkeypatch.setitem(
        sys.modules,
        "langchain_core.exceptions",
        exceptions_module,
    )
    monkeypatch.syspath_prepend(str(VIDEO_AGENT_ROOT))

    spec = importlib.util.spec_from_file_location(
        "sandbox_manager_under_test",
        SANDBOX_MANAGER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _empty_manager(module: ModuleType):
    manager = module.SandboxManager.__new__(module.SandboxManager)
    manager.base_dir = "/sandbox-root"
    manager.datastructures_lock = Lock()
    manager.loaded_video = {}
    manager.fork_count = {}
    manager.toolkits = {}
    manager.completed_stop_operations = {}
    return manager


def test_stop_sandbox_accepts_empty_sandbox(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    removed_paths: list[str] = []
    monkeypatch.setattr(
        sandbox_manager_module.os.path,
        "exists",
        lambda path: True,
    )
    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "rmtree",
        removed_paths.append,
    )

    result = manager.stop_sandbox(
        "empty-sandbox",
        operation_id="stop-empty-sandbox",
    )

    assert result is True
    assert removed_paths == ["/sandbox-root/empty-sandbox"]
    assert manager.loaded_video == {}


def test_stop_sandbox_replays_completion_after_response_loss(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    sandbox_exists = True
    removed_paths: list[str] = []

    def path_exists(path: str) -> bool:
        return sandbox_exists

    def remove_path(path: str) -> None:
        nonlocal sandbox_exists
        removed_paths.append(path)
        sandbox_exists = False

    monkeypatch.setattr(
        sandbox_manager_module.os.path,
        "exists",
        path_exists,
    )
    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "rmtree",
        remove_path,
    )

    assert manager.stop_sandbox(
        "sandbox-1",
        operation_id="stop-operation-1",
    ) is True
    assert manager.stop_sandbox(
        "sandbox-1",
        operation_id="stop-operation-1",
    ) is True

    assert removed_paths == ["/sandbox-root/sandbox-1"]
    assert manager.completed_stop_operations == {
        "stop-operation-1": "sandbox-1",
    }

    with pytest.raises(FileNotFoundError, match="sandbox-1"):
        manager.stop_sandbox(
            "sandbox-1",
            operation_id="different-operation",
        )


def test_create_sandbox_rejects_residual_directory(
    sandbox_manager_module: ModuleType,
    tmp_path: Path,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.base_dir = str(tmp_path)
    residual_path = tmp_path / "rollout-1"
    residual_path.mkdir()
    marker_path = residual_path / "marker.txt"
    marker_path.write_text("existing state")

    with pytest.raises(FileExistsError, match="rollout-1"):
        manager.create_sandbox("rollout-1")

    assert marker_path.read_text() == "existing state"


def test_fork_loaded_only_sandbox_does_not_generate_toolkit(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.loaded_video["parent"] = "video.mp4"
    toolkit_calls: list[str] = []
    monkeypatch.setattr(
        sandbox_manager_module.os.path,
        "exists",
        lambda path: True,
    )
    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "copytree",
        lambda source, destination: None,
    )

    def record_toolkit(sandbox_id: str) -> None:
        toolkit_calls.append(sandbox_id)

    manager.generate_toolkit = record_toolkit

    result = manager.fork("parent")

    assert result == {"sandbox_id": "parent_1"}
    assert manager.loaded_video["parent_1"] == "video.mp4"
    assert toolkit_calls == []


def test_fork_propagates_toolkit_failure_and_cleans_copy(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.toolkits["parent"] = DummyToolKit()
    removed_paths: list[str] = []
    monkeypatch.setattr(
        sandbox_manager_module.os.path,
        "exists",
        lambda path: True,
    )
    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "copytree",
        lambda source, destination: None,
    )
    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "rmtree",
        removed_paths.append,
    )

    def fail_toolkit(sandbox_id: str) -> None:
        raise RuntimeError("toolkit creation failed")

    manager.generate_toolkit = fail_toolkit

    with pytest.raises(RuntimeError, match="toolkit creation failed"):
        manager.fork("parent")

    assert removed_paths == ["/sandbox-root/parent_1"]


def test_fork_rolls_back_partial_copy_failure(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
    tmp_path: Path,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.base_dir = str(tmp_path)
    parent_path = tmp_path / "parent"
    parent_path.mkdir()

    def fail_after_partial_copy(source: str, destination: str) -> None:
        destination_path = Path(destination)
        destination_path.mkdir()
        (destination_path / "partial.bin").write_bytes(b"partial")
        raise OSError("copy failed")

    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "copytree",
        fail_after_partial_copy,
    )

    with pytest.raises(OSError, match="copy failed"):
        manager.fork("parent")

    assert not (tmp_path / "parent_1").exists()
    assert "parent" not in manager.fork_count
    assert "parent_1" not in manager.loaded_video
    assert "parent_1" not in manager.toolkits


def test_fork_preserves_copy_and_rollback_failures(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
    tmp_path: Path,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.base_dir = str(tmp_path)
    (tmp_path / "parent").mkdir()

    def fail_after_partial_copy(source: str, destination: str) -> None:
        Path(destination).mkdir()
        raise OSError("copy failed")

    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "copytree",
        fail_after_partial_copy,
    )
    monkeypatch.setattr(
        sandbox_manager_module.shutil,
        "rmtree",
        lambda path: (_ for _ in ()).throw(OSError("rollback failed")),
    )

    with pytest.raises(RuntimeError) as exc_info:
        manager.fork("parent")

    assert "copy failed" in str(exc_info.value)
    assert "rollback failed" in str(exc_info.value)
    assert manager.fork_count["parent"] == 1


def test_object_query_propagates_agent_failure(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.get_toolkit = lambda sandbox_id: SimpleNamespace()
    monkeypatch.chdir(VIDEO_AGENT_ROOT)
    monkeypatch.setattr(
        sandbox_manager_module.pickle,
        "load",
        lambda file: SimpleNamespace(template=""),
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "ChatOpenAI",
        lambda **kwargs: object(),
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "create_react_agent",
        lambda *args, **kwargs: object(),
    )

    class FailingAgentExecutor:
        def __init__(self, **kwargs) -> None:
            return None

        def invoke(self, inputs):
            raise RuntimeError("object query failed")

    monkeypatch.setattr(
        sandbox_manager_module,
        "AgentExecutor",
        FailingAgentExecutor,
    )

    with pytest.raises(RuntimeError, match="object query failed"):
        manager.object_memory_querying("sandbox-1", "question")


def test_vqa_releases_lock_after_tool_failure(
    sandbox_manager_module: ModuleType,
) -> None:
    class FailingToolKit:
        def visual_question_answering(
            self,
            question: str,
            segment_id: int,
        ) -> str:
            raise RuntimeError("VQA failed")

    manager = _empty_manager(sandbox_manager_module)
    manager.llava_lock = Lock()
    manager.get_toolkit = lambda sandbox_id: FailingToolKit()

    with pytest.raises(RuntimeError, match="VQA failed"):
        manager.visual_question_answering(
            "sandbox-1",
            "('what happened?', 1)",
        )

    assert manager.llava_lock.acquire(blocking=False) is True
    manager.llava_lock.release()


def test_constructor_requires_deepseek_key_before_component_initialization(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
    tmp_path: Path,
) -> None:
    class RecordingComponent:
        initialization_count = 0

        def __init__(self, **kwargs) -> None:
            type(self).initialization_count += 1

    monkeypatch.setenv("EGOSCHEMA_VIDEO_DIR", str(tmp_path))
    monkeypatch.delenv("STEPCODE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        sandbox_manager_module,
        "Captioning",
        RecordingComponent,
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "SegmentFeature",
        RecordingComponent,
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "Tracking",
        RecordingComponent,
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "ReID",
        RecordingComponent,
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "CACHE_FILE",
        tmp_path / "react_prompt_cache.pkl",
    )

    with pytest.raises(RuntimeError, match="STEPCODE_API_KEY is required"):
        sandbox_manager_module.SandboxManager(base_dir=str(tmp_path))

    assert RecordingComponent.initialization_count == 0


def test_constructor_propagates_absolute_model_directory_from_foreign_cwd(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
    tmp_path: Path,
) -> None:
    class RecordingComponent:
        calls: list[dict[str, object]] = []

        def __init__(self, **kwargs) -> None:
            type(self).calls.append(kwargs)

    video_dir = tmp_path / "videos"
    cache_dir = tmp_path / "cache"
    runtime_dir = tmp_path / "runtime"
    model_dir = tmp_path / "models"
    sandbox_dir = tmp_path / "sandboxes"
    caller_dir = tmp_path / "caller"
    for directory in (
        video_dir,
        cache_dir,
        runtime_dir,
        model_dir,
        sandbox_dir,
        caller_dir,
    ):
        directory.mkdir()

    monkeypatch.setenv("EGOSCHEMA_VIDEO_DIR", str(video_dir))
    monkeypatch.setenv("STEPCODE_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EGOSCHEMA_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("VIDEO_LLAVA_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("VIDEO_AGENT_MODEL_DIR", str(model_dir))
    monkeypatch.chdir(caller_dir)
    for component_name in ("Captioning", "SegmentFeature", "Tracking", "ReID"):
        monkeypatch.setattr(
            sandbox_manager_module,
            component_name,
            RecordingComponent,
        )

    sandbox_manager_module.SandboxManager(base_dir=str(sandbox_dir))

    assert len(RecordingComponent.calls) == 4
    for call in RecordingComponent.calls[:3]:
        assert call["model_dir"] == model_dir.resolve()


def test_object_query_uses_deepseek_v4_flash_without_thinking(
    monkeypatch: pytest.MonkeyPatch,
    sandbox_manager_module: ModuleType,
) -> None:
    manager = _empty_manager(sandbox_manager_module)
    manager.provider_api_key = "test-stepcode-key"
    manager.provider_base_url = "https://models-proxy.stepfun-inc.com"
    manager.get_toolkit = lambda sandbox_id: SimpleNamespace()
    monkeypatch.setattr(
        sandbox_manager_module.pickle,
        "load",
        lambda file: SimpleNamespace(template=""),
    )
    model_calls: list[dict[str, object]] = []

    def record_model(**kwargs):
        model_calls.append(kwargs)
        return object()

    monkeypatch.setattr(
        sandbox_manager_module,
        "ChatOpenAI",
        record_model,
    )
    monkeypatch.setattr(
        sandbox_manager_module,
        "create_react_agent",
        lambda *args, **kwargs: object(),
    )

    class SuccessfulAgentExecutor:
        def __init__(self, **kwargs) -> None:
            return None

        def invoke(self, inputs):
            return {"output": "answer"}

    monkeypatch.setattr(
        sandbox_manager_module,
        "AgentExecutor",
        SuccessfulAgentExecutor,
    )

    assert manager.object_memory_querying(
        "sandbox-1",
        "question",
    ) == "answer"
    assert model_calls == [
        {
            "model": "deepseek-v4-flash",
            "temperature": 0.0,
            "api_key": "test-stepcode-key",
            "base_url": "https://models-proxy.stepfun-inc.com",
            "model_kwargs": {
                "extra_body": {
                    "thinking": {
                        "type": "disabled",
                    },
                },
            },
        },
    ]
