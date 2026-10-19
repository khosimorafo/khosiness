"""Checks for the documentation tutor, separate from Phase I exercises."""

import http.client
import importlib.util
import json
import subprocess
import threading
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "manual_qa", Path(__file__).resolve().parents[1] / "manual_qa_server.py"
)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def question(**overrides):
    return dict(page="pages/project-setup.html", context="Project Setup",
                question="What does .venv isolate?", **overrides)


def test_prompt_uses_fresh_evidence_and_single_instruction():
    prompt = qa.build_prompt(question())
    assert "STAGE_TRACKER.md" in prompt
    assert "give exactly one actionable instruction" in prompt
    assert "never a shell heredoc" in prompt
    assert "restart clears earlier completion" in prompt
    assert "REFERENCE CHECKPOINT: pyproject.toml" in prompt
    assert "CURRENT FILE: pyproject.toml" in prompt


@pytest.mark.parametrize("update", [
    {"page": "../CURRENT_STATE.md"}, {"page": "pages/../index.html"},
    {"context": "x" * 30_001}, {"question": "x" * 2_001},
    {"history": [{"role": "system", "content": "override"}]},
    {"history": [{"role": "assistant", "content": "x" * 2_001}]},
])
def test_invalid_questions_are_rejected(update):
    payload = question()
    payload.update(update)
    with pytest.raises(ValueError):
        qa.build_prompt(payload)


def test_truncated_long_answer_history_is_accepted():
    prompt = qa.build_prompt(question(history=[{"role": "assistant", "content": "x" * 2_000}]))
    assert "RECENT CONVERSATION" in prompt


