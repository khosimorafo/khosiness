import pytest

from khosiness.models.base import ToolCall
from khosiness.tools.filesystem import (
    MAX_FILE_BYTES,
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
    assert result.content == "    1 | hello"


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


@pytest.mark.parametrize("size,truncated", [(0, False), (3, False), (4, True)])
def test_listing_requested_limit_and_completeness(tmp_path, size, truncated):
    for number in range(size):
        (tmp_path / f"{number}.txt").touch()

    result = ListDirectoryTool(tmp_path).execute({"path": ".", "max_items": 3})

    assert result.ok is True
    assert len(result.content.splitlines()) == min(size, 3)
    assert result.metadata == {"count": min(size, 3), "truncated": truncated}


def test_listing_sorts_selected_subset_and_consumes_only_one_extra(tmp_path, monkeypatch):
    for name in ["z", "a", "m", "b", "c", "d", "e", "f", "g", "h"]:
        (tmp_path / name).touch()

    def limited_entries(directory):
        assert directory == tmp_path
        for name in ["z", "a", "m", "b"]:
            yield tmp_path / name
        raise AssertionError("listing consumed beyond its three entries and lookahead")

    # This checks yielded-item consumption, not Path.iterdir's underlying scan.
    monkeypatch.setattr(type(tmp_path), "iterdir", limited_entries)

    result = ListDirectoryTool(tmp_path).execute({"path": ".", "max_items": 3})

    assert result.content.splitlines() == ["a", "m", "z"]
    assert result.metadata == {"count": 3, "truncated": True}


def test_listing_is_shallow(tmp_path, monkeypatch):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "nested.txt").write_text("not a root entry", encoding="utf-8")
    (tmp_path / "top.txt").touch()

    def forbid_recursive_listing(*args, **kwargs):
        raise AssertionError("directory listing must remain shallow")

    monkeypatch.setattr(type(tmp_path), "rglob", forbid_recursive_listing)

    result = ListDirectoryTool(tmp_path).execute({"path": "."})

    assert result.content.splitlines() == ["folder/", "top.txt"]
    assert result.metadata == {"count": 2, "truncated": False}


def test_listing_character_budget_flags_incomplete_names(tmp_path):
    for number in range(100):
        (tmp_path / (f"{number:03}-" + "x" * 230)).touch()

    result = ListDirectoryTool(tmp_path).execute({"path": "."})

    assert result.ok is True
    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.metadata["truncated"] is True


