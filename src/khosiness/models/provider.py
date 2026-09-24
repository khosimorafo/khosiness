from collections.abc import Callable

from .base import ModelResponse


class CallableProviderAdapter:
    """Convert a provider transport's dictionary to ModelResponse."""

    def __init__(
        self,
        transport: Callable[[list[dict], list[dict]], dict],
    ):
        self._transport = transport

    def generate(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> ModelResponse:
        raw = self._transport(messages, tools)
        return ModelResponse.model_validate(raw)
