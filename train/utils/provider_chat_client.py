from __future__ import annotations

import os
from typing import Any, Mapping, Sequence

import httpx


class ProviderChatClient:
    """Strict OpenAI-compatible chat client for provider-backed rollouts."""

    def __init__(
        self,
        *,
        model: str = "deepseek-v4-flash",
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = (
            base_url
            or os.environ.get(
                "STEPCODE_BASE_URL",
                "https://models-proxy.stepfun-inc.com",
            )
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("STEPCODE_API_KEY")
        if not self.api_key or not self.api_key.strip():
            raise RuntimeError("STEPCODE_API_KEY is required")
        self.timeout_seconds = timeout_seconds
        self.usage_records: list[dict[str, Any]] = []

    async def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        response_schema: Mapping[str, Any],
    ) -> str:
        payload = {
            "model": self.model,
            "messages": list(messages),
            # StepCode currently accepts json_object but rejects json_schema.
            # Response.model_validate_json() enforces the repository schema locally.
            "response_format": {"type": "json_object"},
            # The local loop executes JSON actions; request content-only output
            # even when prior messages contain native tool-call history.
            "tool_choice": "none",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        body = response.json()
        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("provider response must contain a non-empty choices list")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise ValueError("provider response choice must contain a message object")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("provider response message must contain non-empty content")
        usage = body.get("usage")
        if not isinstance(usage, dict):
            raise ValueError("provider response must contain a usage object")
        required_usage_fields = ("prompt_tokens", "completion_tokens", "total_tokens")
        for field in required_usage_fields:
            value = usage.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"provider response usage.{field} must be a non-negative integer"
                )
        self.usage_records.append(dict(usage))
        return content
