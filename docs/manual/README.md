# khosiness implementation manual

Open index.html for the multi-page manual or the static single-file edition
in single-file/khosiness-harness-engineering-manual.html. Animations remain
usable on their own and embedded on their matching pages.

Every numbered step (0–18) and the Part II overview now has a visual lesson.
Use [the visual lesson directory](../animations/index.html) to browse them.
Steps 11–18 and Part II each add eight self-paced scenes with a concrete
task, explicit responsibility boundaries, a failed or rejected path, and
an inspectable trace or state distinction. They reuse the approved layout
and existing playback/fullscreen controls. Later examples remain conceptual;
they do not create runtime capabilities, experiments, or stage credit.
Reference notes on the matching pages identify missing integration and
contract gaps before those stages are implemented.

Step 6 now includes an eight-scene context-selection lesson. It is a
conceptual simulation, including the reference budget guard; it does
not implement the context builder. Playback starts paused.

Step 7 includes an eight-scene repository-navigation lesson: shallow
listing, scoped search, numbered reads, caller verification, incomplete
results, and a rejected outside-workspace path. Its outputs are illustrative;
the numbered/structured/configurable interfaces are planned additions.
The live Step 5 safeguards must be preserved during implementation.

Steps 8, 9, and 10 each include an eight-scene conceptual lesson covering
execution controls, policy/approval decisions, and checkpoint recovery.
They preserve the desktop layout below and run no commands, approvals,
or checkpoint writes. Each page explains the gaps between the reference
helpers and enforced execution, authorization, or safe recovery.

## Animation layout standard

All later animations must preserve the approved Step 6/7 layout: diagram
and explanation beside each other on desktop, with controls alongside and
the complete active scene readable on one screen. Organize content and
remove wasted space instead of shrinking text, scaling, or clipping it.
The primer stays above the animation; it is outside the one-screen target.

Reuse [the shared layout stylesheet](../animations/assets/lesson-layout.css)
and [fullscreen control](../animations/assets/lesson-layout.js) where
applicable. Keep **Expand lesson**, iframe `allowfullscreen`, an exit
control, and Escape support. Fullscreen starts at the top and permits
scrolling when a short window or enlarged text needs it. Mobile uses a
readable stacked layout with vertical scrolling and no horizontal overflow.

Before handing off a lesson, inspect every scene at 1366x768, 1440x900,
and 1920x1080 for vertical fit, visible controls, and unclipped text/code.
Check embedded fullscreen at 1366x768 and inspect screenshots. Preserve
keyboard access, reduced motion, no-JavaScript reading, and the tutor panel
behavior. The full standing rule is in [AGENTS.md](../../AGENTS.md#animation-layout-standard).

## Optional local Q&A

From the project directory, run:

```bash
python docs/manual/manual_qa_server.py
```

Open http://127.0.0.1:8765/index.html and select **Ask about this page**.
Press Enter to submit a question, or Shift+Enter to insert a new line.
Enter during input-method composition does not submit.
The restored tutor uses the signed-in Codex CLI, requesting gpt-6-sol with
medium reasoning effort and displaying the confirmed runtime metadata.
Questions include the current page, selected text, recent conversation in
that tab, the fresh stage tracker, and bounded repository/reference excerpts.
The server rereads evidence on each request. Chat history is not stored on
disk; reload a tab after a tutoring restart.
Long tracker excerpts retain the progress summary and newest stage notes;
omitted middle history is explicitly labeled.

Codex must be installed and signed in. It runs ephemerally from a temporary
directory with user config/rules ignored, approval disabled, and a read-only
sandbox. Command execution, code execution, image reads, browser access,
plugins/apps, web search, hooks, and delegation are disabled for tutor
requests. The tutor answers from supplied evidence; read-only is an
additional write guard, not a substitute for disabling capabilities.
These settings follow the installed CLI and the [official configuration
reference](https://learn.chatgpt.com/docs/config-file/config-reference).
The service binds only to localhost.
Only manual/animation browser assets are served. Stop it with Ctrl+C.

Opening a page through file:/// still works for reading; its question panel
explains how to start the server. The single-file edition remains static.
The service is documentation tooling, not a khosiness harness stage.

## Tutoring cadence

STAGE_TRACKER.md records actual progress; the manual describes requirements.
Follow one actionable instruction at a time, with recorded N/Y progress.
Multiline edits use an editor command and separate code block. The tutor
must not infer completed exercises or understanding from reference code.

Only Setup and Step 0 expect an empty pytest suite (exit status 5). From
Step 1 onward, collected tests must pass with exit status 0.

## Verification

Documentation-only tests run with:

```bash
.venv/bin/python -m pytest -q docs/manual/tests
```

They do not count as Phase I exercise implementation or understanding credit.
