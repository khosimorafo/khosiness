from khosiness.models.base import ToolCall

from .base import Tool, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict]:
        return [tool.schema() for tool in self._tools.values()]

    def execute(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)

        if tool is None:
            return ToolResult(
                ok=False,
                content=f"Unknown tool: {call.name}",
            )

        try:
            return tool.execute(call.arguments)
        except Exception as exc:
            return ToolResult(
                ok=False,
                content=f"{type(exc).__name__}: {exc}",
            )
