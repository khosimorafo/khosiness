from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from khosiness.sandbox.base import ExecRequest, Sandbox

from .base import Tool, ToolResult


class ShellArguments(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    argv: list[str] = Field(min_length=1)
    cwd: str = Field(default=".", min_length=1)
    timeout_seconds: int = Field(default=20, ge=1, le=120)


class ShellTool(Tool):
    name = "shell"
    description = (
        "Execute a configured absolute executable through the runtime. "
        "cwd defaults to the workspace; timeout_seconds is 1–120."
    )
    risk = "process_execution"

    def __init__(self, workspace: Path, sandbox: Sandbox):
        self.workspace = workspace.resolve(strict=True)
        self.sandbox = sandbox

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": ShellArguments.model_json_schema(),
        }

    def execute(self, arguments: dict) -> ToolResult:
        args = ShellArguments.model_validate(arguments)

        request = ExecRequest(
            argv=args.argv,
            cwd=self.workspace / args.cwd,
            timeout_seconds=args.timeout_seconds,
        )
        result = self.sandbox.execute(request)

        return ToolResult(
            ok=not result.timed_out and result.exit_code == 0,
            content=(
                f"exit_code={result.exit_code}\n"
                f"timed_out={result.timed_out}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            ),
            metadata=result.model_dump(),
        )
