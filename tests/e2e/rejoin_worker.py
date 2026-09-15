#!/usr/bin/env python3
"""Submit one ReJoin job through the local personal StepMind Python backend."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import socket
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.source.resolve().is_relative_to('/data/ycfeng') or not args.command:
        raise ValueError('A local task source and worker command are required')
    credentials = Path('/data/ycfeng/tmp/brainctl-auth-i-fengyicheng')
    os.environ['BRAINPP_ACCESS_KEY'] = (credentials / 'accesskey_id').read_text().strip()
    os.environ['BRAINPP_SECRET_KEY'] = (credentials / 'accesskey_secret').read_text().strip()
    os.environ['STEPMIND_BACKEND'] = 'rjob'
    os.environ['EXP_ID'] = 'rejoin-p04'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.path.insert(0, '/data/ycfeng/steptron')
    from steptron.exp.base_exp import ResourceConfig
    from steptron.utils.stepmind import get_rjob_client, spawn_tasks

    os.chdir(args.source)
    envs = {key: value for key, value in os.environ.items()
            if key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY',
                       'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy')}
    envs['PYTHONDONTWRITEBYTECODE'] = '1'
    envs['NVIDIA_DRIVER_CAPABILITIES'] = 'compute,utility'
    cfg = ResourceConfig(cpu=4, gpu=1, mem_gb=16, replica=1, image=args.image,
                         mounts=['juicefs+s3://oss.i.shaipower.com/codesign-exp:/mnt/codesign-exp'],
                         positive_tags=['H200'], extra_requirements=[], custom_resources=[],
                         envs=envs, command='{COMMAND}', pull_code=False, host_network=True,
                         task_specs={'default': {'is_critical': True}}, auto_port_num=0,
                         i_know_i_am_wasting_resource=True)
    command = args.command[1:] if args.command[0] == '--' else args.command
    workers = spawn_tasks(cfg, command=shlex.join(command), charged_group='step_main',
                          use_image=True, code_mount_point=str(args.source))
    name = workers.rjob.meta.name
    client = get_rjob_client()
    job = client.api.get_namespaced_custom_object(
        group=client.group, version=client.version, namespace=client.namespace,
        plural=client.plural, name=name, _request_timeout=25)
    creator = job['metadata']['labels'].get('kubebrain.brainpp.cn/creator')
    mounts = {key: task['template']['metadata'].get('annotations', {}).get(
        'kubebrain.brainpp.cn/filestore-volume') for key, task in job['spec']['taskSpecs'].items()}
    expected_mount = f'{socket.gethostbyname(socket.gethostname())}:{args.source}:{args.source}'
    if creator != 'i-fengyicheng' or any(value != expected_mount for value in mounts.values()):
        raise ValueError('Created job identity or local NFS source differs from the request')
    record = {'job': name, 'creator': creator, 'image': args.image, 'mounts': mounts,
              'worker_status': str(workers.poll()), 'platform_status': job.get('status', {}),
              'quota': 'step_main', 'gpu': 'H200', 'command': command}
    args.report.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
    if record['worker_status'] != 'succeeded':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
