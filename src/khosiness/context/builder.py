from dataclasses import dataclass

from khosiness.state import RunState
from khosiness.task import Task


@dataclass
class ContextStats:
    messages: int
    characters: int


class ContextBuilder:
    """Select what the model sees for the next decision."""

    def __init__(
        self,
        max_recent_observations: int = 8,
        max_observation_chars: int = 8_000,
    ):
        for name, value in (
            ("max_recent_observations", max_recent_observations),
            ("max_observation_chars", max_observation_chars),
        ):
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")

        self.max_recent_observations = max_recent_observations
        self.max_observation_chars = max_observation_chars
        self.last_stats = ContextStats(messages=0, characters=0)

    def build(
        self,
        task: Task,
        state: RunState,
    ) -> list[dict]:
        recent = (
            state.observations[-self.max_recent_observations :]
            if self.max_recent_observations
            else []
        )

        rendered_observations = []
        for observation in recent:
            text = repr(observation)
            if len(text) > self.max_observation_chars:
                text = text[: self.max_observation_chars] + "... [truncated]"
            rendered_observations.append(text)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are operating inside a controlled harness. "
                    "Use tools to gather evidence. "
                    "Never invent tool results."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Objective: {task.objective}\n"
                    f"Constraints: {task.constraints}\n"
                    f"Success criteria: {task.success_criteria}\n"
                    f"Current step: {state.step}"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Recent observations:\n" + "\n".join(rendered_observations)
                ),
            },
        ]

        self.last_stats = ContextStats(
            messages=len(messages),
            characters=sum(len(message["content"]) for message in messages),
        )

        return messages
