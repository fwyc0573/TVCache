from __future__ import annotations

import httpx
import pytest

from utils.video_sandbox_client import SandboxClient


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self.response = httpx.Response(
            status_code=500,
            json={"error": "sandbox failed"},
            request=httpx.Request("POST", "http://sandbox.test/execute"),
        )

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def post(self, url: str, json: dict) -> httpx.Response:
        return self.response


@pytest.mark.asyncio
async def test_sandbox_client_raises_on_server_error(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    client = SandboxClient(base_url="http://sandbox.test")

    with pytest.raises(httpx.HTTPStatusError):
        await client.start_sandbox("sandbox-1")


@pytest.mark.asyncio
async def test_sandbox_client_sends_stop_operation_id(monkeypatch) -> None:
    requests: list[tuple[str, dict[str, str]]] = []

    class RecordingAsyncClient:
        def __init__(self, *args, **kwargs):
            return None

        async def __aenter__(self) -> "RecordingAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ) -> None:
            return None

        async def post(
            self,
            url: str,
            json: dict[str, str],
        ) -> httpx.Response:
            requests.append((url, json))
            return httpx.Response(
                status_code=200,
                json={
                    "success": True,
                    "sandbox_id": json["sandbox_id"],
                    "operation_id": json["operation_id"],
                },
                request=httpx.Request("POST", url),
            )

    monkeypatch.setattr(httpx, "AsyncClient", RecordingAsyncClient)
    client = SandboxClient(base_url="http://sandbox.test")

    response = await client.stop_sandbox(
        "sandbox-1",
        operation_id="stop-operation-1",
    )

    assert requests == [
        (
            "http://sandbox.test/stop",
            {
                "sandbox_id": "sandbox-1",
                "operation_id": "stop-operation-1",
            },
        ),
    ]
    assert response == {
        "success": True,
        "sandbox_id": "sandbox-1",
        "operation_id": "stop-operation-1",
    }


@pytest.mark.asyncio
async def test_sandbox_client_reuses_generated_stop_operation_id(
    monkeypatch,
) -> None:
    requests: list[dict[str, str]] = []

    class RecordingAsyncClient:
        def __init__(self, *args, **kwargs):
            return None

        async def __aenter__(self) -> "RecordingAsyncClient":
            return self

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ) -> None:
            return None

        async def post(
            self,
            url: str,
            json: dict[str, str],
        ) -> httpx.Response:
            requests.append(json)
            return httpx.Response(
                status_code=200,
                json={
                    "success": True,
                    "sandbox_id": json["sandbox_id"],
                    "operation_id": json["operation_id"],
                },
                request=httpx.Request("POST", url),
            )

    monkeypatch.setattr(httpx, "AsyncClient", RecordingAsyncClient)
    client = SandboxClient(base_url="http://sandbox.test")

    await client.stop_sandbox("sandbox-1")
    await client.stop_sandbox("sandbox-1")

    assert len(requests) == 2
    assert requests[0]["operation_id"]
    assert requests[0]["operation_id"] == requests[1]["operation_id"]
