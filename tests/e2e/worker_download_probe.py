"""Measure a bounded public checkpoint range from the intended GPU worker."""

import json
import os
from pathlib import Path
import socket
import sys
import time

import requests


url = (
    "https://hf-mirror.com/LanguageBind/Video-LLaVA-7B/resolve/"
    "aecae02b7dee5c249e096dcb0ce546eb6f811806/model-00001-of-00002.safetensors"
)
size = 8 * 1024 * 1024
started = time.monotonic()
received = 0
with requests.get(url, headers={"Range": f"bytes=0-{size - 1}"},
                  stream=True, timeout=(10, 30)) as response:
    response.raise_for_status()
    assert response.status_code == 206, response.status_code
    assert response.headers["Content-Range"] == f"bytes 0-{size - 1}/9976576392"
    for block in response.iter_content(1024 * 1024):
        received += len(block)
        if time.monotonic() - started > 50:
            break
result = {
    "host": socket.gethostname(), "python": sys.version.split()[0],
    "requested_bytes": size, "received_bytes": received,
    "elapsed_seconds": time.monotonic() - started,
    "complete": received == size,
}
result["bytes_per_second"] = received / result["elapsed_seconds"]
Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result), flush=True)
