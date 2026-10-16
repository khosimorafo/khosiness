from typing import Protocol

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict


class ModelResponse(BaseModel):
    text: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    stop_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class ModelAdapter(Protocol):
    def generate(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> ModelResponse:
        """Return a provider-neutral model response."""
        ...
