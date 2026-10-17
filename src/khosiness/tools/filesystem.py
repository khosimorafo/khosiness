from itertools import islice
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import Tool, ToolResult

MAX_FILE_BYTES = 1_000_000
MAX_OUTPUT_CHARS = 20_000
MAX_ENTRIES = 100
MAX_MATCHES = 100


class PathArguments(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    path: str = Field(min_length=1)


class ReadArguments(PathArguments):
    start_line: int = Field(default=1, ge=1)
    end_line: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def ordered_range(self):
        if self.end_line is not None and self.end_line < self.start_line:
            raise ValueError("end_line must be at least start_line")
        return self


class SearchArguments(PathArguments):
    query: str = Field(min_length=1)


def safe_path(workspace: Path, relative_path: str) -> Path:
    workspace = workspace.resolve()
    candidate = (workspace / relative_path).resolve()
    if not candidate.is_relative_to(workspace):
        raise ValueError("path escapes workspace")
    return candidate


def read_text_bounded(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"not a file: {path.name}")
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("file exceeds byte limit")
    return data.decode("utf-8")


def schema_for(tool: Tool, arguments: type[BaseModel]) -> dict:
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": arguments.model_json_schema(),
    }


class ListDirectoryTool(Tool):
    name = "list_directory"
    description = "List at most 100 entries inside the workspace."

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def schema(self) -> dict:
        return schema_for(self, PathArguments)

    def execute(self, arguments: dict) -> ToolResult:
        args = PathArguments.model_validate(arguments)
        path = safe_path(self.workspace, args.path)
        if not path.is_dir():
            raise ValueError(f"not a directory: {args.path}")

        # Select a bounded subset, then sort it.
        # Directory order is unspecified.
        items = list(islice(path.iterdir(), MAX_ENTRIES + 1))
        entries = sorted(
            item.name + ("/" if not item.is_symlink() and item.is_dir() else "")
            for item in items[:MAX_ENTRIES]
        )
        text = "\n".join(entries)
        return ToolResult(
            ok=True,
            content=text[:MAX_OUTPUT_CHARS],
            metadata={
                "count": len(entries),
                "truncated": len(items) > MAX_ENTRIES or len(text) > MAX_OUTPUT_CHARS,
            },
        )


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read a UTF-8 file; optional line bounds are 1-based and inclusive."

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def schema(self) -> dict:
        return schema_for(self, ReadArguments)

    def execute(self, arguments: dict) -> ToolResult:
        args = ReadArguments.model_validate(arguments)
        path = safe_path(self.workspace, args.path)
        text = read_text_bounded(path)
        selected = "".join(
            text.splitlines(keepends=True)[args.start_line - 1 : args.end_line]
        )
        return ToolResult(
            ok=True,
            content=selected[:MAX_OUTPUT_CHARS],
            metadata={
                "characters": len(text),
                "start_line": args.start_line,
                "end_line": args.end_line,
                "truncated": len(selected) > MAX_OUTPUT_CHARS,
            },
        )


class SearchFilesTool(Tool):
    name = "search_files"
    description = (
        "Search UTF-8 files; return at most 100 matches and 20,000 characters."
    )

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def schema(self) -> dict:
        return schema_for(self, SearchArguments)

    def execute(self, arguments: dict) -> ToolResult:
        args = SearchArguments.model_validate(arguments)
        root = safe_path(self.workspace, args.path)
        if not root.is_dir():
            raise ValueError(f"not a directory: {args.path}")

        matches: list[str] = []
        output_chars = 0
        for path in root.rglob("*"):
            # Validate every discovered target, including symlink files.
            resolved = safe_path(self.workspace, str(path.relative_to(self.workspace)))
            if not resolved.is_file():
                continue
            try:
                lines = read_text_bounded(resolved).splitlines()
            except UnicodeDecodeError:
                continue

            for number, line in enumerate(lines, start=1):
                if args.query in line:
                    match = (
                        f"{path.relative_to(self.workspace)}:"
                        f"{number}:{line.strip()}"
                    )
                    matches.append(match)
                    output_chars += len(match) + (1 if len(matches) > 1 else 0)
                    if len(matches) >= MAX_MATCHES or output_chars >= MAX_OUTPUT_CHARS:
                        return ToolResult(
                            ok=True,
                            content="\n".join(matches)[:MAX_OUTPUT_CHARS],
                            metadata={"truncated": True},
                        )

        return ToolResult(
            ok=True,
            content="\n".join(matches),
            metadata={"truncated": False},
        )
