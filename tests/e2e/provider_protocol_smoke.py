"""Value-free protocol smoke for the StepCode OpenAI-compatible endpoint."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "thought": {"type": "string"},
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "tool": {"type": "string"},
                    "inputs": {"type": "string"},
                },
                "required": ["tool", "inputs"],
            },
        },
        "final_answer": {"type": ["integer", "null"]},
    },
    "required": ["thought", "actions", "final_answer"],
}


def request_json(
    url: str,
    *,
    api_key: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as error:
        raw = error.read()
        try:
            body_obj = json.loads(raw)
        except json.JSONDecodeError:
            body_obj = {"error_type": "non_json"}
        raise RuntimeError(f"HTTP {error.code} for {url}: {body_obj.get('error', body_obj.get('error_type'))}") from error
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"non-JSON response from {url}") from error
    if not isinstance(parsed, dict):
        raise RuntimeError(f"JSON response from {url} is not an object")
    return status, parsed


def completion_payload(
    messages: list[dict[str, Any]],
    response_format: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": "deepseek-v4-flash",
        "messages": messages,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    return payload


def json_schema_format() -> dict[str, Any]:
    return {
            "type": "json_schema",
            "json_schema": {
                "name": "agent_response",
                "strict": True,
                "schema": SCHEMA,
            }
    }


def json_object_format() -> dict[str, str]:
    return {"type": "json_object"}


def extract_content(body: dict[str, Any]) -> str:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("completion response has no choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("completion response has no message object")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("completion response has no non-empty content")
    return content


def main() -> int:
    api_key = os.environ.get("STEPCODE_API_KEY", "")
    base_url = os.environ.get("STEPCODE_BASE_URL", "https://models-proxy.stepfun-inc.com").rstrip("/")
    if not api_key.strip():
        raise RuntimeError("STEPCODE_API_KEY is required")

    model_status, models_body = request_json(f"{base_url}/v1/models", api_key=api_key)
    model_ids = {
        item.get("id")
        for item in models_body.get("data", [])
        if isinstance(item, dict)
    }
    if "deepseek-v4-flash" not in model_ids:
        raise RuntimeError("deepseek-v4-flash is absent from /v1/models")

    first_messages = [
        {
            "role": "user",
            "content": "Return a json response with final_answer set to 0 and no actions.",
        }
    ]
    response_format_name = os.environ.get("STEPCODE_RESPONSE_FORMAT", "json_schema")
    if response_format_name == "json_schema":
        response_format = json_schema_format()
    elif response_format_name == "json_object":
        response_format = json_object_format()
    elif response_format_name == "none":
        response_format = None
    else:
        raise RuntimeError(f"unsupported STEPCODE_RESPONSE_FORMAT={response_format_name}")

    first_status, first_body = request_json(
        f"{base_url}/v1/chat/completions",
        api_key=api_key,
        payload=completion_payload(first_messages, response_format),
    )
    first_content = extract_content(first_body)
    try:
        first_json = json.loads(first_content)
    except json.JSONDecodeError as error:
        raise RuntimeError("structured completion content is not JSON") from error
    if not isinstance(first_json, dict):
        raise RuntimeError("structured completion content is not an object")

    tool_messages = [
        {
            "role": "user",
            "content": "Use the tool result and return a json final answer.",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "thought": "I need the local tool result.",
                    "actions": [{"tool": "probe", "inputs": "{}"}],
                    "final_answer": None,
                }
            ),
            "tool_calls": [
                {
                    "id": "probe-call-1",
                    "type": "function",
                    "function": {
                        "name": "probe",
                        "arguments": "{}",
                    },
                }
            ],
        },
        {
            "role": "tool",
            "name": "probe",
            "tool_call_id": "probe-call-1",
            "content": "local-result",
        },
    ]
    tool_status, tool_body = request_json(
        f"{base_url}/v1/chat/completions",
        api_key=api_key,
        payload=completion_payload(tool_messages, response_format),
    )
    tool_content = extract_content(tool_body)
    try:
        json.loads(tool_content)
    except json.JSONDecodeError as error:
        raise RuntimeError("tool-turn completion content is not JSON") from error

    print(f"base_url={base_url}")
    print(f"response_format={response_format_name}")
    print(f"models_http_status={model_status}")
    print("model_present=PASS")
    print(f"structured_json_http_status={first_status}")
    print("structured_json_content=PASS")
    print(f"tool_turn_http_status={tool_status}")
    print("tool_role_round_trip=PASS")
    print("provider_tool_execution_observed=NO")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"provider_protocol_smoke=FAIL: {error}", file=sys.stderr)
        raise
