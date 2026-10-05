from pydantic import BaseModel, Field


class RunState(BaseModel):
    """Current progress of one harness run."""

    run_id: str
    step: int = 0
    observations: list[dict] = Field(default_factory=list)
    finished: bool = False
    final_answer: str | None = None
