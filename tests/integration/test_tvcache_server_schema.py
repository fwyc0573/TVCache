from __future__ import annotations

import sys
from pathlib import Path


SERVER_ROOT = Path(__file__).resolve().parents[2] / "tvcache" / "server"
sys.path.insert(0, str(SERVER_ROOT))

import tvcache_server


def test_put_and_get_use_current_server_schema() -> None:
    client = tvcache_server.app.test_client()

    try:
        put_response = client.put(
            "/put",
            json={
                "task_name": "schema-test",
                "history": ["prepare", "query"],
                "env_id": "environment-1",
                "values": ["prepared", "answer"],
                "tool_exec_times": [0.125, 0.25],
                "start_idx": 0,
            },
        )

        assert put_response.status_code == 200, put_response.get_data(
            as_text=True
        )
        assert put_response.get_json() == {
            "success": True,
            "removed_env_ids": [],
        }

        get_response = client.get(
            "/get",
            query_string=[
                ("task_name", "schema-test"),
                ("tool_calls", "prepare"),
                ("tool_calls", "query"),
            ],
        )

        assert get_response.status_code == 200, get_response.get_data(
            as_text=True
        )
        assert get_response.get_json() == {
            "found": True,
            "env_id": "environment-1",
            "value": "answer",
            "tool_exec_time": 0.25,
        }
    finally:
        tvcache_server.cache.ttl_cleanup_stop_event.set()
        tvcache_server.cache.ttl_cleanup_thread.join(timeout=1)


def test_server_defaults_use_task_loopback_and_port(
    monkeypatch,
) -> None:
    run_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        tvcache_server.app,
        "run",
        lambda **kwargs: run_calls.append(kwargs),
    )

    tvcache_server.run_server()

    assert run_calls == [
        {
            "host": "127.0.0.1",
            "port": 8001,
            "debug": False,
            "threaded": True,
        }
    ]


def test_drain_task_detaches_and_returns_cached_environments() -> None:
    client = tvcache_server.app.test_client()

    try:
        for history, env_id in [
            (["prepare"], "drain-environment-1"),
            (["inspect"], "drain-environment-2"),
        ]:
            put_response = client.put(
                "/put",
                json={
                    "task_name": "drain-schema-test",
                    "history": history,
                    "env_id": env_id,
                    "values": [history[0]],
                    "tool_exec_times": [0.1],
                    "start_idx": 0,
                },
            )
            assert put_response.status_code == 200

        drain_response = client.post(
            "/drain_task",
            json={
                "task_name": "drain-schema-test",
                "drain_id": "drain-schema-operation",
            },
        )

        assert drain_response.status_code == 200, (
            drain_response.get_data(as_text=True)
        )
        assert drain_response.get_json() == {
            "success": True,
            "drain_id": "drain-schema-operation",
            "env_ids": [
                "drain-environment-1",
                "drain-environment-2",
            ],
        }
        replay_response = client.post(
            "/drain_task",
            json={
                "task_name": "drain-schema-test",
                "drain_id": "drain-schema-operation",
            },
        )
        assert replay_response.status_code == 200
        assert replay_response.get_json() == drain_response.get_json()
        assert (
            tvcache_server.cache.prefix_tree_env_count[
                "drain-schema-test"
            ]
            == 0
        )
        assert client.get(
            "/get",
            query_string=[
                ("task_name", "drain-schema-test"),
                ("tool_calls", "prepare"),
            ],
        ).get_json()["found"] is False

        ack_response = client.post(
            "/ack_task_drain",
            json={
                "task_name": "drain-schema-test",
                "drain_id": "drain-schema-operation",
            },
        )
        assert ack_response.status_code == 200
        assert ack_response.get_json() == {
            "success": True,
            "drain_id": "drain-schema-operation",
        }
        repeated_ack_response = client.post(
            "/ack_task_drain",
            json={
                "task_name": "drain-schema-test",
                "drain_id": "drain-schema-operation",
            },
        )
        assert repeated_ack_response.status_code == 200
        assert repeated_ack_response.get_json() == ack_response.get_json()
    finally:
        tvcache_server.cache.ttl_cleanup_stop_event.set()
        tvcache_server.cache.ttl_cleanup_thread.join(timeout=1)
