"""Record the image runtime and exercise a real CUDA operation."""

import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import sys

import torch


names = [
    "transformers", "torchvision", "ultralytics", "openai-clip", "timm",
    "decord", "moviepy", "langchain", "langchain-openai",
    "sentence-transformers", "bitsandbytes", "einops", "pytorchvideo",
    "numpy", "sentencepiece", "peft", "accelerate", "ftfy", "opencv-python",
]
installed = {d.metadata["Name"].lower(): d.version for d in metadata.distributions()}
result = {
    "python": sys.version,
    "host": platform.node(),
    "torch": torch.__version__,
    "cuda_available": torch.cuda.is_available(),
    "packages": {name: installed.get(name, "MISSING") for name in names},
}
assert result["cuda_available"], "CUDA must be available in the GPU worker"
result["gpu"] = torch.cuda.get_device_name(0)
result["cuda_sum"] = torch.ones(4, device="cuda").sum().item()
assert result["cuda_sum"] == 4.0, result
Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result), flush=True)
