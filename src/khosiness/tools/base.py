from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    ok: bool
    content: str
    metadata: dict = Field(default_factory=dict)


class Tool(ABC):
    name: str
    description: str
    risk: str = "read_only"

    @abstractmethod
    def schema(self) -> dict: ...

    @abstractmethod
    def execute(self, arguments: dict) -> ToolResult: ...
