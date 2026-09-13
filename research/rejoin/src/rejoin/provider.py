"""Provider interfaces reserved for P04; P02 uses a scripted action list."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence


class CompletionProvider(Protocol):
    def complete(self, messages: Sequence[Mapping[str, Any]]) -> str:
        ...


class ScriptedProvider:
    """Deterministic placeholder that keeps P02 independent from API credentials."""

    def __init__(self, response: str = "scripted") -> None:
        self.response = response

    def complete(self, messages: Sequence[Mapping[str, Any]]) -> str:
        return self.response
