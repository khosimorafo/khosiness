from collections.abc import Callable

from .base import ModelResponse


class CallableProviderAdapter:
    """A thin adapter around any provider-specific transport function.

    The transport is responsible for talking to the provider SDK and returning
    a dictionary that conforms to ModelResponse. Keeping the SDK-specific
    conversion here prevents provider objects from leaking into the harness.
    """

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
