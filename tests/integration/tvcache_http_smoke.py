#!/usr/bin/env python3
"""Run a minimal, reproducible HTTP smoke check against a TVCache server."""

from __future__ import annotations

import argparse
import os
import time
from typing import Any

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("TVCACHE_BASE_URL", "http://127.0.0.1:18001"),
        help="TVCache server URL (default: TVCACHE_BASE_URL or 18001)",
    )
    parser.add_argument(
        "--task-name",
        default=f"manual-smoke-{int(time.time())}",
        help="Unique task name used for this run",
    )
    return parser.parse_args()


def request_json(response: requests.Response, expected_status: int) -> Any:
    if response.status_code != expected_status:
        raise RuntimeError(
            f"unexpected HTTP status {response.status_code} (expected {expected_status}): "
            f"{response.text[:500]}"
        )
    return response.json()


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    task_name = args.task_name
    history = ["manual_call_a", "manual_call_b"]
    values = ["manual_value_a", "manual_value_b"]
    exec_times = [0.125, 0.25]
    query = [("task_name", task_name)] + [("tool_calls", item) for item in history]

    with requests.Session() as session:
        before = request_json(session.get(f"{base_url}/get", params=query, timeout=10), 200)
        if before.get("found") is not False:
            raise AssertionError(f"expected an initial miss, got {before}")

        put_payload = {
            "task_name": task_name,
            "history": history,
            "env_id": f"env-{task_name}",
            "values": values,
            "tool_exec_times": exec_times,
            "start_idx": 0,
        }
        put = request_json(session.put(f"{base_url}/put", json=put_payload, timeout=10), 200)
        if put.get("success") is not True:
            raise AssertionError(f"PUT did not report success: {put}")

        exact = request_json(session.get(f"{base_url}/get", params=query, timeout=10), 200)
        if (
            exact.get("found") is not True
            or exact.get("env_id") != put_payload["env_id"]
            or exact.get("value") != values[-1]
            or exact.get("tool_exec_time") != exec_times[-1]
        ):
            raise AssertionError(f"exact lookup mismatch: {exact}")

        prefix = request_json(
            session.post(
                f"{base_url}/prefix_match",
                json={"task_name": task_name, "tool_calls": [*history, "manual_call_c"]},
                timeout=10,
            ),
            200,
        )
        if prefix.get("found") is not True or prefix.get("env_id") != put_payload["env_id"]:
            raise AssertionError(f"prefix lookup mismatch: {prefix}")
        if prefix.get("history") != history:
            raise AssertionError(f"prefix history mismatch: {prefix}")

        visualize = request_json(session.get(f"{base_url}/visualize", timeout=10), 200)
        node = visualize[task_name]["children"][history[0]]["children"][history[1]]
        if node.get("cache_hits", 0) < 1 or node.get("prefix_hits", 0) < 1:
            raise AssertionError(f"expected hit counters in visualize output: {node}")

        all_envs = request_json(
            session.get(f"{base_url}/get_all_envs", params={"task_name": task_name}, timeout=10),
            200,
        )
        if put_payload["env_id"] not in all_envs.get("env_ids", []):
            raise AssertionError(f"environment missing from get_all_envs: {all_envs}")

    print(f"base_url={base_url}")
    print(f"task_name={task_name}")
    print("initial_found=False")
    print("put_success=True")
    print(f"exact_env_id={exact['env_id']}")
    print(f"exact_value={exact['value']}")
    print(f"exact_tool_exec_time={exact['tool_exec_time']}")
    print(f"prefix_history_len={len(prefix['history'])}")
    print(f"cache_hits={node['cache_hits']}")
    print(f"prefix_hits={node['prefix_hits']}")
    print(f"all_env_count={len(all_envs['env_ids'])}")
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
