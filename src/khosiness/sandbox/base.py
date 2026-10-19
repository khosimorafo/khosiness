from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExecRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    argv: list[str] = Field(min_length=1)
    cwd: Path
    timeout_seconds: int = Field(default=20, ge=1, le=120)

    @field_validator("argv")
    @classmethod
    def validate_argv(cls, value: list[str]) -> list[str]:
        if not value[0]:
            raise ValueError("executable must not be empty")
        if any("\x00" in argument for argument in value):
            raise ValueError("arguments must not contain NUL")
        return value


class ExecResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = Field(ge=0)
    timed_out: bool = False
    metadata: dict = Field(default_factory=dict)


class Sandbox(Protocol):
    def execute(self, request: ExecRequest) -> ExecResult: ...
