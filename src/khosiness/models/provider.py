from collections.abc import Callable

from .base import ModelResponse


class CallableProviderAdapter:
    """Wrap a transport that returns a provider-neutral dictionary."""

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
