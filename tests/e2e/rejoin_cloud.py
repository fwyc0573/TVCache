#!/usr/bin/env python3
"""Persist ReJoin source, evidence, and complete registry images on JuiceFS."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.parse
import urllib.request


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + '.part')
    part.write_text(json.dumps(value, indent=2) + '\n')
    part.replace(path)


def file_digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def persist(config_path: Path, local_report: Path) -> None:
    config = json.loads(config_path.read_text())
    root = Path(config['cloud_root'])
    if not root.is_relative_to('/mnt/codesign-exp/ycfeng'):
        raise ValueError('Cloud output must be inside the personal ycfeng directory')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    root.chmod(0o700)
    for name in ('sources', 'manifests', 'code', 'evidence/p03', 'rollouts/p04', 'reports'):
        (root / name).mkdir(parents=True, exist_ok=True)
    gpu = subprocess.check_output(['nvidia-smi', '-L'], text=True).strip()
    report = {'cloud_root': str(root), 'started_at': time.time(), 'gpu': gpu,
              'files': [], 'images': [], 'source_revision': config['source_revision']}
    for item in config['files']:
        source = config_path.parent / item['source']
        target = root / item['destination']
        if not target.resolve().is_relative_to(root.resolve()):
            raise ValueError('Output path leaves the task directory')
        target.parent.mkdir(parents=True, exist_ok=True)
        part = target.with_name(target.name + '.part')
        shutil.copyfile(source, part)
        digest = file_digest(part)
        if digest != item['sha256'] or part.stat().st_size != item['size']:
            raise ValueError(f'Copy verification failed for {item["destination"]}')
        part.replace(target)
        report['files'].append({**item, 'cloud_path': str(target), 'verified': True})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    registry = 'https://hub.i.basemind.com'
    repository = 'swe-openhands/runtime'
    layout = root / 'images/oci'
    blobs = layout / 'blobs/sha256'
    blobs.mkdir(parents=True, exist_ok=True)
    descriptors = []
    verified_blobs = {}
    for image in config['images']:
        scope = urllib.parse.quote('repository:' + repository + ':pull', safe='')
        with opener.open(registry + '/service/token?service=harbor-registry&scope=' + scope,
                         timeout=60) as response:
            token = json.load(response)['token']
        headers = {'Authorization': 'Bearer ' + token,
                   'Accept': 'application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json'}
        request = urllib.request.Request(
            f'{registry}/v2/{repository}/manifests/{image["image_digest"]}', headers=headers)
        with opener.open(request, timeout=60) as response:
            raw = response.read()
        digest = 'sha256:' + hashlib.sha256(raw).hexdigest()
        if digest != image['image_digest']:
            raise ValueError(f'Image manifest differs: {image["task_id"]}')
        manifest = json.loads(raw)
        manifest_file = blobs / digest.split(':')[1]
        manifest_file.write_bytes(raw)
        for blob in [manifest['config'], *manifest['layers']]:
            blob_digest = blob['digest']
            if not blob_digest.startswith('sha256:'):
                raise ValueError('Only sha256 registry blobs are supported')
            if blob_digest in verified_blobs:
                continue
            destination = blobs / blob_digest.split(':')[1]
            if destination.exists():
                if destination.stat().st_size != blob['size'] or file_digest(destination) != blob_digest[7:]:
                    raise ValueError(f'Existing blob failed verification: {blob_digest}')
            else:
                part = destination.with_name(destination.name + '.part')
                request = urllib.request.Request(
                    f'{registry}/v2/{repository}/blobs/{blob_digest}', headers=headers)
                hasher = hashlib.sha256()
                size = 0
                with opener.open(request, timeout=120) as response, part.open('wb') as stream:
                    for chunk in iter(lambda: response.read(1024 * 1024), b''):
                        stream.write(chunk)
                        hasher.update(chunk)
                        size += len(chunk)
                if size != blob['size'] or hasher.hexdigest() != blob_digest[7:]:
                    raise ValueError(f'Download failed verification: {blob_digest}')
                part.replace(destination)
            verified_blobs[blob_digest] = blob['size']
        descriptor = {'mediaType': manifest['mediaType'], 'digest': digest, 'size': len(raw),
                      'annotations': {'org.opencontainers.image.ref.name': image['task_id']}}
        descriptors.append(descriptor)
        report['images'].append({**image, 'verified': True, 'layer_count': len(manifest['layers']),
                                 'oci_reference': f'oci:{layout}:{image["task_id"]}'})
        write_json(root / 'reports/transfer_progress.json', report)
        print('IMAGE_PERSISTED', image['task_id'], 'unique_blob_bytes', sum(verified_blobs.values()), flush=True)
    write_json(layout / 'oci-layout', {'imageLayoutVersion': '1.0.0'})
    write_json(layout / 'index.json', {'schemaVersion': 2, 'manifests': descriptors})
    report.update(status='PASS', finished_at=time.time(), blob_count=len(verified_blobs),
                  blob_bytes=sum(verified_blobs.values()), blobs=verified_blobs)
    write_json(root / 'reports/storage_transfer.json', report)
    write_json(local_report, report)
    local_report.chmod(0o666)
    write_json(root / 'manifests/ASSETS_COMPLETE.json', {
        'status': 'PASS', 'source_revision': config['source_revision'],
        'tasks': len(descriptors), 'report': 'reports/storage_transfer.json'})
    print('REJOIN_CLOUD_PASS', 'images', len(descriptors), 'blobs', len(verified_blobs), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    persist(args.config, args.report)
