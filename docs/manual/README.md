# khosiness implementation manual

This directory contains two equivalent forms of the latest manual:

- `index.html` + `pages/` + `assets/`: a conventional multi-page local documentation site.
- `single-file/khosiness-harness-engineering-manual.html`: the self-contained artifact version used in ChatGPT.

The multi-page site is the easiest form to inspect or edit from a terminal/editor. Open `index.html` in a browser. All links are relative and work from a normal filesystem or static HTTP server.

The manual is authoritative for the Phase I sequence unless a later explicit decision in `PROJECT_HISTORY.md` supersedes it.

## Ask questions inside a stage page

The multi-page manual has an **Ask about this page** button on the overview and
every dedicated stage page. It uses a separate local tutor service; it does not
run the khosiness harness being built in Phase I.
The Step 0 page embeds its conceptual animation. The same animation also has
an **Ask about this page** button when opened on its own. Future stage
animations belong on their matching pages.
Use **Expand** in the tutor header for a reading panel that reaches the top
and sits to the right of the content cards on wide pages; **Restore** returns
it to its compact size.

From the repository root, start the tutor:

```bash
python docs/manual/manual_qa_server.py
```

Then open `http://127.0.0.1:8765/index.html` and navigate to any stage. The
button sends the current page's text, your question, any selected text, and
recent questions and answers from that browser tab to the signed-in Codex CLI.
The local server adds `STAGE_TRACKER.md` to each question so the tutor can
answer progress questions from the recorded stage status rather than guessing
from a manual page. It also adds a bounded read of the stage's listed files
and the matching manual code checkpoint. This lets the tutor identify missing
code and suggest short, exact snippets while clearly separating existing code
from reference code. The files and tracker are read afresh for each question.
For roadmap questions, it can also compare the next pending stage even when
you are still viewing a completed stage.
The tutor is instructed to suggest commands and code without executing them;
the read-only sandbox blocks writes. For implementation guidance, it gives no
more than three steps at a time.
Codex must be installed and
`codex login status` must report that you are signed in. The CLI is run from an
empty temporary directory with a read-only sandbox. This blocks writes but
does not prevent it from reading files your user can read; the tutor prompt
instructs it not to inspect files. The browser does not hold an API key, and
the tutor does not store chat history on disk.
The tutor starts Codex with `--ignore-user-config`, so model and effort values
in `~/.codex/config.toml` do not apply. After each answer, the panel displays
the model and reasoning-effort setting reported by that CLI invocation. A CLI
report of `none` means no explicit effort setting was reported; it does not
establish an API-level `none` reasoning mode.
No model snapshot is pinned, so the reported default may change with CLI or
account updates.

Opening a page with `file:///` still works for reading and shows instructions
for switching to the local server when you want to ask questions. The
self-contained single-file artifact remains a static reference without the
question panel.
