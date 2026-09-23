# khosiness Codex handoff

> Historical handoff instructions, written before Step 0. For current progress,
> read `STAGE_TRACKER.md` and inspect Git status.

This package moves the complete latest khosiness project context into a terminal-oriented form for Codex.

## Copy into the live repository

This handoff is an **overlay** for the existing repository at:

```text
/home/l/working/github.com/khosiness
```

It intentionally does not contain a root `README.md`, so extracting it cannot overwrite the live project README. The archive contains additive Codex/context files plus `docs/manual/`.

If using the overlay ZIP supplied with this handoff:

```bash
cd /home/l/working/github.com/khosiness
unzip /path/to/khosiness-codex-overlay.zip
```

Then inspect before committing:

```bash
git status --short
git diff -- AGENTS.md CODEX_SEED_PROMPT.md PROJECT_HISTORY.md CURRENT_STATE.md CODEX_HANDOFF_README.md docs/manual
```

## Start Codex

1. `cd /home/l/working/github.com/khosiness`
2. Inspect `git status` before copying/committing anything.
3. Start Codex from the repository root.
4. Paste the prompt in `CODEX_SEED_PROMPT.md` into the first session.
5. Let Codex read `AGENTS.md`, `PROJECT_HISTORY.md`, `CURRENT_STATE.md` and the manual.
6. Continue with **Step 0 — The Mental Model**.

## Contents

- `AGENTS.md` — persistent operational instructions for terminal Codex.
- `CODEX_SEED_PROMPT.md` — full historical seed prompt for the first session.
- `PROJECT_HISTORY.md` — how the project and design evolved.
- `CURRENT_STATE.md` — pointer to the live stage tracker and repository identity.
- `docs/manual/index.html` — latest manual as a normal multi-page site.
- `docs/manual/pages/` — all dedicated manual pages.
- `docs/manual/assets/style.css` — shared manual CSS.
- `docs/manual/assets/manual.js` — copy-code helper for local pages.
- `docs/manual/single-file/` — latest self-contained ChatGPT artifact version.

## Important

Only the **latest khosiness naming and architecture** are included as canonical guidance. Earlier `harness` and `khosi` artifact variants are intentionally excluded from this handoff.
