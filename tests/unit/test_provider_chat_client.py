from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "train"
    / "utils"
    / "provider_chat_client.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "provider_chat_client_under_test",
        MODULE_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload


class FakeAsyncClient:
    response = FakeResponse(
        200,
        {
            "choices": [{"message": {"content": '{"actions": [], "final_answer": 2}'}}],
            "usage": {
                "prompt_tokens": 11,
                "completion_tokens": 7,
                "total_tokens": 18,
                "completion_tokens_details": {"reasoning_tokens": 3},
            },
        },
    )
    requests: list[dict] = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args) -> None:
        return None

    async def post(self, url: str, **kwargs):
        type(self).requests.append({"url": url, **kwargs})
        return self.response


@pytest.mark.asyncio
async def test_provider_client_posts_schema_constrained_messages(monkeypatch) -> None:
    module = load_module()
    FakeAsyncClient.requests.clear()
    monkeypatch.setenv("STEPCODE_API_KEY", "test-key")
    monkeypatch.setenv("STEPCODE_BASE_URL", "https://provider.test")
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)

    client = module.ProviderChatClient(model="deepseek-v4-flash")
    messages = [
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": '{"actions": [{"tool": "preprocess", "inputs": ""}]}'},
        {"role": "tool", "content": "preprocessing completed"},
    ]
    response = await client.complete(messages, {"type": "object"})

    assert response == '{"actions": [], "final_answer": 2}'
    request = FakeAsyncClient.requests[-1]
    assert request["url"] == "https://provider.test/v1/chat/completions"
    assert request["json"]["model"] == "deepseek-v4-flash"
    assert request["json"]["messages"] == messages
    assert request["json"]["response_format"] == {"type": "json_object"}
    assert request["json"]["tool_choice"] == "none"
    assert client.usage_records == [
        {
            "prompt_tokens": 11,
            "completion_tokens": 7,
            "total_tokens": 18,
            "completion_tokens_details": {"reasoning_tokens": 3},
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "usage",
    [
        None,
        {"prompt_tokens": 1, "completion_tokens": 2},
        {"prompt_tokens": -1, "completion_tokens": 2, "total_tokens": 1},
        {"prompt_tokens": True, "completion_tokens": 2, "total_tokens": 3},
        {"prompt_tokens": 1, "completion_tokens": "2", "total_tokens": 3},
    ],
)
async def test_provider_client_fails_on_missing_or_malformed_usage(monkeypatch, usage) -> None:
    module = load_module()
    monkeypatch.setenv("STEPCODE_API_KEY", "test-key")
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.response = FakeResponse(
        200,
        {
            "choices": [{"message": {"content": '{"actions": [], "final_answer": 2}'}}],
            "usage": usage,
        },
    )

    client = module.ProviderChatClient()
    with pytest.raises(ValueError, match="usage"):
        await client.complete([], {"type": "object"})


@pytest.mark.asyncio
async def test_provider_client_fails_on_malformed_success_response(monkeypatch) -> None:
    module = load_module()
    monkeypatch.setenv("STEPCODE_API_KEY", "test-key")
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.response = FakeResponse(200, {"choices": []})

    client = module.ProviderChatClient()
    with pytest.raises(ValueError, match="choices"):
        await client.complete([], {"type": "object"})


@pytest.mark.asyncio
async def test_provider_client_fails_before_request_without_key(monkeypatch) -> None:
    module = load_module()
    monkeypatch.delenv("STEPCODE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="STEPCODE_API_KEY is required"):
        module.ProviderChatClient()
