"""Download the exact Video-LLaVA and LanguageBind files used by the VQA server."""

import hashlib
import fnmatch
import json
import os
from pathlib import Path

from huggingface_hub import snapshot_download
from download_ranged_asset import ASSETS, download


cache = Path(os.environ.get('TVCACHE_HF_CACHE', '/data/ycfeng/tmp/tvcache-videollava-hf-cache'))
inventory = Path('/data/ycfeng/tmp/tvcache-asset-inventory-20260909')
repos = [
    ('LanguageBind/Video-LLaVA-7B', 'aecae02b7dee5c249e096dcb0ce546eb6f811806',
     ['*.safetensors', 'model.safetensors.index.json', 'config.json',
      'generation_config.json', 'tokenizer*', 'special_tokens_map.json']),
    ('LanguageBind/LanguageBind_Image', 'd8c2e37b439f4fc47c649dc8b90cdcd3a4e0c80e',
     ['pytorch_model.bin', '*.json', 'merges.txt']),
    ('LanguageBind/LanguageBind_Video_merge', 'efc40ec6ba6b2081276c11e7e19b24f08a099e79',
     ['pytorch_model.bin', '*.json', 'merges.txt']),
]
download_workers = int(os.environ.get('TVCACHE_DOWNLOAD_WORKERS', '8'))

for repo, revision, patterns in repos:
    metadata = json.loads((inventory / (repo.replace('/', '--') + '.json')).read_text())
    assert metadata['sha'] == revision, (repo, metadata['sha'], revision)
    print(f'Downloading {repo} revision={revision}', flush=True)
    # Populate the normal HF blob cache using the verified range downloader.
    # The mirror must provide the same pinned revision and official LFS digest.
    endpoint = os.environ.get('HF_ENDPOINT', 'https://huggingface.co').rstrip('/')
    for entry in metadata['siblings']:
        name = entry['rfilename']
        if not entry.get('lfs') or not any(fnmatch.fnmatch(name, p) for p in patterns):
            continue
        asset = f'{repo}/{name}'
        ASSETS[asset] = f'{endpoint}/{repo}/resolve/{revision}/{name}'
        blob = cache / ('models--' + repo.replace('/', '--')) / 'blobs' / entry['lfs']['sha256']
        download(asset, blob, workers=download_workers, part_size_mb=4,
                 expected_sha256=entry['lfs']['sha256'], total_override=entry['size'])
    snapshot = Path(snapshot_download(
        repo, revision=revision, cache_dir=cache, allow_patterns=patterns,
        max_workers=2,
    ))
    for entry in metadata['siblings']:
        file = snapshot / entry['rfilename']
        if not file.is_file():
            continue
        expected_size = entry['size']
        assert file.stat().st_size == expected_size, file
        # LFS blobs have already passed the official SHA-256 check above.
        print(f'Verified {repo}/{file.name} bytes={expected_size}', flush=True)
    # The existing service resolves the main cache ref in offline mode.
    ref = snapshot.parent.parent / 'refs' / 'main'
    ref.parent.mkdir(exist_ok=True)
    if ref.exists():
        assert ref.read_text().strip() == revision, ref
    else:
        ref.write_text(revision)
    print(f'Complete {repo} path={snapshot}', flush=True)
