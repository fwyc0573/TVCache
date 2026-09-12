from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


VIDEO_AGENT_ROOT = (
    Path(__file__).resolve().parents[2]
    / "video-agent-tools"
    / "VideoAgent"
)
CAPTIONING_PATH = VIDEO_AGENT_ROOT / "captioning.py"


class FakeTensor:
    def __init__(self, value) -> None:
        self.value = value

    def unsqueeze(self, dimension: int) -> "FakeTensor":
        assert dimension == 0
        return self


@pytest.fixture
def captioning_module(
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    torch_module = ModuleType("torch")
    torch_module.Tensor = FakeTensor
    torch_module.float32 = object()
    torch_module.tensor = lambda value, dtype: FakeTensor(value)
    torch_module.stack = (
        lambda tensors, dim: FakeTensor([tensor.value for tensor in tensors])
    )

    transforms_module = ModuleType("torchvision.transforms")
    transforms_module.Compose = lambda transforms: lambda value: value
    transforms_module.Resize = lambda size: object()
    transforms_module.CenterCrop = lambda size: object()
    video_transforms_module = ModuleType(
        "torchvision.transforms._transforms_video"
    )
    video_transforms_module.NormalizeVideo = lambda **kwargs: object()
    torchvision_module = ModuleType("torchvision")
    torchvision_module.transforms = transforms_module

    video_transform_module = ModuleType(
        "LaViLa.lavila.data.video_transforms"
    )
    video_transform_module.Permute = lambda order: object()
    models_module = ModuleType("LaViLa.lavila.models.models")
    models_module.VCLM_OPENAI_TIMESFORMER_LARGE_336PX_GPT2_XL = object
    tokenizer_module = ModuleType("LaViLa.lavila.models.tokenizer")
    tokenizer_module.MyGPT2Tokenizer = object
    narrator_module = ModuleType("LaViLa.eval_narrator")
    narrator_module.decode_one = lambda tokens, tokenizer: ""

    for name, module in {
        "torch": torch_module,
        "torchvision": torchvision_module,
        "torchvision.transforms": transforms_module,
        "torchvision.transforms._transforms_video": (
            video_transforms_module
        ),
        "LaViLa.lavila.data.video_transforms": video_transform_module,
        "LaViLa.lavila.models.models": models_module,
        "LaViLa.lavila.models.tokenizer": tokenizer_module,
        "LaViLa.eval_narrator": narrator_module,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)

    monkeypatch.syspath_prepend(str(VIDEO_AGENT_ROOT))
    spec = importlib.util.spec_from_file_location(
        "captioning_provider_under_test",
        CAPTIONING_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_on_demand_captioning_uses_local_lavila_and_zero_api_tokens(
    monkeypatch: pytest.MonkeyPatch,
    captioning_module: ModuleType,
) -> None:
    class FakeCapture:
        def __init__(self, video_path: str) -> None:
            self.position = 0
            self.released = False

        def isOpened(self) -> bool:
            return True

        def get(self, property_id: int) -> float:
            assert property_id == captioning_module.cv2.CAP_PROP_FPS
            return 2.0

        def set(self, property_id: int, value: int) -> bool:
            assert property_id == captioning_module.cv2.CAP_PROP_POS_FRAMES
            self.position = value
            return True

        def read(self):
            frame = self.position
            self.position += 1
            return True, frame

        def release(self) -> None:
            self.released = True

    capture = FakeCapture("video.mp4")
    monkeypatch.setattr(
        captioning_module.cv2,
        "VideoCapture",
        lambda video_path: capture,
    )
    captioning = captioning_module.Captioning.__new__(
        captioning_module.Captioning
    )
    captioning.val_transform = lambda frames: frames
    generated_frames: list[FakeTensor] = []

    def generate_local_caption(frames: FakeTensor) -> str:
        generated_frames.append(frames)
        return f"caption-{len(generated_frames)}"

    captioning.get_captions_from_frames = generate_local_caption

    captions, prompt_tokens, completion_tokens = (
        captioning.generate_captions_for_frames(
            "video.mp4",
            start_frame_idx=0,
            end_frame_idx=8,
        )
    )

    assert captions == {
        0: "caption-1",
        4: "caption-2",
    }
    assert prompt_tokens == 0
    assert completion_tokens == 0
    assert len(generated_frames) == 2
    assert capture.released is True


def test_active_video_agent_path_contains_no_openai_visual_fallback() -> None:
    manager_source = (VIDEO_AGENT_ROOT / "sandbox_manager.py").read_text()
    captioning_source = CAPTIONING_PATH.read_text()
    toolkit_source = (VIDEO_AGENT_ROOT / "tools.py").read_text()

    for forbidden in (
        "OPENAI_API_KEY",
        "openai_api_key",
        "gpt-4.1",
    ):
        assert forbidden not in manager_source
    for forbidden in (
        "from openai import OpenAI",
        "self.client",
        "gpt-4.1-mini",
    ):
        assert forbidden not in captioning_source
    for forbidden in (
        "openai_api_key",
        "gpt4v_VQA",
        "api.openai.com",
        "gpt-4-vision-preview",
    ):
        assert forbidden not in toolkit_source
