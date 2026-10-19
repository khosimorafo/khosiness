import sys

import pytest
from pydantic import ValidationError

from khosiness.models.base import ToolCall
from khosiness.sandbox.base import ExecRequest, ExecResult
from khosiness.tools.registry import ToolRegistry
from khosiness.tools.shell import ShellTool
from khosiness.sandbox.local import LocalSandbox


@pytest.mark.parametrize("timeout", [-1, 0, 121, True, "20"])
def test_request_rejects_invalid_timeout(tmp_path, timeout):
    with pytest.raises(ValidationError):
        ExecRequest(
            argv=[sys.executable, "-V"],
            cwd=tmp_path,
            timeout_seconds=timeout,
        )


def test_runner_captures_stdout_and_stderr(tmp_path):
    runner = LocalSandbox(tmp_path)

    result = runner.execute(
        ExecRequest(
            argv=[
                sys.executable,
                "-c",
                'import sys; print("hello"); print("problem", file=sys.stderr)',
            ],
            cwd=tmp_path,
        )
    )

    assert result.exit_code == 0
    assert result.timed_out is False
    assert result.stdout == "hello\n"
    assert result.stderr == "problem\n"
    assert result.metadata["stdout_bytes"] == 6
    assert result.metadata["stderr_bytes"] == 8
    assert result.metadata["stdout_truncated"] is False
    assert result.metadata["stderr_truncated"] is False


def test_nonzero_exit_is_returned_as_data(tmp_path):
    runner = LocalSandbox(tmp_path)

    result = runner.execute(
        ExecRequest(
            argv=[
                sys.executable,
                "-c",
                'print("before failure"); raise SystemExit(7)',
            ],
            cwd=tmp_path,
        )
    )

    assert result.exit_code == 7
    assert result.timed_out is False
    assert result.stdout == "before failure\n"


