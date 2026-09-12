from __future__ import annotations

import os
from pathlib import Path


VIDEO_AGENT_ROOT = Path(__file__).resolve().parent


class VideoAgentModelConfig:
    """The smallest verified local model combination for this rollout."""

    lavila_constructor = "VCLM_OPENAI_TIMESFORMER_BASE_GPT2"
    lavila_checkpoint = (
        "vclm_openai_timesformer_base_gpt2_base.pt_ego4d.jobid_319630."
        "ep_0002.md5sum_68a71f.pth"
    )
    lavila_tokenizer = "gpt2_tokenizer"
    lavila_crop_size = 224
    lavila_random_init_dependencies = True
    viclip_variant = "l"
    viclip_checkpoint = "ViCLIP/ViClip-InternVid-10M-FLT.pth"
    clip_checkpoint = "ViT-B-32.pt"
    dinov2_constructor = "dinov2_vits14"
    dinov2_checkpoint = "dinov2_vits14_pretrain.pth"
    rtdetr_checkpoint = "rtdetr-l.pt"


MODEL_CONFIG = VideoAgentModelConfig()


def resolve_video_agent_path(*parts: str) -> Path:
    return VIDEO_AGENT_ROOT.joinpath(*parts).resolve()


def resolve_required_environment_value(variable_name: str) -> str:
    value = os.environ.get(variable_name)
    if value is None or not value.strip():
        raise RuntimeError(f"{variable_name} is required")
    return value


def resolve_required_directory(variable_name: str) -> Path:
    value = resolve_required_environment_value(variable_name)
    directory = Path(value).expanduser()
    if not directory.is_absolute():
        raise ValueError(f"{variable_name} must be absolute: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(
            f"{variable_name} must reference an existing directory: "
            f"{directory}"
        )
    return directory.resolve()
