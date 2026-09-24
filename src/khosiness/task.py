from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    """A bounded unit of work executed by the harness."""

    id: str
    objective: str
    workspace: Path
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    max_steps: int = 30

    @field_validator("objective")
    @classmethod
    def objective_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("objective must not be blank")
        return value

    @field_validator("workspace")
    @classmethod
    def workspace_must_exist(cls, value: Path) -> Path:
        value = value.expanduser().resolve()
        if not value.exists():
            raise ValueError(f"workspace does not exist: {value}")
        if not value.is_dir():
            raise ValueError(f"workspace is not a directory: {value}")
        return value

    @field_validator("max_steps")
    @classmethod
    def max_steps_must_be_positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("max_steps must be >= 1")
        return value