def test_runner_preserves_selected_python_environment(tmp_path):
    runner = LocalSandbox(tmp_path)

    result = runner.execute(
        ExecRequest(
            argv=[
                sys.executable,
                "-c",
                "import sys; print(sys.prefix)",
            ],
            cwd=tmp_path,
        )
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == sys.prefix


@pytest.fixture
def no_process(monkeypatch):
    def forbid_process(*args, **kwargs):
        pytest.fail("rejected request reached process creation")

    monkeypatch.setattr(
        "khosiness.sandbox.local.subprocess.run",
        forbid_process,
    )


def test_timeout_preserves_output_before_termination(tmp_path):
    runner = LocalSandbox(tmp_path)

    result = runner.execute(
        ExecRequest(
            argv=[
                sys.executable,
                "-c",
                'import time; print("started", flush=True); time.sleep(10)',
            ],
            cwd=tmp_path,
            timeout_seconds=1,
        )
    )

    assert result.timed_out is True
    assert result.exit_code is None
    assert result.stdout == "started\n"


@pytest.mark.parametrize(
    ("command", "reason"),
    [
        ("python", "executable must use an absolute path"),
        ("/not-configured/python", "command is not allowed"),
    ],
)
def test_unconfigured_command_is_rejected_before_launch(
    tmp_path, no_process, command, reason
):
    runner = LocalSandbox(tmp_path)

    with pytest.raises(PermissionError, match=reason):
        runner.execute(ExecRequest(argv=[command, "-V"], cwd=tmp_path))


def test_empty_allowlist_permits_nothing(tmp_path, no_process):
    runner = LocalSandbox(tmp_path, allowed_commands=set())

    with pytest.raises(PermissionError, match="command is not allowed"):
        runner.execute(ExecRequest(argv=[sys.executable, "-V"], cwd=tmp_path))


@pytest.mark.parametrize("escape", ["parent", "symlink"])
def test_cwd_escape_is_rejected_before_launch(tmp_path, no_process, escape):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner = LocalSandbox(workspace)

    cwd = tmp_path
    if escape == "symlink":
        cwd = workspace / "escape"
        cwd.symlink_to(tmp_path, target_is_directory=True)

    with pytest.raises(PermissionError, match="cwd escapes workspace"):
        runner.execute(ExecRequest(argv=[sys.executable, "-V"], cwd=cwd))


@pytest.mark.parametrize("size", [19_999, 20_000, 20_001])
def test_output_limits_preserve_each_stream_tail(tmp_path, size):
    runner = LocalSandbox(tmp_path)
    source = (
        "import sys; "
        "size = int(sys.argv[1]); "
        "text = 'x' * (size - 3) + 'END'; "
        "sys.stdout.write(text); "
        "sys.stderr.write(text)"
    )

    result = runner.execute(
        ExecRequest(
            argv=[sys.executable, "-c", source, str(size)],
            cwd=tmp_path,
        )
    )

    expected = "x" * (min(size, 20_000) - 3) + "END"
    assert result.exit_code == 0
    assert result.stdout == expected
    assert result.stderr == expected
    for stream in ("stdout", "stderr"):
        assert result.metadata[f"{stream}_bytes"] == size
        assert result.metadata[f"{stream}_truncated"] is (size > 20_000)


def test_child_receives_controlled_launch_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("KHOSINESS_TEST_SECRET", "must-not-inherit")
    runner = LocalSandbox(tmp_path)
    literal_argument = "hello; echo unexpected | cat"
    source = (
        "import os, sys; "
        "print(os.environ.get('KHOSINESS_TEST_SECRET', 'absent')); "
        "print(repr(sys.stdin.read())); "
        "print(sys.argv[1]); "
        "print(os.getcwd())"
    )

    result = runner.execute(
        ExecRequest(
            argv=[sys.executable, "-c", source, literal_argument],
            cwd=tmp_path,
        )
    )

    assert result.exit_code == 0
    assert result.stdout.splitlines() == [
        "absent",
        "''",
        literal_argument,
        str(tmp_path.resolve()),
    ]


def test_unconfigured_executable_alias_is_rejected(tmp_path, no_process):
    alias = tmp_path / "python"
    alias.symlink_to(sys.executable)
    runner = LocalSandbox(tmp_path)

    with pytest.raises(PermissionError, match="command is not allowed"):
        runner.execute(ExecRequest(argv=[str(alias), "-V"], cwd=tmp_path))


def test_changed_executable_target_is_rejected(tmp_path, no_process):
    launcher = tmp_path / "python"
    launcher.symlink_to(sys.executable)
    runner = LocalSandbox(tmp_path, allowed_commands={str(launcher)})

    replacement = tmp_path / "replacement"
    replacement.write_text("different target", encoding="utf-8")
    launcher.unlink()
    launcher.symlink_to(replacement)

    with pytest.raises(PermissionError, match="command is not allowed"):
        runner.execute(ExecRequest(argv=[str(launcher), "-V"], cwd=tmp_path))


class RecordingSandbox:
    def __init__(self, result):
        self.result = result
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return self.result


@pytest.mark.parametrize(
    ("exit_code", "timed_out", "expected_ok"),
    [(0, False, True), (7, False, False), (None, True, False)],
)
def test_shell_adapter_translates_request_and_result(
    tmp_path, exit_code, timed_out, expected_ok
):
    execution = ExecResult(
        exit_code=exit_code,
        stdout="captured output\n",
        stderr="diagnostic\n",
        duration_ms=7,
        timed_out=timed_out,
        metadata={"stdout_truncated": False},
    )
    sandbox = RecordingSandbox(execution)
    tool = ShellTool(tmp_path, sandbox)

    result = tool.execute(
        {
            "argv": [sys.executable, "-V"],
            "cwd": "child",
            "timeout_seconds": 3,
        }
    )

    assert len(sandbox.requests) == 1
    request = sandbox.requests[0]
    assert request.argv == [sys.executable, "-V"]
    assert request.cwd == tmp_path.resolve() / "child"
    assert request.timeout_seconds == 3
    assert result.ok is expected_ok
    assert result.metadata == execution.model_dump()
    assert "captured output\n" in result.content
    assert "diagnostic\n" in result.content


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"argv": []},
        {"argv": [""]},
        {"argv": ["python", "\x00"]},
        {"argv": "python -V"},
        {"argv": [7]},
        {"argv": ["python"], "cwd": 7},
        {"argv": ["python"], "timeout_seconds": True},
        {"argv": ["python"], "extra": 1},
    ],
)
def test_invalid_tool_arguments_do_not_reach_runtime(tmp_path, arguments):
    sandbox = RecordingSandbox(ExecResult(exit_code=0, duration_ms=0))
    registry = ToolRegistry()
    registry.register(ShellTool(tmp_path, sandbox))

    result = registry.execute(ToolCall(id="invalid", name="shell", arguments=arguments))

    assert result.ok is False
    assert result.content.startswith("ValidationError:")
    assert sandbox.requests == []


def test_shell_schema_publishes_argument_contract(tmp_path):
    sandbox = RecordingSandbox(ExecResult(exit_code=0, duration_ms=0))
    schema = ShellTool(tmp_path, sandbox).schema()["parameters"]

    assert schema["additionalProperties"] is False
    assert schema["required"] == ["argv"]
    assert schema["properties"]["argv"]["minItems"] == 1
    assert schema["properties"]["cwd"]["default"] == "."
    assert schema["properties"]["timeout_seconds"]["minimum"] == 1
    assert schema["properties"]["timeout_seconds"]["maximum"] == 120


def test_registry_shell_runs_a_real_command(tmp_path):
    registry = ToolRegistry()
    registry.register(ShellTool(tmp_path, LocalSandbox(tmp_path)))

    result = registry.execute(
        ToolCall(
            id="real-command",
            name="shell",
            arguments={
                "argv": [
                    sys.executable,
                    "-c",
                    'print("through registry")',
                ]
            },
        )
    )

    assert result.ok is True
    assert result.metadata["exit_code"] == 0
    assert result.metadata["stdout"] == "through registry\n"


def test_registry_records_runtime_rejection_as_failure(tmp_path, no_process):
    runner = LocalSandbox(tmp_path, allowed_commands=set())
    registry = ToolRegistry()
    registry.register(ShellTool(tmp_path, runner))

    result = registry.execute(
        ToolCall(
            id="rejected-command",
            name="shell",
            arguments={"argv": [sys.executable, "-V"]},
        )
    )

    assert result.ok is False
    assert result.content.startswith("PermissionError: command is not allowed")
