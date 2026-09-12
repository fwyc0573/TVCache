#!/usr/bin/env python3
"""Complete the minimal pinned Hugging Face cache needed by Video-LLaVA offline loading."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
import argparse

BASE = Path("/data/ycfeng/tmp/tvcache-videollava-hf-cache-h800")
INVENTORY = Path("/data/ycfeng/tmp/tvcache-asset-inventory-20260909")
ENDPOINT = "https://artifactory.stepfun-inc.com/artifactory/api/huggingfaceml/huggingface-mirror"
REPOS = {
    "LanguageBind/Video-LLaVA-7B": "aecae02b7dee5c249e096dcb0ce546eb6f811806",
    "LanguageBind/LanguageBind_Image": "d8c2e37b439f4fc47c649dc8b90cdcd3a4e0c80e",
    "LanguageBind/LanguageBind_Video_merge": "efc40ec6ba6b2081276c11e7e19b24f08a099e79",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".download")
    subprocess.run(
        ["curl", "-fLsS", "--retry", "4", "--max-time", "900", url, "-o", str(tmp)],
        check=True,
    )
    tmp.replace(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=BASE)
    parser.add_argument("--inventory-dir", type=Path, default=INVENTORY)
    parser.add_argument("--endpoint", default=ENDPOINT)
    args = parser.parse_args()
    base, inventory_root, endpoint = args.cache_dir, args.inventory_dir, args.endpoint.rstrip("/")
    for repo, revision in REPOS.items():
        key = repo.replace("/", "--")
        root = base / ("models--" + key)
        snapshot = root / "snapshots" / revision
        snapshot.mkdir(parents=True, exist_ok=True)
        refs = root / "refs"
        refs.mkdir(parents=True, exist_ok=True)
        (refs / "main").write_text(revision)
        inventory = json.loads((inventory_root / (key + ".json")).read_text())
        for entry in inventory["siblings"]:
            name = entry["rfilename"]
            if name in {".gitattributes", "README.md"}:
                continue
            # The pinned Video-LLaVA snapshot has safetensors shards.  Avoid
            # downloading the duplicate ~15 GB PyTorch .bin checkpoint.
            if repo == "LanguageBind/Video-LLaVA-7B" and (
                name.startswith("pytorch_model-") or name == "pytorch_model.bin.index.json"
            ):
                continue
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            expected_size = entry.get("size")
            expected_sha = entry.get("lfs", {}).get("sha256")
            blob = root / "blobs" / expected_sha if expected_sha else None
            if blob and blob.exists() and expected_size == blob.stat().st_size:
                if target.exists() or target.is_symlink():
                    target.unlink()
                target.symlink_to(blob)
                continue
            if target.exists() and target.stat().st_size == expected_size:
                # Keep an already downloaded regular file, but verify LFS files.
                if expected_sha and sha256(target) != expected_sha:
                    target.unlink()
                else:
                    continue
            url = f"{endpoint}/{repo}/resolve/{revision}/{name}"
            print(f"download {repo} {name}", flush=True)
            download(url, target)
            if expected_size is not None and target.stat().st_size != expected_size:
                raise RuntimeError(f"size mismatch for {target}: {target.stat().st_size} != {expected_size}")
            if expected_sha and sha256(target) != expected_sha:
                raise RuntimeError(f"sha256 mismatch for {target}")
        print(f"complete {repo}: {snapshot}", flush=True)


if __name__ == "__main__":
    main()
