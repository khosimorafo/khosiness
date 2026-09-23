# khosiness stage tracker

This file is the canonical live record of curriculum progress and the current
three-instruction batch.
Update it after validating each reported batch. Complete only one manual stage at
a time.

## Cadence

- Give the human no more than three actionable instructions at once.
- Wait for results before providing the next batch.
- Validate the results, record progress here, and continue until the stage gate
  passes.
- Stop at each stage boundary until the human asks to proceed.

## Phase I progress

| Stage | Status |
| --- | --- |
| Project Setup | Complete |
| Step 0 — The Mental Model | Complete |
| Step 1 — Define the Task Contract | Pending |
| Step 2 — Create the Model Adapter | Pending |
| Step 3 — Build the Event Log | Pending |
| Step 4 — Implement the Agent Loop | Pending |
| Step 5 — Build the Tool System | Pending |
| Step 6 — Engineer the Context | Pending |
| Step 7 — Repository Navigation | Pending |
| Step 8 — Shell Execution and Sandbox | Pending |
| Step 9 — Policy and Human Approval | Pending |
| Step 10 — State, Checkpoints and Recovery | Pending |
| Step 11 — Memory | Pending |
| Step 12 — Context Compaction | Pending |
| Step 13 — Skills and Progressive Disclosure | Pending |
| Step 14 — Subagents | Pending |
| Step 15 — Evaluation | Pending |
| Step 16 — The Harness Learning Loop | Pending |
| Step 17 — Assemble the First-Generation Architecture | Pending |
| Step 18 — Complete Phase I | Pending |

## Completed stage: Step 0 — The Mental Model

Responsibility: define the control boundary and assign ownership before adding
behavior-bearing code.

Failure mode addressed: treating "the agent" as an undefined owner of reasoning,
authority, execution, persistence and completion.

### Completed

- Read the dedicated Step 0 manual page.
- Inspected the live repository and handoff documents.
- Confirmed `kness --version` reports `khosiness 0.1.0`.
- Confirmed `khosiness` imports from `src/khosiness/__init__.py`.
- Confirmed the handoff/manual overlay is present as untracked files.
- Expanded `README.md` with the system definition, governing rule, v0 scope and
  three representative tasks.
- Created `docs/architecture.md` with the six planes, system boundary, ownership
  table and Stage 0 non-goals.
- Removed unintended Markdown indentation and passed structural and whitespace
  validation.
- Passed the Step 0 file-existence and governing-rule checks.
- Confirmed pytest collects no tests and returns exit status 5,
  with no collection or test failures.
- Reconfirmed the CLI version and canonical package import path.
- Passed the manual understanding check. The human explained that the model
  proposes, the harness validates, harness policy permits, and the tool/runtime
  layer executes. The human identified the harness as owner of current run
  state, the event store as owner of durable factual history, and a future
  memory subsystem as owner of cross-run memory. For a search returning many
  matches, the human said history retains the factual results while the
  harness selects only task-relevant matches for the next model context.
  The manual's listed understanding questions have no remaining gaps.
- Completion against task criteria is documented but was not separately
  repeated by the human during the teach-back. Revisit this briefly before
  Step 1, where task criteria become concrete.
- Reviewed the Step 0 files against the manual checkpoint and checked the final
  documentation formatting.

### Accepted validation exception

The manual requires `pytest -q` to exit successfully while collecting no tests.
Pytest normally returns status 5 for an empty suite, so the manual's expected
exit status is incorrect. No test or collection failure occurred. The human
explicitly accepted this as the Project Setup and Step 0 empty-suite exception
on 2026-09-23. It expires when Step 1 adds the first test; after that, status 5
indicates a collection problem and is a failure. No artificial test was added.

### Stage boundary

The documentation checks, setup smoke checks, checkpoint comparison and manual
understanding check passed. Step 0 is closed. Step 1 remains pending until the
human explicitly asks to proceed.

### Supplemental visual lesson

An original, self-contained Step 0 animation is available at
`docs/animations/step-00-mental-model.html`. It illustrates the six planes, a
rejected shell proposal, a permitted read, event history versus selected
context, and harness-owned completion. It is labeled as conceptual because
the runtime is not yet implemented.
An independent review found misleading red arrows on permitted paths; those
were corrected. A later review found that scenes 3, 5, and 6 still need a
focused visual pass: the rejection marker appears before policy, routes
overlap during context selection, and the completion decision is not drawn.
Use the manual's written ownership rules for those distinctions until then.

### Known manual discrepancies

The bundled reference manual has stale `src/harness/` tree labels, omits
`cli.py` from some trees, and lacks the live `*.egg-info/` ignore rule in its
setup snapshot. Its Setup README snapshots disagree, and generic event/trace
instructions on Step 0 do not apply to this documentation-only stage. Treat
these as reference defects, not reasons to change the canonical live package.
The Step 0 runtime failure trace is N/A because there is no event log or agent
loop yet; the supplemental animation is explicitly conceptual.

### Manual study aid

The multi-page manual has a shared page-scoped Q&A panel backed by a separate
local tutor service. This is documentation tooling for every stage, not a
behavioral component of the khosiness harness or progress on Step 1.
The Step 0 animation is embedded in its matching manual page and has the
same optional tutor when opened alone. Future animations should follow this
page pairing; the Step 1 stage boundary remains unchanged.
The follow-up review found and we fixed two tutor defects: long answers no
longer break the next question, and animation shortcuts no longer intercept
typing in the standalone tutor. The separate completion teach-back remains
open until the human answers it.
