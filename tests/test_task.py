from pathlib import Path

import pytest

from khosiness.task import Task


def test_task_accepts_existing_workspace(tmp_path: Path):
    task = Task(
        id="task-1",
        objective="Find retry configuration",
        workspace=tmp_path,
        max_steps=5,
    )

    assert task.workspace == tmp_path.resolve()
    assert task.objective == "Find retry configuration"
    assert task.max_steps == 5


def test_task_rejects_missing_workspace(tmp_path: Path):
    with pytest.raises(ValueError, match="workspace does not exist"):
        Task(
            id="task-1",
            objective="Find retry configuration",
            workspace=tmp_path / "missing",
        )


def test_task_rejects_file_as_workspace(tmp_path: Path):
    file_path = tmp_path / "not-a-directory"
    file_path.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="workspace is not a directory"):
        Task(
            id="task-1",
            objective="Find retry configuration",
            workspace=file_path,
        )


def test_task_rejects_blank_objective(tmp_path: Path):
    with pytest.raises(ValueError, match="objective must not be blank"):
        Task(id="task-1", objective="   ", workspace=tmp_path)


def test_task_rejects_zero_steps(tmp_path: Path):
    with pytest.raises(ValueError, match="max_steps must be >= 1"):
        Task(
            id="task-1",
            objective="Find CLI version",
            workspace=tmp_path,
            max_steps=0,
        )


def test_task_round_trip_json(tmp_path: Path):
    task = Task(
        id="task-1",
        objective="Find retry configuration",
        workspace=tmp_path,
        constraints=["Do not modify files"],
        success_criteria=["Name the defining file"],
        max_steps=8,
    )

    restored = Task.model_validate_json(task.model_dump_json())

    assert restored == task
