from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

for source_root in (REPO_ROOT / "tvcache" / "client", REPO_ROOT / "train"):
    source_path = str(source_root)
    if source_path not in sys.path:
        sys.path.insert(0, source_path)

