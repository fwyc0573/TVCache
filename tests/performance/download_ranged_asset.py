#!/usr/bin/env python3
"""Download large public model assets with resumable HTTP ranges."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
import json
import os
from pathlib import Path
import threading
import time

import requests


ASSETS = {
    "lavila-base": (
        "https://dl.fbaipublicfiles.com/lavila/checkpoints/narrator/"
        "vclm_openai_timesformer_base_gpt2_base.pt_ego4d.jobid_319630."
        "ep_0002.md5sum_68a71f.pth"
    ),
    "clip-b32": (
        "https://openaipublic.azureedge.net/clip/models/"
        "40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/"
        "ViT-B-32.pt"
    ),
    "viclip-l": (
        "https://modelscope.cn/models/OpenGVLab/ViCLIP/resolve/master/"
        "ViClip-InternVid-10M-FLT.pth"
    ),
    "dinov2-s": (
        "https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/"
        "dinov2_vits14_pretrain.pth"
    ),
    "rtdetr-l": (
        "https://github.com/ultralytics/assets/releases/download/v8.3.0/"
        "rtdetr-l.pt"
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _head(url: str) -> int:
    response = requests.head(url, allow_redirects=True, timeout=60)
    size = response.headers.get("content-length")
    if response.ok and size is not None:
        return int(size)
    response = requests.get(
        url,
        headers={"Range": "bytes=0-0"},
        stream=True,
        timeout=(60, 120),
    )
    response.raise_for_status()
    if response.status_code != 206:
        raise RuntimeError(f"probe range request returned HTTP {response.status_code}")
    content_range = response.headers.get("content-range", "")
    try:
        return int(content_range.rsplit("/", 1)[1])
    except (IndexError, ValueError) as error:
        raise RuntimeError(f"missing content length for {url}") from error


def _download_part(url: str, destination: Path, start: int, end: int) -> None:
    expected = end - start + 1
    if destination.is_file() and destination.stat().st_size == expected:
        return
    temporary = destination.with_name(
        f"{destination.name}.tmp.{os.getpid()}.{threading.get_ident()}"
    )
    last_error: BaseException | None = None
    for attempt in range(1, 6):
        response = None
        published = False
        try:
            response = requests.get(
                url,
                headers={"Range": f"bytes={start}-{end}"},
                stream=True,
                timeout=(30, 120),
            )
            response.raise_for_status()
            if response.status_code != 206:
                raise RuntimeError(
                    f"range request {start}-{end} returned HTTP {response.status_code}"
                )
            content_range = response.headers.get("content-range", "")
            expected_range = f"bytes {start}-{end}/"
            if not content_range.startswith(expected_range):
                raise RuntimeError(
                    f"range request {start}-{end} returned Content-Range {content_range!r}"
                )
            actual = 0
            with temporary.open("wb") as stream:
                for block in response.iter_content(chunk_size=1024 * 1024):
                    if block:
                        stream.write(block)
                        actual += len(block)
            if actual != expected:
                raise RuntimeError(
                    f"range {start}-{end} returned {actual} bytes; expected {expected}"
                )
            if temporary.stat().st_size != expected:
                raise RuntimeError(
                    f"temporary range {start}-{end} has {temporary.stat().st_size} bytes; "
                    f"expected {expected}"
                )
            os.replace(temporary, destination)
            published = True
            return
        except (OSError, requests.RequestException, RuntimeError) as error:
            if isinstance(error, requests.HTTPError):
                if error.response.status_code not in {429, 500, 502, 503, 504}:
                    raise
            last_error = error
            print(
                f"range={start}-{end} attempt={attempt}/5 "
                f"failure={type(error).__name__}",
                flush=True,
            )
            if attempt == 5:
                break
            time.sleep(attempt)
        finally:
            if response is not None:
                response.close()
            if temporary.exists() and not published:
                temporary.unlink()
    assert last_error is not None
    raise RuntimeError(
        f"range {start}-{end} failed after 5 attempts"
    ) from last_error


def download(
    name: str,
    output: Path,
    workers: int,
    part_size_mb: int,
    expected_sha256: str | None = None,
    total_override: int | None = None,
    part_dir_override: Path | None = None,
) -> None:
    url = ASSETS[name]
    total = total_override if total_override is not None else _head(url)
    if total <= 0:
        raise ValueError("total_bytes must be positive")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_file() and output.stat().st_size == total:
        if expected_sha256:
            digest = _sha256(output)
            if digest != expected_sha256:
                raise RuntimeError(
                    f"{name}: existing file SHA-256 {digest} != {expected_sha256}"
                )
        print(f"{name}: already complete bytes={total}")
        return

    part_dir = part_dir_override or output.with_name(output.name + ".parts")
    part_dir.mkdir(exist_ok=True)
    if part_size_mb < 1:
        raise ValueError("part_size_mb must be positive")
    part_size = part_size_mb * 1024 * 1024
    manifest = part_dir / "manifest.json"
    manifest_data = {
        "asset": name,
        "url": url,
        "total_bytes": total,
        "part_size_bytes": part_size,
    }
    if manifest.exists():
        existing = json.loads(manifest.read_text())
        if existing != manifest_data:
            raise RuntimeError(
                f"part manifest mismatch at {manifest}: {existing} != {manifest_data}"
            )
    elif any(part_dir.glob("part-*")):
        raise RuntimeError(
            f"refusing to reuse unmanifested part directory: {part_dir}"
        )
    else:
        manifest.write_text(json.dumps(manifest_data, sort_keys=True) + "\n")
    ranges = []
    start = 0
    index = 0
    while start < total:
        end = min(total - 1, start + part_size - 1)
        ranges.append((index, start, end))
        start = end + 1
        index += 1

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(
                _download_part,
                url,
                part_dir / f"part-{index:04d}",
                start,
                end,
            )
            for index, start, end in ranges
        ]
        for future in futures:
            future.result()

    temporary = output.with_name(output.name + ".assembling")
    with temporary.open("wb") as stream:
        for index, _, _ in ranges:
            stream.write((part_dir / f"part-{index:04d}").read_bytes())
    if temporary.stat().st_size != total:
        raise RuntimeError(
            f"assembled {temporary.stat().st_size} bytes; expected {total}"
        )
    temporary.replace(output)
    if expected_sha256:
        digest = _sha256(output)
        if digest != expected_sha256:
            raise RuntimeError(
                f"{name}: SHA-256 {digest} != {expected_sha256}"
            )
    elapsed = time.monotonic() - started
    print(f"{name}: downloaded bytes={total} seconds={elapsed:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", choices=sorted(ASSETS))
    parser.add_argument("output", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--part-size-mb", type=int, default=1)
    parser.add_argument("--sha256", default=None)
    parser.add_argument("--total-bytes", type=int, default=None)
    parser.add_argument("--part-dir", type=Path, default=None)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.with_name(args.output.name + ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"A download already owns {args.output}") from error
        download(
            args.name,
            args.output,
            args.workers,
            args.part_size_mb,
            args.sha256,
            args.total_bytes,
            args.part_dir,
        )


if __name__ == "__main__":
    main()
