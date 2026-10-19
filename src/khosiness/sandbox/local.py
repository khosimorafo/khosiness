import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

from .base import ExecRequest, ExecResult


class LocalSandbox:
    """Local execution controls; not OS-level isolation."""

    def __init__(
        self,
        workspace: Path,
        allowed_commands: set[str] | None = None,
    ):
        self.workspace = workspace.resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError("workspace must be a directory")

        configured = {sys.executable} if allowed_commands is None else allowed_commands

        self.allowed_commands: dict[Path, Path] = {}
        for command in configured:
            path = Path(command)
            if not path.is_absolute():
                raise ValueError("allowed commands must use absolute paths")

            resolved = path.resolve(strict=True)
            if not resolved.is_file() or not os.access(resolved, os.X_OK):
                raise ValueError(f"command is not an executable file: {resolved}")

            self.allowed_commands[path] = resolved

    @staticmethod
    def _read_tail(stream) -> tuple[str, int]:
        stream.seek(0, os.SEEK_END)
        total_bytes = stream.tell()
        stream.seek(max(0, total_bytes - 20_000))
        content = stream.read(20_000).decode("utf-8", errors="replace")
        return content, total_bytes

    def execute(self, request: ExecRequest) -> ExecResult:
        executable = Path(request.argv[0])
        if not executable.is_absolute():
            raise PermissionError("executable must use an absolute path")

        expected_target = self.allowed_commands.get(executable)
        if expected_target is None or executable.resolve() != expected_target:
            raise PermissionError(f"command is not allowed: {executable}")

        cwd = request.cwd.resolve(strict=True)
        if not cwd.is_relative_to(self.workspace):
            raise PermissionError("cwd escapes workspace")
        if not cwd.is_dir():
            raise ValueError("cwd must be a directory")

        started = time.perf_counter()
        timed_out = False
        exit_code = None

        with tempfile.TemporaryFile() as stdout_file:
            with tempfile.TemporaryFile() as stderr_file:
                try:
                    process = subprocess.run(
                        [str(executable), *request.argv[1:]],
                        cwd=cwd,
                        stdin=subprocess.DEVNULL,
                        stdout=stdout_file,
                        stderr=stderr_file,
                        timeout=request.timeout_seconds,
                        shell=False,
                        check=False,
                        env={
                            "PATH": os.defpath,
                            "PYTHONUNBUFFERED": "1",
                        },
                    )
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    timed_out = True

                stdout, stdout_bytes = self._read_tail(stdout_file)
                stderr, stderr_bytes = self._read_tail(stderr_file)

        return ExecResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=int((time.perf_counter() - started) * 1000),
            timed_out=timed_out,
            metadata={
                "stdout_bytes": stdout_bytes,
                "stderr_bytes": stderr_bytes,
                "stdout_truncated": stdout_bytes > 20_000,
                "stderr_truncated": stderr_bytes > 20_000,
            },
        )
