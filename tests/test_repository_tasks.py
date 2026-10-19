"""Deterministic navigation over source fixtures; the fixture code is never run."""

from pathlib import Path

import pytest

from khosiness.models.base import ToolCall
from khosiness.tools.filesystem import ListDirectoryTool, ReadFileTool, SearchFilesTool
from khosiness.tools.registry import ToolRegistry


SAMPLE_FILES = {
    "README.md": (
        "# Fixture service\n\n"
        "Retries are configured in src/db/config.py.\n"
    ),
    "pyproject.toml": (
        '[project]\nname = "fixture-service"\nversion = "0.1.0"\n\n'
        '[project.scripts]\nfixture-check = "src.cli:main"\n'
    ),
    "docs/design.md": (
        "# Design notes\n\n"
        "The database layer creates sessions from configuration.\n"
    ),
    "src/db/config.py": "DB_RETRY_COUNT = 3\nDB_TIMEOUT_SECONDS = 5\n",
    "src/db/session.py": (
        "from .config import DB_RETRY_COUNT, DB_TIMEOUT_SECONDS\n\n"
        "def create_session():\n"
        '    return {"retries": DB_RETRY_COUNT, "timeout": DB_TIMEOUT_SECONDS}\n'
    ),
    "src/service/worker.py": (
        "from src.db.session import create_session\n\n"
        "def run():\n"
        "    return create_session()\n"
    ),
    "src/service/notes.py": "# Planned call: create_session()\n",
    "src/api/health.py": (
        "from src.db.session import create_session\n\n"
        "def readiness():\n"
        "    session = create_session()\n"
        '    return session["timeout"] > 0\n'
    ),
    "src/cli.py": (
        "from src.service.worker import run\n\n"
        "def main():\n"
        "    return run()\n"
    ),
}


def build_sample_repo(workspace: Path) -> Path:
    for relative, content in SAMPLE_FILES.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return workspace


@pytest.fixture
def sample_repo(tmp_path):
    return build_sample_repo(tmp_path / "repo")


@pytest.fixture
def tools(sample_repo):
    registry = ToolRegistry()
    for tool_class in (ListDirectoryTool, ReadFileTool, SearchFilesTool):
        registry.register(tool_class(sample_repo))
    return registry


def test_search_returns_source_path_line_and_text(tools):
    result = tools.execute(
        ToolCall(
            id="find-setting",
            name="search_files",
            arguments={"path": "src/db", "query": "DB_RETRY_COUNT"},
        )
    )

    assert result.ok is True
    assert result.metadata["truncated"] is False
    assert result.metadata["partial_match"] is False
    matches = result.metadata["matches"]
    assert len(matches) == 3
    definition = next(match for match in matches if match["path"] == "src/db/config.py")
    assert definition == {
        "path": "src/db/config.py",
        "line": 1,
        "text": "DB_RETRY_COUNT = 3",
    }
    for match in matches:
        expected_source = SAMPLE_FILES[match["path"]].splitlines()[match["line"] - 1]
        assert match["text"] == expected_source


def test_read_file_returns_numbered_source_range(tools):
    result = tools.execute(
        ToolCall(
            id="read-worker",
            name="read_file",
            arguments={"path": "src/service/worker.py", "start_line": 3, "end_line": 4},
        )
    )

    assert result.ok is True
    assert result.content == "    3 | def run():\n    4 |     return create_session()"
    assert result.metadata["path"] == "src/service/worker.py"
    assert result.metadata["start_line"] == 3
    assert result.metadata["end_line"] == 4
    assert result.metadata["truncated"] is False


def test_directory_listing_returns_a_bounded_shallow_map(tools):
    result = tools.execute(
        ToolCall(id="orient", name="list_directory", arguments={"path": ".", "max_items": 3})
    )

    assert result.ok is True
    entries = result.content.splitlines()
    assert len(entries) == 3
    assert set(entries) <= {"README.md", "pyproject.toml", "src/", "docs/"}
    assert result.metadata == {"count": 3, "truncated": True}


