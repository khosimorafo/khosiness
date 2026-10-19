from itertools import islice
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import Tool, ToolResult

MAX_FILE_BYTES = 1_000_000
MAX_OUTPUT_CHARS = 20_000
MAX_ENTRIES = 100
MAX_MATCHES = 100
MAX_READ_LINES = 200


class PathArguments(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    path: str = Field(min_length=1)


class ListArguments(PathArguments):
    max_items: int = Field(
        default=MAX_ENTRIES,
        ge=1,
        le=MAX_ENTRIES,
    )


class ReadArguments(PathArguments):
    start_line: int = Field(default=1, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    max_lines: int = Field(
        default=MAX_READ_LINES,
        ge=1,
        le=MAX_READ_LINES,
    )

    @model_validator(mode="after")
    def ordered_range(self):
        if self.end_line is not None and self.end_line < self.start_line:
            raise ValueError("end_line must be at least start_line")
        return self


class SearchArguments(PathArguments):
    query: str = Field(min_length=1)
    max_matches: int = Field(
        default=MAX_MATCHES,
        ge=1,
        le=MAX_MATCHES,
    )


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
    description = "List a shallow directory inside the workspace; max_items is 1–100."

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def schema(self) -> dict:
        return schema_for(self, ListArguments)

    def execute(self, arguments: dict) -> ToolResult:
        args = ListArguments.model_validate(arguments)
        path = safe_path(self.workspace, args.path)
        if not path.is_dir():
            raise ValueError(f"not a directory: {args.path}")

        # Select a bounded subset, then sort it.
        # Directory order is unspecified.
        items = list(islice(path.iterdir(), args.max_items + 1))
        entries = sorted(
            item.name + ("/" if not item.is_symlink() and item.is_dir() else "")
            for item in items[:args.max_items]
        )
        text = "\n".join(entries)
        return ToolResult(
            ok=True,
            content=text[:MAX_OUTPUT_CHARS],
            metadata={
                "count": len(entries),
                "truncated": len(items) > args.max_items or len(text) > MAX_OUTPUT_CHARS,
            },
        )


class ReadFileTool(Tool):
    name = "read_file"
    description = (
        "Read numbered UTF-8 lines; bounds are 1-based and inclusive. "
        "Return at most max_lines (1–200) and 20,000 characters."
    )

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def schema(self) -> dict:
        return schema_for(self, ReadArguments)

    def execute(self, arguments: dict) -> ToolResult:
        args = ReadArguments.model_validate(arguments)
        path = safe_path(self.workspace, args.path)
        text = read_text_bounded(path)
        lines = text.splitlines()
        requested_end = min(
            args.end_line if args.end_line is not None else len(lines),
            len(lines),
        )
        selected_end = min(requested_end, args.start_line + args.max_lines - 1)

        numbered: list[str] = []
        output_chars = 0
        returned_end = None
        partial_line = False
        for number in range(args.start_line, selected_end + 1):
            prefix = f"{number:>5} | "
            source = lines[number - 1]
            separator_chars = 1 if numbered else 0
            remaining = MAX_OUTPUT_CHARS - output_chars - separator_chars
            # Keep the full citation prefix and at least one source character
            # for a nonempty line. A blank source line needs only its prefix.
            if remaining < len(prefix) + bool(source):
                break
            line = prefix + source
            rendered = line[:remaining]
            numbered.append(rendered)
            output_chars += separator_chars + len(rendered)
            returned_end = number
            if len(rendered) < len(line):
                partial_line = True
                break

        truncated = requested_end >= args.start_line and (
            returned_end is None or returned_end < requested_end or partial_line
        )
        return ToolResult(
            ok=True,
            content="\n".join(numbered),
            metadata={
                "path": str(path.relative_to(self.workspace)),
                "characters": len(text),
                "start_line": args.start_line if numbered else None,
                "end_line": returned_end,
                "total_lines": len(lines),
                "partial_line": partial_line,
                "truncated": truncated,
            },
        )


class SearchFilesTool(Tool):
    name = "search_files"
    description = (
        "Search UTF-8 files with literal text; return path, line and text. "
        "max_matches is 1–100; rendered output is capped at 20,000 characters. "
        "truncated means the result may be incomplete."
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

        matches: list[dict] = []
        rendered_matches: list[str] = []
        output_chars = 0

        def finish(truncated: bool = False, partial_match: bool = False) -> ToolResult:
            return ToolResult(
                ok=True,
                content="\n".join(rendered_matches),
                metadata={
                    "matches": matches,
                    "truncated": truncated,
                    "partial_match": partial_match,
                },
            )

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
                    relative = str(path.relative_to(self.workspace))
                    prefix = f"{relative}:{number}:"
                    separator_chars = 1 if matches else 0
                    remaining = MAX_OUTPUT_CHARS - output_chars - separator_chars
                    if remaining < len(prefix) + 1:
                        return finish(truncated=True)
                    selected_text = line[:remaining - len(prefix)]
                    partial_match = len(selected_text) < len(line)
                    matches.append(
                        {"path": relative, "line": number, "text": selected_text}
                    )
                    rendered = prefix + selected_text
                    rendered_matches.append(rendered)
                    output_chars += separator_chars + len(rendered)
                    if (
                        len(matches) >= args.max_matches
                        or output_chars >= MAX_OUTPUT_CHARS
                        or partial_match
                    ):
                        return finish(truncated=True, partial_match=partial_match)

        return finish()
