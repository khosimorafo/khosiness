from collections import deque

from .base import ModelResponse


class FakeModel:
    """Deterministic model adapter for unit tests."""

    def __init__(self, responses: list[ModelResponse]):
        self.responses = deque(responses)
        self.calls: list[dict] = []

    def generate(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> ModelResponse:
        self.calls.append({"messages": messages, "tools": tools})

        if not self.responses:
            raise RuntimeError("FakeModel has no queued response")

        return self.responses.popleft()