def test_search_then_read_keeps_tool_reads_in_the_requested_subtree(sample_repo, tools, monkeypatch):
    import khosiness.tools.filesystem as filesystem

    original_read = filesystem.read_text_bounded
    read_paths = []

    def observe_read(path):
        assert path.is_relative_to(sample_repo / "src/db"), "unrelated subtree was opened"
        read_paths.append(path)
        return original_read(path)

    monkeypatch.setattr(filesystem, "read_text_bounded", observe_read)

    listing = tools.execute(
        ToolCall(id="orient", name="list_directory", arguments={"path": "."})
    )
    assert listing.ok is True
    assert read_paths == []

    search = tools.execute(
        ToolCall(
            id="search-db",
            name="search_files",
            arguments={"path": "src/db", "query": "DB_RETRY_COUNT"},
        )
    )
    assert search.ok is True
    assert search.metadata["truncated"] is False
    definition = next(
        match for match in search.metadata["matches"]
        if match["path"] == "src/db/config.py" and match["text"].startswith("DB_RETRY_COUNT =")
    )
    evidence = tools.execute(
        ToolCall(
            id="verify-definition",
            name="read_file",
            arguments={
                "path": definition["path"],
                "start_line": definition["line"],
                "end_line": definition["line"],
                "max_lines": 1,
            },
        )
    )

    assert evidence.ok is True
    assert evidence.content == "    1 | DB_RETRY_COUNT = 3"
    assert evidence.metadata["end_line"] == 1
    assert evidence.metadata["total_lines"] == 2
    assert evidence.metadata["truncated"] is False
    assert set(read_paths) == {
        sample_repo / "src/db/config.py", sample_repo / "src/db/session.py"
    }
    assert len(read_paths) == 3  # Two scoped search reads, one follow-up file read.


def test_source_reads_verify_setting_use_and_two_callers(tools):
    search = tools.execute(
        ToolCall(
            id="caller-candidates",
            name="search_files",
            arguments={"path": "src", "query": "create_session()"},
        )
    )
    assert search.ok is True
    assert search.metadata["truncated"] is False
    candidates = {
        (match["path"], match["line"]): match["text"]
        for match in search.metadata["matches"]
    }
    assert set(candidates) == {
        ("src/db/session.py", 3),
        ("src/service/worker.py", 4),
        ("src/api/health.py", 4),
        ("src/service/notes.py", 1),
    }
    assert candidates[("src/db/session.py", 3)].startswith("def ")
    assert candidates[("src/service/notes.py", 1)].startswith("# ")

    excerpts = {}
    for path, start, end in [
        ("src/db/session.py", 1, 4),
        ("src/service/worker.py", 3, 4),
        ("src/api/health.py", 3, 5),
        ("src/service/notes.py", 1, 1),
    ]:
        read = tools.execute(
            ToolCall(
                id=f"verify-{path}",
                name="read_file",
                arguments={"path": path, "start_line": start, "end_line": end},
            )
        )
        assert read.ok is True
        assert read.metadata["truncated"] is False
        excerpts[path] = read.content

    assert "    1 | from .config import DB_RETRY_COUNT" in excerpts["src/db/session.py"]
    assert '"retries": DB_RETRY_COUNT' in excerpts["src/db/session.py"]
    assert "    4 |     return create_session()" in excerpts["src/service/worker.py"]
    assert "    4 |     session = create_session()" in excerpts["src/api/health.py"]
    assert excerpts["src/service/notes.py"] == "    1 | # Planned call: create_session()"
    # These are fixture-specific source assertions, not a general caller analyzer
    # or proof that the application executes either caller on a particular run.


def test_capped_repository_search_returns_only_a_candidate_subset(tools):
    result = tools.execute(
        ToolCall(
            id="bounded-candidates",
            name="search_files",
            arguments={"path": "src", "query": "create_session", "max_matches": 2},
        )
    )

    assert result.ok is True
    assert len(result.metadata["matches"]) == 2
    assert result.metadata["truncated"] is True
    assert result.metadata["partial_match"] is False
    all_locations = {
        ("src/db/session.py", 3),
        ("src/service/worker.py", 1), ("src/service/worker.py", 4),
        ("src/api/health.py", 1), ("src/api/health.py", 4),
        ("src/service/notes.py", 1),
    }
    returned = {(match["path"], match["line"]) for match in result.metadata["matches"]}
    assert returned < all_locations


def test_outside_read_is_a_failed_result_before_file_access(sample_repo, tools, monkeypatch):
    import khosiness.tools.filesystem as filesystem

    (sample_repo.parent / "outside.txt").write_text("private fixture data", encoding="utf-8")

    def forbid_read(path):
        raise AssertionError("outside file must not be read")

    monkeypatch.setattr(filesystem, "read_text_bounded", forbid_read)
    result = tools.execute(
        ToolCall(id="outside", name="read_file", arguments={"path": "../outside.txt"})
    )

    assert result.ok is False
    assert result.content == "ValueError: path escapes workspace"
    assert result.metadata == {}


def test_missing_source_is_not_successful_evidence(tools):
    result = tools.execute(
        ToolCall(id="missing", name="read_file", arguments={"path": "src/db/missing.py"})
    )

    assert result.ok is False
    assert "not a file" in result.content
    assert result.metadata == {}
