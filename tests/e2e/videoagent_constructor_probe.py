"""Load the three real VideoAgent wrappers on CUDA and record memory use."""

import gc
import importlib
import json
import os
from pathlib import Path
import sys
import time

import torch


def main():
    output = Path(sys.argv[1])
    model_dir = Path(os.environ["VIDEO_AGENT_MODEL_DIR"])
    assert torch.cuda.is_available(), "CUDA is required"
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] /
                           "video-agent-tools" / "VideoAgent"))
    result = {"python": sys.version, "torch": torch.__version__,
              "gpu": torch.cuda.get_device_name(0), "constructors": []}
    for module_name, class_name in (("captioning", "Captioning"),
                                    ("segment_feature", "SegmentFeature"),
                                    ("tracking", "Tracking")):
        print(f"START {class_name}", flush=True)
        started = time.monotonic()
        torch.cuda.reset_peak_memory_stats()
        constructor = getattr(importlib.import_module(module_name), class_name)
        instance = constructor([], model_dir=model_dir)
        torch.cuda.synchronize()
        row = {"class": class_name, "seconds": time.monotonic() - started,
               "allocated_bytes": torch.cuda.memory_allocated(),
               "peak_allocated_bytes": torch.cuda.max_memory_allocated()}
        assert row["allocated_bytes"] > 0, row
        result["constructors"].append(row)
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(row), flush=True)
        del instance
        gc.collect()
        torch.cuda.empty_cache()
    print("PASS constructors=3", flush=True)


if __name__ == "__main__":
    main()
