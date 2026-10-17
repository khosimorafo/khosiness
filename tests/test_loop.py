from pathlib import Path

from pydantic import BaseModel

from khosiness.event_store import JsonlEventStore
from khosiness.loop import run
from khosiness.models.base import ModelResponse, ToolCall
from khosiness.models.fake import FakeModel
from khosiness.state import RunState
from khosiness.task import Task


class MinimalContext:
    """Show the model the task and the latest tool observation."""

    def build(self, task: Task, state: RunState) -> list[dict]:
        messages = [{"role": "user", "content": task.objective}]
        if state.observations:
            messages.append(
                {
                    "role": "tool",
                    "content": state.observations[-1]["result"]["content"],
                }
            )
        return messages


class FakeToolResult(BaseModel):
    ok: bool
    content: str


class FakeTools:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.calls: list[ToolCall] = []

    def schemas(self) -> list[dict]:
        return [{"name": "echo"}]

    def execute(self, call: ToolCall) -> FakeToolResult:
        self.calls.append(call)
        if self.fail:
            return FakeToolResult(ok=False, content="echo failed")
        return FakeToolResult(ok=True, content=call.arguments["text"])


def make_task(tmp_path: Path, max_steps: int = 5) -> Task:
    return Task(
        id="task-1",
        objective="Use echo, then finish",
        workspace=tmp_path,
        max_steps=max_steps,
    )


def test_loop_executes_tool_then_finishes(tmp_path: Path) -> None:
    model = FakeModel(
        [
            ModelResponse(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelResponse(text="finished"),
        ]
    )
    tools = FakeTools()
    events = JsonlEventStore(tmp_path / "events.jsonl")
    checkpoints: list[RunState] = []

    result = run(
        task=make_task(tmp_path),
        state=RunState(run_id="run-1"),
        model=model,
        context_builder=MinimalContext(),
        tools=tools,
        events=events,
        save_state=lambda current: checkpoints.append(current.model_copy(deep=True)),
    )

    assert result.step == 2
    assert result.finished is True
    assert result.final_answer == "finished"
    assert len(tools.calls) == 1
    assert result.observations[0]["result"]["content"] == "hello"
    assert model.calls[1]["messages"][-1] == {
        "role": "tool",
        "content": "hello",
    }
    assert [event.type for event in events.load_all()] == [
        "model_called",
        "model_responded",
        "tool_requested",
        "tool_completed",
        "model_called",
        "model_responded",
        "task_completed",
    ]
    assert [(state.step, state.finished) for state in checkpoints] == [
        (1, False),
        (2, True),
    ]


def test_loop_stops_on_first_final_answer(tmp_path: Path) -> None:
    model = FakeModel([ModelResponse(text="done")])
    tools = FakeTools()
    events = JsonlEventStore(tmp_path / "events.jsonl")
    checkpoints: list[RunState] = []

    result = run(
        task=make_task(tmp_path),
        state=RunState(run_id="run-1"),
        model=model,
        context_builder=MinimalContext(),
        tools=tools,
        events=events,
        save_state=lambda current: checkpoints.append(current.model_copy(deep=True)),
    )

    assert result.step == 1
    assert result.finished is True
    assert result.final_answer == "done"
    assert result.observations == []
    assert tools.calls == []
    assert len(model.calls) == 1
    assert [(state.step, state.finished) for state in checkpoints] == [
        (1, True),
    ]
    assert [event.type for event in events.load_all()] == [
        "model_called",
        "model_responded",
        "task_completed",
    ]


def test_loop_obeys_step_limit(tmp_path: Path) -> None:
    model = FakeModel(
        [
            ModelResponse(
                tool_calls=[
                    ToolCall(
                        id=str(index),
                        name="echo",
                        arguments={"text": "again"},
                    )
                ]
            )
            for index in range(3)
        ]
    )
    tools = FakeTools()
    events = JsonlEventStore(tmp_path / "events.jsonl")
    checkpoints: list[RunState] = []

    result = run(
        task=make_task(tmp_path, max_steps=2),
        state=RunState(run_id="run-1"),
        model=model,
        context_builder=MinimalContext(),
        tools=tools,
        events=events,
        save_state=lambda current: checkpoints.append(current.model_copy(deep=True)),
    )

    assert result.step == 2
    assert result.finished is False
    assert result.final_answer is None
    assert len(model.calls) == 2
    assert len(model.responses) == 1
    assert len(tools.calls) == 2
    assert len(result.observations) == 2
    assert [state.step for state in checkpoints] == [1, 2]
    assert [event.type for event in events.load_all()] == [
        "model_called",
        "model_responded",
        "tool_requested",
        "tool_completed",
        "model_called",
        "model_responded",
        "tool_requested",
        "tool_completed",
        "step_limit_reached",
    ]


def test_tool_failure_becomes_observation(tmp_path: Path) -> None:
    model = FakeModel(
        [
            ModelResponse(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelResponse(text="The echo tool failed"),
        ]
    )
    tools = FakeTools(fail=True)
    events = JsonlEventStore(tmp_path / "events.jsonl")

    result = run(
        task=make_task(tmp_path),
        state=RunState(run_id="run-1"),
        model=model,
        context_builder=MinimalContext(),
        tools=tools,
        events=events,
    )

    assert result.step == 2
    assert result.observations[0]["result"] == {
        "ok": False,
        "content": "echo failed",
    }
    assert model.calls[1]["messages"][-1] == {
        "role": "tool",
        "content": "echo failed",
    }
    assert result.final_answer == "The echo tool failed"
    assert [event.type for event in events.load_all()] == [
        "model_called",
        "model_responded",
        "tool_requested",
        "tool_failed",
        "model_called",
        "model_responded",
        "task_completed",
    ]
