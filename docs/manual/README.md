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

From the repository root, start the tutor:

```bash
python docs/manual/manual_qa_server.py
```

Then open `http://127.0.0.1:8765/index.html` and navigate to any stage. The
button sends the current page's text, your question and recent questions from
that browser tab to the signed-in Codex CLI. Codex must be installed and
`codex login status` must report that you are signed in. The CLI is run from an
empty temporary directory with a read-only sandbox. The browser does not hold
an API key, and the tutor does not store chat history on disk.

Opening a page with `file:///` still works for reading and shows instructions
for switching to the local server when you want to ask questions. The
self-contained single-file artifact remains a static reference without the
question panel.