def test_listing_symlink_names_do_not_follow_directory_targets(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = tmp_path / "outside"
    target.mkdir()
    (target / "private.txt").write_text("private", encoding="utf-8")
    (workspace / "outside-link").symlink_to(target, target_is_directory=True)

    result = ListDirectoryTool(workspace).execute({"path": "."})

    assert result.content == "outside-link"
    assert result.metadata == {"count": 1, "truncated": False}


@pytest.mark.parametrize(
    "tool_class,field,base,maximum",
    [
        (ListDirectoryTool, "max_items", {"path": "."}, 100),
        (ReadFileTool, "max_lines", {"path": "config.py"}, 200),
        (SearchFilesTool, "max_matches", {"path": ".", "query": "RETRY"}, 100),
    ],
)
def test_navigation_invalid_budget_rejected_before_path_resolution(
    tmp_path, monkeypatch, tool_class, field, base, maximum
):
    import khosiness.tools.filesystem as filesystem

    registry = ToolRegistry()
    tool = tool_class(tmp_path)
    registry.register(tool)

    def forbid_resolution(*args, **kwargs):
        raise AssertionError("invalid arguments must fail before safe_path")

    monkeypatch.setattr(filesystem, "safe_path", forbid_resolution)
    invalid_arguments = [
        {**base, field: value}
        for value in [0, -1, maximum + 1, "3", True, 1.5]
    ] + [{**base, "unexpected": True}, {**base, "path": 7}]

    for arguments in invalid_arguments:
        result = registry.execute(ToolCall(id="invalid", name=tool.name, arguments=arguments))

        assert result.ok is False
        assert "ValidationError" in result.content, arguments


@pytest.mark.parametrize(
    "tool_class,field,maximum,required",
    [
        (ListDirectoryTool, "max_items", 100, {"path"}),
        (ReadFileTool, "max_lines", 200, {"path"}),
        (SearchFilesTool, "max_matches", 100, {"path", "query"}),
    ],
)
def test_navigation_published_schema_exposes_budget_contract(
    tmp_path, tool_class, field, maximum, required
):
    registry = ToolRegistry()
    registry.register(tool_class(tmp_path))

    schema = registry.schemas()[0]["parameters"]

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == required
    budget = schema["properties"][field]
    assert budget["type"] == "integer"
    assert budget["minimum"] == 1
    assert budget["maximum"] == maximum
    assert budget["default"] == maximum


@pytest.mark.parametrize(
    "tool_class,arguments",
    [
        (ListDirectoryTool, {"path": "outside-dir"}),
        (ReadFileTool, {"path": "outside-file"}),
        (SearchFilesTool, {"path": "outside-dir", "query": "private"}),
    ],
)
def test_navigation_rejects_symlink_root_before_target_access(
    tmp_path, monkeypatch, tool_class, arguments
):
    import khosiness.tools.filesystem as filesystem

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret.txt"
    secret.write_text("private", encoding="utf-8")
    (workspace / "outside-dir").symlink_to(outside, target_is_directory=True)
    (workspace / "outside-file").symlink_to(secret)
    tool = tool_class(workspace)
    registry = ToolRegistry()
    registry.register(tool)

    def forbid_target_access(*args, **kwargs):
        raise AssertionError("outside target must be rejected before reading/traversal")

    monkeypatch.setattr(filesystem, "read_text_bounded", forbid_target_access)
    monkeypatch.setattr(type(tmp_path), "iterdir", forbid_target_access)
    monkeypatch.setattr(type(tmp_path), "rglob", forbid_target_access)

    result = registry.execute(ToolCall(id="escape", name=tool.name, arguments=arguments))

    assert result.ok is False
    assert "path escapes workspace" in result.content


def test_search_files(tmp_path):
    (tmp_path / "config.py").write_text(
        "RETRY_COUNT = 3\n",
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute({"query": "RETRY", "path": "."})

    assert "config.py:1:RETRY_COUNT = 3" in result.content
    assert result.metadata == {
        "matches": [{"path": "config.py", "line": 1, "text": "RETRY_COUNT = 3"}],
        "truncated": False,
        "partial_match": False,
    }


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
        {"path": "a", "max_lines": 0},
        {"path": "a", "max_lines": MAX_READ_LINES + 1},
        {"path": "a", "max_lines": "2"},
        {"path": "a", "max_lines": True},
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

    assert result.content == "    2 | two\n    3 | three"
    assert result.metadata["path"] == "lines.txt"
    assert result.metadata["start_line"] == 2
    assert result.metadata["end_line"] == 3
    assert result.metadata["total_lines"] == 4
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
    assert result.metadata["partial_line"] is True
    assert result.metadata["end_line"] == 1

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


@pytest.mark.parametrize(
    "start,end,max_lines,numbers,truncated",
    [
        (2, 5, 2, [2, 3], True),
        (2, 3, 2, [2, 3], False),
        (5, None, 200, [5, 6], False),
        (6, 100, 200, [6], False),
        (9, None, 200, [], False),
    ],
)
def test_read_line_window_metadata(tmp_path, start, end, max_lines, numbers, truncated):
    (tmp_path / "lines.txt").write_text(
        "".join(f"line {number}\n" for number in range(1, 7)),
        encoding="utf-8",
    )

    result = ReadFileTool(tmp_path).execute(
        {
            "path": "lines.txt",
            "start_line": start,
            "end_line": end,
            "max_lines": max_lines,
        }
    )

    assert result.ok is True
    assert result.content == "\n".join(f"{n:>5} | line {n}" for n in numbers)
    assert result.metadata["start_line"] == (numbers[0] if numbers else None)
    assert result.metadata["end_line"] == (numbers[-1] if numbers else None)
    assert result.metadata["total_lines"] == 6
    assert result.metadata["truncated"] is truncated
    assert result.metadata["partial_line"] is False


def test_read_default_line_limit(tmp_path):
    (tmp_path / "many.txt").write_text("x\n" * (MAX_READ_LINES + 1), encoding="utf-8")

    result = ReadFileTool(tmp_path).execute({"path": "many.txt"})

    assert len(result.content.splitlines()) == MAX_READ_LINES
    assert result.metadata["end_line"] == MAX_READ_LINES
    assert result.metadata["total_lines"] == MAX_READ_LINES + 1
    assert result.metadata["truncated"] is True
    assert result.metadata["partial_line"] is False


def test_read_empty_file_has_no_returned_range(tmp_path):
    (tmp_path / "empty.txt").touch()

    result = ReadFileTool(tmp_path).execute({"path": "empty.txt"})

    assert result.ok is True
    assert result.content == ""
    assert result.metadata["start_line"] is None
    assert result.metadata["end_line"] is None
    assert result.metadata["total_lines"] == 0
    assert result.metadata["truncated"] is False


def test_read_character_cap_tracks_partial_last_line(tmp_path):
    (tmp_path / "long.txt").write_text(
        "short\n" + "x" * MAX_OUTPUT_CHARS + "\nunseen\n",
        encoding="utf-8",
    )

    result = ReadFileTool(tmp_path).execute({"path": "long.txt"})

    assert result.content.startswith("    1 | short\n    2 | ")
    assert len(result.content) == MAX_OUTPUT_CHARS
    assert "unseen" not in result.content
    assert result.metadata["end_line"] == 2
    assert result.metadata["total_lines"] == 3
    assert result.metadata["partial_line"] is True
    assert result.metadata["truncated"] is True


def test_read_character_cap_does_not_emit_partial_citation_prefix(tmp_path):
    first = "x" * (MAX_OUTPUT_CHARS - len("    1 | ") - 3)
    (tmp_path / "boundary.txt").write_text(first + "\nhidden\n", encoding="utf-8")

    result = ReadFileTool(tmp_path).execute({"path": "boundary.txt"})

    assert result.content == "    1 | " + first
    assert result.metadata["end_line"] == 1
    assert result.metadata["total_lines"] == 2
    assert result.metadata["partial_line"] is False
    assert result.metadata["truncated"] is True


def test_read_preserves_blank_lines_and_indentation(tmp_path):
    (tmp_path / "blank.py").write_text("\n    retry = 3\n", encoding="utf-8")

    result = ReadFileTool(tmp_path).execute({"path": "blank.py"})

    assert result.content == "    1 | \n    2 |     retry = 3"
    assert result.metadata["total_lines"] == 2
    assert result.metadata["truncated"] is False


def test_search_match_limit(tmp_path):
    (tmp_path / "many.txt").write_text(
        "RETRY\n" * 101,
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content.splitlines()) == 100
    assert len(result.metadata["matches"]) == 100
    assert result.metadata["truncated"] is True


def test_search_character_limit(tmp_path):
    (tmp_path / "long.txt").write_text(
        "RETRY" + "x" * MAX_OUTPUT_CHARS,
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert result.metadata["truncated"] is True
    assert result.metadata["partial_match"] is True
    match = result.metadata["matches"][0]
    assert match["path"] == "long.txt" and match["line"] == 1
    assert result.content == f"long.txt:1:{match['text']}"
    assert len(match["text"]) < MAX_OUTPUT_CHARS


@pytest.mark.parametrize("budget,count,truncated", [(1, 1, True), (2, 2, True), (3, 3, True), (100, 3, False)])
def test_search_requested_match_limit(tmp_path, budget, count, truncated):
    (tmp_path / "hits.py").write_text(
        "  RETRY = 1\n  RETRY = 2\n  RETRY = 3\n",
        encoding="utf-8",
    )

    result = SearchFilesTool(tmp_path).execute(
        {"path": ".", "query": "RETRY", "max_matches": budget}
    )

    expected = [
        {"path": "hits.py", "line": n, "text": f"  RETRY = {n}"}
        for n in range(1, count + 1)
    ]
    assert result.metadata["matches"] == expected
    assert result.content == "\n".join(
        f"{m['path']}:{m['line']}:{m['text']}" for m in expected
    )
    assert result.metadata["truncated"] is truncated
    assert result.metadata["partial_match"] is False


def test_search_stops_before_reading_later_files_at_match_limit(tmp_path, monkeypatch):
    import khosiness.tools.filesystem as filesystem

    first = tmp_path / "first.txt"
    later = tmp_path / "later.txt"
    first.write_text("RETRY\n", encoding="utf-8")
    later.write_text("RETRY\n", encoding="utf-8")
    original = filesystem.read_text_bounded
    read_paths = []

    def observe_read(path):
        read_paths.append(path)
        assert path != later, "the match budget must stop later file reads"
        return original(path)

    monkeypatch.setattr(type(tmp_path), "rglob", lambda self, pattern: iter([first, later]))
    monkeypatch.setattr(filesystem, "read_text_bounded", observe_read)

    result = SearchFilesTool(tmp_path).execute(
        {"path": ".", "query": "RETRY", "max_matches": 1}
    )

    assert read_paths == [first]
    assert len(result.metadata["matches"]) == 1
    assert result.metadata["truncated"] is True


def test_search_character_limit_omits_match_if_citation_cannot_fit(tmp_path):
    prefix = "hits.txt:1:"
    first = "RETRY" + "x" * (MAX_OUTPUT_CHARS - len(prefix) - 3 - len("RETRY"))
    (tmp_path / "hits.txt").write_text(first + "\nRETRY second\n", encoding="utf-8")

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert result.content == prefix + first
    assert result.metadata["matches"] == [{"path": "hits.txt", "line": 1, "text": first}]
    assert result.metadata["truncated"] is True
    assert result.metadata["partial_match"] is False


def test_search_partial_text_may_end_before_query(tmp_path):
    (tmp_path / "late.txt").write_text(
        "x" * MAX_OUTPUT_CHARS + "RETRY\n", encoding="utf-8"
    )

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert len(result.content) == MAX_OUTPUT_CHARS
    assert "RETRY" not in result.metadata["matches"][0]["text"]
    assert result.metadata["partial_match"] is True
    assert result.metadata["truncated"] is True


@pytest.mark.parametrize("budget", [0, 101, "1", True])
def test_search_invalid_match_limit_rejected_before_traversal(tmp_path, monkeypatch, budget):
    def forbid_traversal(*args, **kwargs):
        raise AssertionError("invalid arguments must be rejected before traversal")

    monkeypatch.setattr(type(tmp_path), "rglob", forbid_traversal)
    registry = ToolRegistry()
    registry.register(SearchFilesTool(tmp_path))

    result = registry.execute(
        ToolCall(
            id="invalid-search",
            name="search_files",
            arguments={"path": ".", "query": "RETRY", "max_matches": budget},
        )
    )

    assert result.ok is False
    assert "ValidationError" in result.content


def test_search_skips_non_utf8_and_preserves_source_whitespace(tmp_path):
    (tmp_path / "binary.bin").write_bytes(b"RETRY\xff")
    source = "    RETRY = '✓'"
    (tmp_path / "config.py").write_text(source + "\n", encoding="utf-8")

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert result.metadata["matches"] == [{"path": "config.py", "line": 1, "text": source}]
    assert result.content == "config.py:1:" + source
    assert result.metadata["truncated"] is False


def test_search_no_matches_returns_empty_metadata(tmp_path):
    (tmp_path / "config.py").write_text("TIMEOUT = 5\n", encoding="utf-8")

    result = SearchFilesTool(tmp_path).execute({"path": ".", "query": "RETRY"})

    assert result.ok is True
    assert result.content == ""
    assert result.metadata == {"matches": [], "truncated": False, "partial_match": False}


def test_search_rejects_oversized_file(tmp_path):
    (tmp_path / "large.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
    registry = ToolRegistry()
    registry.register(SearchFilesTool(tmp_path))

    result = registry.execute(
        ToolCall(id="large-search", name="search_files", arguments={"path": ".", "query": "x"})
    )

    assert result.ok is False
    assert "byte limit" in result.content


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
