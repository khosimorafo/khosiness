# khosiness implementation manual

Open index.html for the multi-page manual, or the static single-file edition
in single-file/khosiness-harness-engineering-manual.html. Both include the
corrected reference checkpoints. Animations in ../animations/ remain usable
on their own and embedded on their matching pages.

The manual requires no local server. The optional Python tutor service was
removed for the complete coding reset on 2026-10-13. Bring lesson questions
to the tutoring conversation instead.

The manual describes what to build. STAGE_TRACKER.md records what has
actually been completed. Every stage is pending in the fresh pass, including
Project Setup. Follow one actionable instruction at a time; use editor
commands and separate code blocks for multiline edits.

Only Setup and Step 0 expect an empty pytest suite (exit status 5). From
Step 1 onward, tests must be collected and pass with exit status 0.
