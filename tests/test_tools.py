import pytest

from khosiness.models.base import ToolCall
from khosiness.tools.filesystem import (
    MAX_FILE_BYTES,
    MAX_OUTPUT_CHARS,
    ListDirectoryTool,
    ReadFileTool,
    SearchFilesTool,
)
from khosiness.tools.registry import ToolRegistry


def test_registry_rejects_duplicate_tool(tmp_path):
    registry = ToolRegistry()
    tool = ReadFileTool(tmp_path)
    registry.register(tool)

    with pytest.raises(ValueError, match="duplicate tool"):
        registry.register(tool)


def test_unknown_tool_returns_structured_error():
    registry = ToolRegistry()

    result = registry.execute(ToolCall(id="1", name="missing", arguments={}))

    assert result.ok is False
    assert "Unknown tool" in result.content


def test_read_file(tmp_path):
    (tmp_path / "hello.txt").write_text("hello", encoding="utf-8")

    result = ReadFileTool(tmp_path).execute({"path": "hello.txt"})

    assert result.ok is True
    assert result.content == "hello"


def test_read_file_cannot_escape_workspace(tmp_path):
    tool = ReadFileTool(tmp_path)

    with pytest.raises(ValueError, match="escapes workspace"):
        tool.execute({"path": "../outside.txt"})


def test_list_directory(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "folder").mkdir()

    result = ListDirectoryTool(tmp_path).execute({"path": "."})

    assert result.content.splitlines() == [
        "a.txt",
        "folder/",
    ]


def test_search_files(tmp_path):
    (tmp_path / "config.py").write_text(
        "RETRY_COUNT = 3\n",
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute({"query": "RETRY", "path": "."})

    assert "config.py:1:RETRY_COUNT = 3" in result.content


def test_missing_file_returns_structured_error(tmp_path):
    registry = ToolRegistry()
    registry.register(ReadFileTool(tmp_path))

    result = registry.execute(
        ToolCall(
            id="1",
            name="read_file",
            arguments={"path": "missing.txt"},
        )
    )

    assert result.ok is False
    assert "not a file" in result.content


def test_argument_validation_precedes_io(tmp_path):
    registry = ToolRegistry()
    registry.register(ReadFileTool(tmp_path))

    invalid_arguments = [
        {},
        {"path": 7},
        {"path": "a", "extra": True},
        {"path": "a", "start_line": 0},
        {"path": "a", "start_line": "1"},
        {"path": "a", "start_line": 3, "end_line": 2},
    ]

    for arguments in invalid_arguments:
        result = registry.execute(
            ToolCall(id="1", name="read_file", arguments=arguments)
        )

        assert result.ok is False
        assert "ValidationError" in result.content


def test_read_line_range(tmp_path):
    (tmp_path / "lines.txt").write_text(
        "one\ntwo\nthree\nfour\n",
        encoding="utf-8",
    )

    result = ReadFileTool(tmp_path).execute(
        {"path": "lines.txt", "start_line": 2, "end_line": 3}
    )

    assert result.content == "two\nthree\n"
    assert result.metadata["truncated"] is False


def test_read_output_and_byte_limits(tmp_path):
    path = tmp_path / "large.txt"
    path.write_text(
        "x" * (MAX_OUTPUT_CHARS + 1),
        encoding="utf-8",
    )

    result = ReadFileTool(tmp_path).execute({"path": path.name})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.metadata["truncated"] is True

    path.write_bytes(b"x" * (MAX_FILE_BYTES + 1))
    registry = ToolRegistry()
    registry.register(ReadFileTool(tmp_path))

    result = registry.execute(
        ToolCall(
            id="1",
            name="read_file",
            arguments={"path": path.name},
        )
    )

    assert result.ok is False
    assert "byte limit" in result.content


def test_search_match_limit(tmp_path):
    (tmp_path / "many.txt").write_text(
        "RETRY\n" * 101,
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content.splitlines()) == 100
    assert result.metadata["truncated"] is True


def test_search_character_limit(tmp_path):
    (tmp_path / "long.txt").write_text(
        "RETRY" + "x" * MAX_OUTPUT_CHARS,
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.metadata["truncated"] is True


def test_directory_output_limit(tmp_path):
    for index in range(101):
        (tmp_path / f"file-{index:03}.txt").touch()

    result = ListDirectoryTool(tmp_path).execute({"path": "."})

    assert len(result.content.splitlines()) == 100
    assert result.metadata["truncated"] is True


def test_search_rejects_symlink_escape_before_read(tmp_path, monkeypatch):
    import khosiness.tools.filesystem as filesystem

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("private data", encoding="utf-8")
    (workspace / "link.txt").symlink_to(outside)

    def forbidden_read(path):
        raise AssertionError("read must not be reached")

    monkeypatch.setattr(filesystem, "read_text_bounded", forbidden_read)
    registry = ToolRegistry()
    registry.register(SearchFilesTool(workspace))

    result = registry.execute(
        ToolCall(
            id="1",
            name="search_files",
            arguments={"path": ".", "query": "private"},
        )
    )

    assert result.ok is False
    assert "path escapes workspace" in result.content
