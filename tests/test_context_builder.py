import pytest

from khosiness.context.builder import ContextBuilder
from khosiness.state import RunState
from khosiness.task import Task


def make_task(tmp_path):
    return Task(
        id="t1",
        objective="Find retry configuration",
        workspace=tmp_path,
        constraints=["Do not modify files"],
        success_criteria=["Name the defining file"],
    )


def test_context_always_contains_task_and_constraints(tmp_path):
    builder = ContextBuilder()
    task = make_task(tmp_path)
    state = RunState(run_id="r1", step=3)

    messages = builder.build(task, state)
    joined = "\n".join(message["content"] for message in messages)

    assert "Find retry configuration" in joined
    assert "Do not modify files" in joined
    assert "Name the defining file" in joined
    assert "Current step: 3" in joined
    assert builder.build(task, state) == messages


def test_context_keeps_only_recent_observations(tmp_path):
    state = RunState(
        run_id="r1",
        observations=[
            {"value": "old"},
            {"value": "middle"},
            {"value": "recent"},
        ],
    )
    before = state.model_copy(deep=True)
    builder = ContextBuilder(max_recent_observations=2)

    messages = builder.build(make_task(tmp_path), state)
    content = messages[-1]["content"]

    assert "old" not in content
    assert "middle" in content
    assert "recent" in content
    assert state == before


def test_large_observation_is_truncated(tmp_path):
    observation = {"value": "x" * 1000}
    state = RunState(run_id="r1", observations=[observation])
    before = state.model_copy(deep=True)
    builder = ContextBuilder(max_observation_chars=100)

    messages = builder.build(make_task(tmp_path), state)

    expected = repr(observation)[:100] + "... [truncated]"
    assert messages[-1]["content"] == "Recent observations:\n" + expected
    assert state == before


def test_context_stats_are_recorded(tmp_path):
    builder = ContextBuilder()
    messages = builder.build(
        make_task(tmp_path),
        RunState(run_id="r1"),
    )

    assert builder.last_stats.messages == len(messages) == 3
    assert builder.last_stats.characters == sum(
        len(message["content"]) for message in messages
    )


def test_zero_window_selects_no_observations(tmp_path):
    state = RunState(
        run_id="r1",
        observations=[{"value": "retained source"}],
    )
    before = state.model_copy(deep=True)
    builder = ContextBuilder(max_recent_observations=0)

    messages = builder.build(make_task(tmp_path), state)

    assert messages[-1]["content"] == "Recent observations:\n"
    assert state == before


def test_zero_character_budget_keeps_only_marker(tmp_path):
    builder = ContextBuilder(max_observation_chars=0)
    state = RunState(
        run_id="r1",
        observations=[{"value": "source text"}],
    )

    messages = builder.build(make_task(tmp_path), state)

    assert messages[-1]["content"] == ("Recent observations:\n... [truncated]")
    assert state.observations == [{"value": "source text"}]


@pytest.mark.parametrize(
    "name,value",
    [
        ("max_recent_observations", -1),
        ("max_observation_chars", -1),
        ("max_recent_observations", 1.5),
        ("max_observation_chars", 1.5),
        ("max_recent_observations", True),
        ("max_observation_chars", False),
    ],
)
def test_invalid_budgets_are_rejected(name, value):
    with pytest.raises(ValueError, match=name):
        ContextBuilder(**{name: value})
