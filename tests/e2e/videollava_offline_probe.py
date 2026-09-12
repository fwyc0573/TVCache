"""Exercise the production four-bit Video-LLaVA loader with offline assets."""

import json
import os
from pathlib import Path
import sys
import time


def main():
    output = Path(sys.argv[1]).resolve()
    repo = Path(__file__).resolve().parents[2]
    cache = Path(os.environ["VIDEO_LLAVA_CACHE_DIR"]).resolve(strict=True)
    runtime = Path(os.environ["VIDEO_LLAVA_RUNTIME_DIR"]).resolve(strict=True)
    assert os.environ["HF_HUB_OFFLINE"] == "1"
    assert os.environ["TRANSFORMERS_OFFLINE"] == "1"
    assert (runtime / "cache_dir").resolve(strict=True) == cache
    os.chdir(runtime)
    sys.path.insert(0, str(repo / "video-agent-tools" / "Video-LLaVA"))
    import torch
    from videollava.model.builder import load_pretrained_model
    from videollava.utils import disable_torch_init

    assert torch.cuda.is_available(), "CUDA is required"
    cuda_sum = torch.zeros(4, device="cuda").sum().item()
    assert cuda_sum == 0.0, cuda_sum
    print(f"CUDA zeros sum={cuda_sum} torch={torch.__version__}", flush=True)
    disable_torch_init()
    started = time.monotonic()
    print("START offline four-bit loader", flush=True)
    tokenizer, model, processors, context = load_pretrained_model(
        "LanguageBind/Video-LLaVA-7B", None, "Video-LLaVA-7B",
        load_4bit=True, device="cuda", cache_dir=str(cache),
    )
    torch.cuda.synchronize()
    assert model.is_loaded_in_4bit
    assert model.get_image_tower().is_loaded
    assert model.get_video_tower().is_loaded
    assert processors["image"] is not None and processors["video"] is not None
    assert torch.cuda.memory_allocated() > 0
    result = {
        "status": "PASS", "python": sys.version, "torch": torch.__version__,
        "cuda_build": torch.version.cuda, "cuda_zeros_sum": cuda_sum,
        "gpu": torch.cuda.get_device_name(0), "seconds": time.monotonic() - started,
        "allocated_bytes": torch.cuda.memory_allocated(),
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "context_length": context, "tokenizer_length": len(tokenizer),
        "four_bit": bool(model.is_loaded_in_4bit),
        "image_tower_loaded": True, "video_tower_loaded": True,
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
