import pytest

from khosiness.models.base import ToolCall
from khosiness.tools.filesystem import (
    MAX_ENTRIES,
    MAX_MATCHES,
    MAX_OUTPUT_CHARS,
    MAX_READ_LINES,
    ListDirectoryTool,
    ReadFileTool,
    SearchFilesTool,
)
from khosiness.tools.registry import ToolRegistry


def test_registry_rejects_duplicate_tool(tmp_path):
    registry = ToolRegistry()
    tool = ReadFileTool(tmp_path)
    registry.register(tool)

    try:
        registry.register(tool)
        assert False, "expected duplicate registration to fail"
    except ValueError:
        pass


def test_unknown_tool_returns_structured_error():
    registry = ToolRegistry()

    result = registry.execute(
        ToolCall(
            id="1",
            name="missing",
            arguments={},
        )
    )

    assert result.ok is False
    assert "Unknown tool" in result.content


def test_read_file(tmp_path):
    (tmp_path / "hello.txt").write_text(
        "hello",
        encoding="utf-8",
    )
    tool = ReadFileTool(tmp_path)

    result = tool.execute({"path": "hello.txt"})

    assert result.ok is True
    assert result.content == "    1 | hello"
    assert result.metadata["path"] == "hello.txt"
    assert result.metadata["end_line"] == 1