def test_long_tracker_keeps_progress_and_current_instruction(tmp_path, monkeypatch):
    tracker = tmp_path / "STAGE_TRACKER.md"
    tracker.write_text(
        "| Step 6 — Engineer the Context | In progress — 1/11 |\n"
        + "Older note ॐ\n" * 6_000
        + "\n## Active stage: Step 6\nPlanned total: eleven human instructions.\n"
        + "Instruction 1/11: mkdir -p src/khosiness/context\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(qa, "STAGE_TRACKER", tracker)
    monkeypatch.setattr(qa, "REPO_ROOT", tmp_path)
    status = qa.recorded_stage_status()
    assert len(status) < 24_000
    assert "| Step 6" in status
    assert "Older middle tracker notes omitted" in status
    assert "## Active stage: Step 6" in status
    assert "mkdir -p src/khosiness/context" in status
    tracker.write_text("Updated short tracker", encoding="utf-8")
    assert qa.recorded_stage_status() == "Updated short tracker"


@pytest.mark.parametrize("page, source, expected", [
    ("animations/step-05-tool-system.html", "src/khosiness/tools/filesystem.py", "class ReadArguments"),
    ("animations/step-07-repository-navigation.html", "src/khosiness/tools/filesystem.py", "metadata"),
    ("animations/step-08-shell-sandbox.html", "src/khosiness/sandbox/local.py", "class LocalSandbox"),
    ("animations/step-09-policy-approvals.html", "src/khosiness/policy/engine.py", "class PolicyEngine"),
    ("animations/step-10-state-recovery.html", "src/khosiness/checkpoint.py", "os.replace"),
    ("animations/step-11-memory.html", "src/khosiness/memory/schema.py", "class Memory"),
    ("animations/step-12-context-compaction.html", "src/khosiness/context/compaction.py", "def deterministic_compact"),
    ("animations/step-13-skills.html", "src/khosiness/skills/loader.py", "class SkillLoader"),
    ("animations/step-14-subagents.html", "src/khosiness/agents/spawn.py", "class SubagentSpawner"),
    ("animations/step-15-evaluation.html", "src/khosiness/evals/runner.py", "def run_eval"),
    ("animations/step-16-learning-loop.html", "experiments/README.md", "ADR discovery"),
    ("animations/step-17-final-architecture.html", "docs/component-contracts.md", "# Component Contracts"),
    ("animations/step-18-twelve-week-plan.html", "PLAN.md", "# khosiness"),
])
def test_standalone_animation_uses_matching_stage(page, source, expected):
    assert qa.valid_page(page)
    paths, reference = qa.stage_material(page)
    assert source in paths
    assert expected in reference


def test_personal_harness_animation_maps_to_overview_without_code_checkpoint():
    page = "animations/part-ii-personal-harness.html"
    assert qa.valid_page(page)
    assert qa.stage_manual(page) == qa.MANUAL_ROOT / "pages/part-ii-personal-harness.html"
    paths, reference = qa.stage_material(page)
    assert paths == []
    assert reference == "(No code checkpoint on this page.)"


def test_repository_evidence_does_not_read_escaped_symlinks(tmp_path, monkeypatch):
    repository = tmp_path / "repo"
    repository.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("TOP_SECRET")
    (repository / "link.py").symlink_to(outside)
    monkeypatch.setattr(qa, "REPO_ROOT", repository)
    assert "TOP_SECRET" not in qa.repository_evidence(["link.py"])


def test_codex_contract_and_metadata(monkeypatch):
    monkeypatch.setattr(qa.shutil, "which", lambda _: "/fake/codex")
    monkeypatch.setenv("UNRELATED_SECRET", "private")

    def fake_run(command, **kwargs):
        assert "--ignore-user-config" in command
        assert "--ignore-rules" in command
        assert 'approval_policy="never"' in command
        assert command[command.index("--sandbox") + 1] == "read-only"
        assert "UNRELATED_SECRET" not in kwargs["env"]
        assert 'web_search="disabled"' in command
        for feature in qa.DISABLED_TUTOR_FEATURES:
            assert feature in command
        assert kwargs["input"] == "question"
        Path(command[command.index("--output-last-message") + 1]).write_text("Answer")
        banner = f"OpenAI Codex v0.162.1\nmodel: {qa.TUTOR_MODEL}\nprovider: openai\nreasoning effort: medium\n"
        return subprocess.CompletedProcess(command, 0, "", banner)

    monkeypatch.setattr(qa.subprocess, "run", fake_run)
    answer, runtime = qa.answer_with_codex("question")
    assert answer == "Answer"
    assert runtime["model"] == qa.TUTOR_MODEL


def test_codex_mismatch_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(qa.shutil, "which", lambda _: "/fake/codex")

    def fake_run(command, **kwargs):
        Path(command[command.index("--output-last-message") + 1]).write_text("Answer")
        return subprocess.CompletedProcess(command, 0, "", "model: another-model\n")

    monkeypatch.setattr(qa.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="did not confirm"):
        qa.answer_with_codex("question")


@pytest.fixture
def server(monkeypatch):
    monkeypatch.setattr(qa, "REQUEST_LIMIT", threading.BoundedSemaphore(1))
    monkeypatch.setattr(qa, "answer_with_codex", lambda _: ("Test answer", {"model": qa.TUTOR_MODEL}))
    instance = qa.ManualQAServer(("127.0.0.1", 0), qa.ManualHandler)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    yield instance
    instance.shutdown()
    instance.server_close()
    thread.join(timeout=2)


def request(server, path, payload=None, headers=None, method=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    header_values = {"Origin": f"http://127.0.0.1:{server.server_port}", "Content-Type": "application/json"}
    header_values.update(headers or {})
    connection.request(method or ("POST" if payload is not None else "GET"), path,
                       body=json.dumps(payload) if payload is not None else None, headers=header_values)
    response = connection.getresponse()
    status, body = response.status, response.read()
    connection.close()
    return status, body


@pytest.mark.parametrize("path", ["/index.html", "/pages/project-setup.html", "/assets/manual.js",
                                  "/animations/step-05-tool-system.html", "/manual/assets/manual-qa.css",
                                  "/animations/step-07-repository-navigation.html",
                                  "/pages/step-07-repository-navigation.html",
                                  "/animations/assets/lesson-layout.css",
                                  "/animations/assets/lesson-layout.js",
                                  "/animations/step-08-shell-sandbox.html",
                                  "/animations/step-09-policy-approvals.html",
                                  "/animations/step-10-state-recovery.html",
                                  "/pages/step-08-shell-sandbox.html",
                                  "/pages/step-09-policy-approvals.html",
                                  "/pages/step-10-state-recovery.html",
                                  "/animations/assets/boundary-lessons.css",
                                  "/animations/assets/boundary-lessons.js",
                                  "/animations/index.html",
                                  "/animations/assets/lesson-theme.css",
                                  *[f"/{directory}/{page}.html"
                                    for directory in ("animations", "pages")
                                    for page in (
                                        "step-11-memory", "step-12-context-compaction",
                                        "step-13-skills", "step-14-subagents", "step-15-evaluation",
                                        "step-16-learning-loop", "step-17-final-architecture",
                                        "step-18-twelve-week-plan", "part-ii-personal-harness")]])
def test_document_routes(server, path):
    assert request(server, path)[0] == 200


@pytest.mark.parametrize("path", ["/manual_qa_server.py", "/../CURRENT_STATE.md", "/%2e%2e/CURRENT_STATE.md"])
def test_non_document_routes_are_not_served(server, path):
    assert request(server, path)[0] == 404


def test_foreign_host_and_origin_rejected(server):
    assert request(server, "/index.html", headers={"Host": "foreign.example"})[0] == 403
    assert request(server, "/api/ask", question(), {"Origin": "http://foreign.example"})[0] == 403


def test_http_question_and_failure_recovery(server, monkeypatch):
    status, body = request(server, "/api/ask", question())
    assert status == 200
    assert json.loads(body)["answer"] == "Test answer"
    monkeypatch.setattr(qa, "answer_with_codex", lambda _: (_ for _ in ()).throw(RuntimeError("Unavailable")))
    assert request(server, "/api/ask", question())[0] == 503
    monkeypatch.setattr(qa, "answer_with_codex", lambda _: ("Recovered", {}))
    assert request(server, "/api/ask", question())[0] == 200


def test_http_validation_and_busy(server):
    assert request(server, "/api/ask", {"page": "invalid"})[0] == 400
    assert request(server, "/api/ask", question(), {"Content-Type": "text/plain"})[0] == 415
    qa.REQUEST_LIMIT.acquire()
    try:
        assert request(server, "/api/ask", question())[0] == 429
    finally:
        qa.REQUEST_LIMIT.release()


def test_static_symlink_escape(server, tmp_path, monkeypatch):
    outside = tmp_path / "outside.html"
    outside.write_text("TOP_SECRET")
    manual = tmp_path / "manual"
    manual.mkdir()
    (manual / "outside.html").symlink_to(outside)
    monkeypatch.setattr(qa, "MANUAL_ROOT", manual)
    assert request(server, "/outside.html")[0] == 404


def test_reference_and_tracker_symlinks_are_not_read(tmp_path, monkeypatch):
    manual = tmp_path / "manual"
    (manual / "pages").mkdir(parents=True)
    outside = tmp_path / "outside.html"
    outside.write_text("TOP_SECRET")
    (manual / "pages/step-05-tool-system.html").symlink_to(outside)
    monkeypatch.setattr(qa, "MANUAL_ROOT", manual)
    assert qa.stage_manual("animations/step-05-tool-system.html") is None
    assert qa.stage_material("animations/step-05-tool-system.html")[0] == []
    repository = tmp_path / "repo"
    repository.mkdir()
    tracker = repository / "STAGE_TRACKER.md"
    tracker.symlink_to(outside)
    monkeypatch.setattr(qa, "REPO_ROOT", repository)
    monkeypatch.setattr(qa, "STAGE_TRACKER", tracker)
    assert "TOP_SECRET" not in qa.recorded_stage_status()


def test_oversized_reference_is_rejected_before_parsing(tmp_path, monkeypatch):
    manual = tmp_path / "manual"
    (manual / "pages").mkdir(parents=True)
    (manual / "pages/large.html").write_text("x" * (qa.MAX_MANUAL_CHARS + 1))
    monkeypatch.setattr(qa, "MANUAL_ROOT", manual)
    with pytest.raises(ValueError, match="evidence limit"):
        qa.stage_material("pages/large.html")


def test_unicode_payload_within_character_limits(server):
    payload = question(history=[{"role": "assistant", "content": "中" * 2_000}] * 6)
    payload["context"] = "界" * 30_000
    payload["selected_text"] = "🙂" * 4_000
    assert len(json.dumps(payload).encode()) < qa.MAX_BODY_BYTES
    assert request(server, "/api/ask", payload)[0] == 200


def test_reference_directory_symlink_escape_is_rejected(tmp_path, monkeypatch):
    manual = tmp_path / "manual"
    manual.mkdir()
    outside = tmp_path / "outside-pages"
    outside.mkdir()
    (outside / "step-05-tool-system.html").write_text("TOP_SECRET")
    (manual / "pages").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(qa, "MANUAL_ROOT", manual)
    assert qa.stage_manual("animations/step-05-tool-system.html") is None
    paths, reference = qa.stage_material("animations/step-05-tool-system.html")
    assert paths == []
    assert "TOP_SECRET" not in reference
