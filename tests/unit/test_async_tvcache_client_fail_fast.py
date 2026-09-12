from __future__ import annotations

import json

import httpx
import pytest

from tvclient.utils.async_tvcache_client import AsyncTVCacheClient


def _server_error_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            json={"error": "cache server failed"},
            request=request,
        )

    return httpx.MockTransport(handler)


def _malformed_success_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json={}, request=request)

    return httpx.MockTransport(handler)


def _json_transport(payload: dict[str, object]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json=payload, request=request)

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_exact_match_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.exact_match("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_prefix_match_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.prefix_match("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_get_test_result_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_test_result("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_unref_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.unref("environment-1", "task")

    await client.close()


@pytest.mark.asyncio
async def test_get_all_envs_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_all_envs("task")

    await client.close()


@pytest.mark.asyncio
async def test_get_test_result_raises_on_missing_found_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_malformed_success_transport())

    with pytest.raises(KeyError, match="found"):
        await client.get_test_result("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_unref_raises_on_missing_success_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_malformed_success_transport())

    with pytest.raises(KeyError, match="success"):
        await client.unref("environment-1", "task")

    await client.close()


@pytest.mark.asyncio
async def test_get_all_envs_raises_on_missing_env_ids_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_malformed_success_transport())

    with pytest.raises(KeyError, match="env_ids"):
        await client.get_all_envs("task")

    await client.close()


@pytest.mark.asyncio
async def test_exact_match_raises_on_missing_found_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_malformed_success_transport()
    )

    with pytest.raises(KeyError, match="found"):
        await client.exact_match("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_prefix_match_raises_on_missing_found_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_malformed_success_transport()
    )

    with pytest.raises(KeyError, match="found"):
        await client.prefix_match("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_put_raises_on_missing_success_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_malformed_success_transport()
    )

    with pytest.raises(KeyError, match="success"):
        await client.put(
            "task",
            ["tool"],
            "environment-1",
            ["value"],
            [0.5],
        )

    await client.close()


@pytest.mark.asyncio
async def test_exact_match_rejects_non_boolean_found_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "found": 1,
                "env_id": None,
                "value": None,
                "tool_exec_time": None,
            }
        )
    )

    with pytest.raises(TypeError, match="found"):
        await client.exact_match("task", ["tool"])

    await client.close()


@pytest.mark.asyncio
async def test_prefix_match_rejects_non_string_environment_id() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "found": True,
                "env_id": 7,
                "history": ["tool"],
            }
        )
    )

    with pytest.raises(TypeError, match="env_id"):
        await client.prefix_match("task", ["tool", "suffix"])

    await client.close()


@pytest.mark.asyncio
async def test_prefix_match_rejects_non_string_history_item() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "found": True,
                "env_id": "environment-1",
                "history": ["tool", 7],
            }
        )
    )

    with pytest.raises(TypeError, match="history"):
        await client.prefix_match("task", ["tool", "suffix"])

    await client.close()


@pytest.mark.asyncio
async def test_put_rejects_non_list_removed_environment_ids() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "success": True,
                "removed_env_ids": "environment-1",
            }
        )
    )

    with pytest.raises(TypeError, match="removed_env_ids"):
        await client.put(
            "task",
            ["tool"],
            "environment-1",
            ["value"],
            [0.5],
        )

    await client.close()


@pytest.mark.asyncio
async def test_put_raises_when_server_rejects_publication() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "success": False,
                "removed_env_ids": [],
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="rejected cache publication",
    ):
        await client.put(
            "task",
            ["tool"],
            "environment-1",
            ["value"],
            [0.5],
        )

    await client.close()


@pytest.mark.asyncio
async def test_drain_task_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.drain_task("task", "drain-1")

    await client.close()


@pytest.mark.asyncio
async def test_drain_task_raises_on_missing_success_field() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_malformed_success_transport()
    )

    with pytest.raises(KeyError, match="success"):
        await client.drain_task("task", "drain-1")

    await client.close()


@pytest.mark.asyncio
async def test_drain_task_rejects_non_list_environment_ids() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "success": True,
                "drain_id": "drain-1",
                "env_ids": "environment-1",
            }
        )
    )

    with pytest.raises(TypeError, match="env_ids"):
        await client.drain_task("task", "drain-1")

    await client.close()


@pytest.mark.asyncio
async def test_drain_task_returns_detached_environment_ids() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "success": True,
                "drain_id": "drain-1",
                "env_ids": ["environment-1", "environment-2"],
            }
        )
    )

    assert await client.drain_task("task", "drain-1") == [
        "environment-1",
        "environment-2",
    ]

    await client.close()


@pytest.mark.asyncio
async def test_drain_task_sends_and_validates_stable_drain_id() -> None:
    requests: list[tuple[str, dict[str, str]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        requests.append((request.url.path, payload))
        return httpx.Response(
            status_code=200,
            json={
                "success": True,
                "drain_id": payload["drain_id"],
                "env_ids": ["environment-1"],
            },
            request=request,
        )

    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )

    assert await client.drain_task("task", "drain-1") == [
        "environment-1",
    ]
    assert requests == [
        (
            "/drain_task",
            {
                "task_name": "task",
                "drain_id": "drain-1",
            },
        ),
    ]

    await client.close()


@pytest.mark.asyncio
async def test_drain_task_rejects_mismatched_drain_id() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=_json_transport(
            {
                "success": True,
                "drain_id": "different-drain",
                "env_ids": ["environment-1"],
            }
        )
    )

    with pytest.raises(RuntimeError, match="drain_id"):
        await client.drain_task("task", "drain-1")

    await client.close()


@pytest.mark.asyncio
async def test_ack_task_drain_sends_and_validates_drain_id() -> None:
    requests: list[tuple[str, dict[str, str]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        requests.append((request.url.path, payload))
        return httpx.Response(
            status_code=200,
            json={
                "success": True,
                "drain_id": payload["drain_id"],
            },
            request=request,
        )

    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )

    await client.ack_task_drain("task", "drain-1")

    assert requests == [
        (
            "/ack_task_drain",
            {
                "task_name": "task",
                "drain_id": "drain-1",
            },
        ),
    ]

    await client.close()


@pytest.mark.asyncio
async def test_ack_task_drain_raises_on_cache_server_error() -> None:
    client = AsyncTVCacheClient(base_url="http://cache.test")
    client._client = httpx.AsyncClient(transport=_server_error_transport())

    with pytest.raises(httpx.HTTPStatusError):
        await client.ack_task_drain("task", "drain-1")

    await client.close()