def test_read_file_cannot_escape_workspace(tmp_path):
    tool = ReadFileTool(tmp_path)

    try:
        tool.execute({"path": "../outside.txt"})
        assert False, "expected path escape to fail"
    except ValueError as exc:
        assert "escapes workspace" in str(exc)


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

    for arguments in [
        {},
        {"path": 7},
        {"path": "a", "extra": True},
        {"path": "a", "start_line": 0},
        {"path": "a", "start_line": "1"},
        {"path": "a", "start_line": 3, "end_line": 2},
    ]:
        result = registry.execute(
            ToolCall(
                id="1",
                name="read_file",
                arguments=arguments,
            )
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

    assert result.content == "    2 | two\n    3 | three"
    assert result.metadata["end_line"] == 3
    assert result.metadata["truncated"] is False


def test_read_output_and_byte_limits(tmp_path):
    from khosiness.tools.filesystem import MAX_FILE_BYTES, MAX_OUTPUT_CHARS

    path = tmp_path / "large.txt"
    path.write_text("x" * (MAX_OUTPUT_CHARS + 1), encoding="utf-8")

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
    from khosiness.tools.filesystem import MAX_OUTPUT_CHARS

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


@pytest.mark.parametrize(
    "tool_class,field,maximum,base",
    [
        (ListDirectoryTool, "max_items", MAX_ENTRIES, {"path": "."}),
        (ReadFileTool, "max_lines", MAX_READ_LINES, {"path": "config.py"}),
        (SearchFilesTool, "max_matches", MAX_MATCHES, {"path": ".", "query": "RETRY"}),
    ],
)
def test_budget_schema_and_runtime_validation(tmp_path, monkeypatch, tool_class, field, maximum, base):
    import khosiness.tools.filesystem as filesystem

    tool = tool_class(tmp_path)
    schema = tool.schema()["parameters"]
    budget = schema["properties"][field]
    assert budget["type"] == "integer"
    assert budget["minimum"] == 1
    assert budget["maximum"] == maximum
    assert budget["default"] == maximum
    assert schema["additionalProperties"] is False

    def forbid_path_resolution(*args):
        raise AssertionError("invalid arguments reached the filesystem")

    monkeypatch.setattr(filesystem, "safe_path", forbid_path_resolution)
    registry = ToolRegistry()
    registry.register(tool)
    for value in (0, -1, maximum + 1, "3", True, 1.5):
        result = registry.execute(
            ToolCall(id="invalid", name=tool.name, arguments={**base, field: value})
        )
        assert result.ok is False
        assert "ValidationError" in result.content


@pytest.mark.parametrize("count,expected,truncated", [(0, 0, False), (3, 3, False), (4, 3, True)])
def test_requested_listing_limit(tmp_path, count, expected, truncated):
    for number in range(count):
        (tmp_path / f"{number}.txt").touch()

    result = ListDirectoryTool(tmp_path).execute({"path": ".", "max_items": 3})

    assert len(result.content.splitlines()) == expected
    assert result.metadata == {"count": expected, "truncated": truncated}


def test_listing_is_shallow_and_does_not_label_symlink_as_directory(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    folder = workspace / "folder"
    folder.mkdir()
    (folder / "nested.txt").write_text("private", encoding="utf-8")
    (workspace / "linked-folder").symlink_to(folder, target_is_directory=True)

    def forbid_recursive_search(*args):
        raise AssertionError("listing must not recurse")

    monkeypatch.setattr(type(workspace), "rglob", forbid_recursive_search)
    result = ListDirectoryTool(workspace).execute({"path": "."})

    assert result.content.splitlines() == ["folder/", "linked-folder"]
    assert result.metadata["truncated"] is False


def test_listing_consumes_only_one_entry_after_requested_limit(tmp_path, monkeypatch):
    for name in ("z", "a", "m", "b"):
        (tmp_path / name).touch()

    def entries(directory):
        assert directory == tmp_path
        for name in ("z", "a", "m", "b"):
            yield tmp_path / name
        raise AssertionError("listing consumed past its single lookahead")

    monkeypatch.setattr(type(tmp_path), "iterdir", entries)
    result = ListDirectoryTool(tmp_path).execute({"path": ".", "max_items": 3})

    assert result.content.splitlines() == ["a", "m", "z"]
    assert result.metadata == {"count": 3, "truncated": True}


@pytest.mark.parametrize(
    "start,end,max_lines,returned,partial",
    [
        (2, 5, 2, [2, 3], True),
        (2, 3, 2, [2, 3], False),
        (5, None, 200, [5, 6], False),
        (9, None, 200, [], False),
    ],
)
def test_numbered_read_window(tmp_path, start, end, max_lines, returned, partial):
    (tmp_path / "lines.txt").write_text(
        "".join(f"line {number}\n" for number in range(1, 7)),
        encoding="utf-8",
    )
    result = ReadFileTool(tmp_path).execute(
        {"path": "lines.txt", "start_line": start, "end_line": end, "max_lines": max_lines}
    )

    assert result.content == "\n".join(f"{n:>5} | line {n}" for n in returned)
    assert result.metadata["path"] == "lines.txt"
    assert result.metadata["start_line"] == (returned[0] if returned else None)
    assert result.metadata["end_line"] == (returned[-1] if returned else None)
    assert result.metadata["total_lines"] == 6
    assert result.metadata["truncated"] is partial


def test_default_read_line_limit_and_source_whitespace(tmp_path):
    (tmp_path / "many.txt").write_text(
        "\n    RETRY = 3\n" + "x\n" * MAX_READ_LINES,
        encoding="utf-8",
    )
    result = ReadFileTool(tmp_path).execute({"path": "many.txt"})

    assert result.content.startswith("    1 | \n    2 |     RETRY = 3")
    assert len(result.content.splitlines()) == MAX_READ_LINES
    assert result.metadata["end_line"] == MAX_READ_LINES
    assert result.metadata["total_lines"] == MAX_READ_LINES + 2
    assert result.metadata["truncated"] is True


def test_read_character_limit_marks_partial_line(tmp_path):
    (tmp_path / "long.txt").write_text(
        "short\n" + "x" * MAX_OUTPUT_CHARS + "\nunseen\n",
        encoding="utf-8",
    )
    result = ReadFileTool(tmp_path).execute({"path": "long.txt"})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.content.startswith("    1 | short\n    2 | ")
    assert "unseen" not in result.content
    assert result.metadata["end_line"] == 2
    assert result.metadata["partial_line"] is True
    assert result.metadata["truncated"] is True


def test_read_character_limit_keeps_citation_prefix_complete(tmp_path):
    first = "x" * (MAX_OUTPUT_CHARS - len("    1 | ") - 3)
    (tmp_path / "boundary.txt").write_text(first + "\nhidden\n", encoding="utf-8")
    result = ReadFileTool(tmp_path).execute({"path": "boundary.txt"})

    assert result.content == "    1 | " + first
    assert result.metadata["end_line"] == 1
    assert result.metadata["partial_line"] is False
    assert result.metadata["truncated"] is True


@pytest.mark.parametrize("budget,expected,truncated", [(1, 1, True), (2, 2, True), (3, 3, True), (100, 3, False)])
def test_requested_search_limit_and_structured_matches(tmp_path, budget, expected, truncated):
    (tmp_path / "config.py").write_text(
        "  RETRY = 1\n  RETRY = 2\n  RETRY = 3\n",
        encoding="utf-8",
    )
    result = SearchFilesTool(tmp_path).execute(
        {"path": ".", "query": "RETRY", "max_matches": budget}
    )

    assert result.metadata["matches"] == [
        {"path": "config.py", "line": number, "text": f"  RETRY = {number}"}
        for number in range(1, expected + 1)
    ]
    assert result.content == "\n".join(
        f"config.py:{number}:  RETRY = {number}" for number in range(1, expected + 1)
    )
    assert result.metadata["truncated"] is truncated
    assert result.metadata["partial_match"] is False


def test_search_character_limit_identifies_partial_match(tmp_path):
    (tmp_path / "long.txt").write_text(
        "RETRY" + "x" * MAX_OUTPUT_CHARS,
        encoding="utf-8",
    )
    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.metadata["truncated"] is True
    assert result.metadata["partial_match"] is True
    assert result.metadata["matches"][0]["path"] == "long.txt"
    assert result.content == "long.txt:1:" + result.metadata["matches"][0]["text"]


def test_search_stops_before_reading_later_files_at_match_limit(tmp_path, monkeypatch):
    import khosiness.tools.filesystem as filesystem

    first = tmp_path / "first.txt"
    later = tmp_path / "later.txt"
    first.write_text("RETRY\n", encoding="utf-8")
    later.write_text("RETRY\n", encoding="utf-8")
    original_read = filesystem.read_text_bounded

    def read_first_only(path):
        assert path == first, "match budget should stop later reads"
        return original_read(path)

    monkeypatch.setattr(type(tmp_path), "rglob", lambda self, pattern: iter([first, later]))
    monkeypatch.setattr(filesystem, "read_text_bounded", read_first_only)
    result = SearchFilesTool(tmp_path).execute(
        {"path": ".", "query": "RETRY", "max_matches": 1}
    )

    assert result.metadata["matches"] == [
        {"path": "first.txt", "line": 1, "text": "RETRY"}
    ]
    assert result.metadata["truncated"] is True


def test_search_partial_match_may_omit_late_query_text(tmp_path):
    (tmp_path / "late.txt").write_text(
        "x" * MAX_OUTPUT_CHARS + "RETRY\n", encoding="utf-8"
    )
    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert "RETRY" not in result.content
    assert result.metadata["partial_match"] is True
    assert result.metadata["truncated"] is True


def test_search_no_match_has_explicit_empty_metadata(tmp_path):
    (tmp_path / "config.py").write_text("TIMEOUT = 5\n", encoding="utf-8")
    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert result.ok is True
    assert result.content == ""
    assert result.metadata == {"matches": [], "truncated": False, "partial_match": False}


def test_search_skips_non_utf8_file_and_preserves_indentation(tmp_path):
    (tmp_path / "binary.bin").write_bytes(b"RETRY\xff")
    (tmp_path / "config.py").write_text("    RETRY = 3\n", encoding="utf-8")
    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert result.content == "config.py:1:    RETRY = 3"
    assert result.metadata["matches"] == [
        {"path": "config.py", "line": 1, "text": "    RETRY = 3"}
    ]


@pytest.mark.parametrize(
    "tool_class,arguments",
    [
        (ListDirectoryTool, {"path": "outside"}),
        (ReadFileTool, {"path": "secret.txt"}),
        (SearchFilesTool, {"path": "outside", "query": "private"}),
    ],
)
def test_symlinked_requested_root_rejected_before_access(
    tmp_path, monkeypatch, tool_class, arguments
):
    import khosiness.tools.filesystem as filesystem

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret.txt"
    secret.write_text("private", encoding="utf-8")
    (workspace / "outside").symlink_to(outside, target_is_directory=True)
    (workspace / "secret.txt").symlink_to(secret)

    def forbidden_access(*args):
        raise AssertionError("symlink target was accessed")

    monkeypatch.setattr(filesystem, "read_text_bounded", forbidden_access)
    monkeypatch.setattr(type(workspace), "iterdir", forbidden_access)
    monkeypatch.setattr(type(workspace), "rglob", forbidden_access)
    registry = ToolRegistry()
    registry.register(tool_class(workspace))
    result = registry.execute(
        ToolCall(id="symlink-root", name=tool_class.name, arguments=arguments)
    )

    assert result.ok is False
    assert "path escapes workspace" in result.content


def test_listing_character_cap_reports_incomplete_names(tmp_path):
    for number in range(100):
        (tmp_path / (f"{number:03}-" + "x" * 230)).touch()

    result = ListDirectoryTool(tmp_path).execute({"path": "."})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.metadata["truncated"] is True


def test_listing_external_symlink_reports_name_without_following_target(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.txt").write_text("private", encoding="utf-8")
    (workspace / "outside-link").symlink_to(outside, target_is_directory=True)

    result = ListDirectoryTool(workspace).execute({"path": "."})

    assert result.content == "outside-link"
    assert result.metadata == {"count": 1, "truncated": False}


def test_empty_file_read_reports_no_line_range(tmp_path):
    (tmp_path / "empty.txt").touch()

    result = ReadFileTool(tmp_path).execute({"path": "empty.txt"})

    assert result.ok is True
    assert result.content == ""
    assert result.metadata["start_line"] is None
    assert result.metadata["end_line"] is None
    assert result.metadata["total_lines"] == 0
    assert result.metadata["truncated"] is False


def test_search_rejects_file_over_byte_limit(tmp_path):
    from khosiness.tools.filesystem import MAX_FILE_BYTES

    (tmp_path / "large.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
    registry = ToolRegistry()
    registry.register(SearchFilesTool(tmp_path))

    result = registry.execute(
        ToolCall(id="large-search", name="search_files", arguments={"path": ".", "query": "x"})
    )

    assert result.ok is False
    assert "byte limit" in result.content


def test_search_omits_match_when_location_prefix_cannot_fit(tmp_path):
    prefix = "hits.txt:1:"
    first = "RETRY" + "x" * (MAX_OUTPUT_CHARS - len(prefix) - 3 - len("RETRY"))
    (tmp_path / "hits.txt").write_text(first + "\nRETRY second\n", encoding="utf-8")

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert result.content == prefix + first
    assert result.metadata["matches"] == [{"path": "hits.txt", "line": 1, "text": first}]
    assert result.metadata["truncated"] is True
    assert result.metadata["partial_match"] is False


@pytest.mark.parametrize(
    "tool_class,valid_arguments",
    [
        (ListDirectoryTool, {"path": "."}),
        (SearchFilesTool, {"path": ".", "query": "RETRY"}),
    ],
)
def test_navigation_rejects_extra_fields_and_nonstring_paths_before_io(
    tmp_path, monkeypatch, tool_class, valid_arguments
):
    import khosiness.tools.filesystem as filesystem

    def forbid_path_resolution(*args):
        raise AssertionError("invalid arguments reached path resolution")

    monkeypatch.setattr(filesystem, "safe_path", forbid_path_resolution)
    registry = ToolRegistry()
    registry.register(tool_class(tmp_path))
    for arguments in (
        {**valid_arguments, "unexpected": True},
        {**valid_arguments, "path": 7},
    ):
        result = registry.execute(
            ToolCall(id="invalid", name=tool_class.name, arguments=arguments)
        )
        assert result.ok is False
        assert "ValidationError" in result.content
