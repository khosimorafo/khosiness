# khosiness stage tracker

This file is the canonical live record of curriculum progress and the current
single instruction.
Update it after validating each reported result. Complete only one manual stage at
a time.

## Cadence

- Give the human one actionable instruction at a time, with exact commands and code.
- Wait for its result before providing the next instruction.
- Validate the result, record progress here, and continue until the stage gate
  passes.
- Stop at each stage boundary until the human asks to proceed.

## Phase I progress

| Stage | Status |
| --- | --- |
| Project Setup | Complete |
| Step 0 — The Mental Model | Complete |
| Step 1 — Define the Task Contract | Complete |
| Step 2 — Create the Model Adapter | Complete |
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
- In a follow-up teach-back, the human identified the harness as the owner of
  the completion decision and the originating task as the standard to check.
  The tutor clarified that this means checking the proposed result against
  the task's completion criteria. No Step 0 understanding gap remains.
- Reviewed the Step 0 files against the manual checkpoint and checked the final
  documentation formatting.

### Accepted validation exception

The manual requires `pytest -q` to exit successfully while collecting no tests.
Pytest normally returns status 5 for an empty suite, so the manual's expected
exit status is incorrect. No test or collection failure occurred. The human
explicitly accepted this as the Project Setup and Step 0 empty-suite exception
on 2026-09-23. It expired when Step 1 added its first test on 2026-09-24;
from then on, status 5 indicates a collection problem and is a failure. No
artificial test was added.

### Stage boundary

The documentation checks, setup smoke checks, checkpoint comparison and manual
understanding check passed. Step 0 is closed. The human opened Step 1 on
2026-09-24 by requesting its conceptual animation.

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
same optional tutor when opened alone. Future animations follow this page
pairing.
The follow-up review found and we fixed two tutor defects: long answers no
longer break the next question, and animation shortcuts no longer intercept
typing in the standalone tutor. The separate completion teach-back is now
closed with the human's answer recorded above.

## Completed stage: Step 1 — Define the Task Contract

Responsibility: make each run a bounded, validated Task with an identity,
objective, existing workspace, constraints, success criteria, and step limit.

Failure mode addressed: treating an open-ended chat message as a runnable task,
including sending a nonexistent workspace to a model or leaving success and
limits undefined.

The conceptual animation at `docs/animations/step-01-task-contract.html` is
embedded in the Step 1 manual page. It distinguishes data validation, which
belongs to Step 1, from later policy enforcement and completion checks. It is a
study aid, not evidence that the Task model or run loop has been built.

An independent review found that scene 6 originally depicted benchmark JSON
entries as validated, runnable Tasks. The scene now labels them as templates
without workspace or max_steps and shows no validation or ready outcome. The
review's reduced-motion announcement and example-wording issues were also
corrected. The embedded layout remains tall at narrow manual-page widths; that
is a presentation limitation, not a Step 1 gate.
After a report of flicker in scene 6, its disappearing outcome row was replaced
with a benchmark-template note, and autoplay now stops on that final scene.
Initial fixes stabilized the outer iframe but did not stabilize its inner
`.screen` card. An independent reviewer reproduced the visible jump in headed
Chrome and Firefox: scene 6 changed the size of `.flow`, `.contract`, `.screen`,
and `.sidebar`. The animation now reserves the tallest measured height of each
part across all scenes, in embedded and standalone views, and measures again
when viewport width changes. Live-server browser checks found identical part
dimensions through scenes 5 → 6 → 5 at embedded widths 1440, 768, and 390 and
standalone widths 1440 and 1280. The manual page requests a fresh animation URL.

At the first review, `src/khosiness/task.py`, `tests/test_task.py`, and
`benchmarks/tasks.json` were empty, untracked files. All three now contain the
Step 1 implementation. The benchmark file's accidental executable bit was
removed.

The Task model, six tests, ten benchmark templates, final validation, the
Step 1 understanding gate, and the stage commit are complete. On 2026-09-24
the human requested one instruction at a time,
superseding the earlier three-instruction cadence.
The human also requested `N/Y` progress on every instruction. Step 1 has 15
planned numbered instructions. Corrections repeat the active number. Steps
1–8 cover the model, deliberate failure and six tests; 9 creates ten benchmark
templates; 10 checks JSON syntax; 11 checks benchmark count; 12 runs the stage
tests; 13 runs the complete suite; 14 is the understanding gate; 15 reviews
and commits the finished Step 1 stage. All 15/15 are complete.

### Instruction 1 — complete

Write `src/khosiness/task.py` with the six Task fields and the three manual
validators for objective, workspace, and max_steps. The first attempt used a
shell heredoc. The human's zsh paste indented the closing `EOF`, leaving the
shell in `heredoc>` mode; after cancellation, the file remains empty. Resume
this same instruction in VS Code, then inspect the saved file before moving on.
Future multiline instructions for this human must use an editor rather than
heredocs.

The human then saved the file in VS Code. Inspection found that line 1 was
unindented but every later nonblank line had two extra leading spaces;
`python -m py_compile src/khosiness/task.py` initially failed on line 3. The
human removed the two-space margin. Codex verified the corrected indentation,
successful compilation, import, objective stripping, workspace resolution,
and `max_steps=1` on a valid Task. The six fields and three validators now
match the Step 1 checkpoint.

### Instruction 2 — complete

Predict and trigger a missing-workspace failure using a one-line `python -c`
command. The chosen path `__missing_workspace_for_step1__` was confirmed absent
before issuing the instruction. Ask the human to report the observed exception;
an exit status of 1 is expected for this deliberate failure. Do not issue the
first automated-test instruction until the human reports this result.
The human initially predicted that `max_steps` was missing. Clarification:
`max_steps` has a default of 30 in the Task model, so omitting it is valid;
the nonexistent workspace is the deliberate invalid input. The human then
correctly predicted that the workspace does not exist and ran the command.
Pydantic reported one validation error on `workspace` with the expected
"workspace does not exist" message. Codex independently reproduced the
rejection. This is a deliberate failure, so the command's exit status 1 is
expected.

### Instruction 3 — complete

The human created the first test in `tests/test_task.py` using pytest's
`tmp_path` as a real workspace. Codex verified indentation, compilation, and
the test result: `1 passed`. The test checks workspace resolution, objective,
and a positive step limit. The Project Setup/Step 0 empty-suite exception is
now expired.

### Instruction 4 — complete

The human added `pytest` and a missing-workspace test to `tests/test_task.py`.
Codex checked indentation and compilation; the focused test passed, and the
full suite reported `2 passed`. The deliberate failure from instruction 2 is
now a repeatable regression check.

### Instruction 5 — complete

The human added a test that passes an existing regular file as `workspace` and
expects "workspace is not a directory". The focused test passed and the full
suite reported `3 passed`. Codex removed two whitespace-only lines above the
new top-level test and reconfirmed compilation and clean whitespace.

### Instruction 6 — complete

The human added a test for an objective consisting only of spaces. The test
compiled and its focused run passed; the full suite reported `4 passed`.
This verifies that stripping whitespace leaves an empty objective that the
Task validator rejects.

### Instruction 7 — complete

The human added the zero-step test. It compiled, the focused test passed, and
the full suite reported `5 passed`. This verifies the lower bound on the
Task's step budget.

### Instruction 8 — complete

The human added a JSON round-trip test using all six Task fields,
`model_dump_json()`, and `Task.model_validate_json()`. Codex checked the saved
indentation and compilation; the focused test passed and the full suite
reported `6 passed`. The Step 1 checkpoint's six-test count is now met.

### Instruction 9/15 — complete

The human wrote `benchmarks/tasks.json` with ten read-only khosiness-repository
task templates. Codex parsed the file, counted ten unique IDs, confirmed every
entry has exactly `id`, `objective`, `constraints`, and `success_criteria`, and
confirmed there is no `workspace` or `max_steps`. The accumulated suite still
reports `6 passed`. Codex removed the file's accidental executable bit (mode
755 → 644). These are templates, not runnable Task instances.

### Instruction 10/15 — complete

The human ran the manual's JSON syntax check,
`python -m json.tool benchmarks/tasks.json > /dev/null`, and it returned to
the prompt without an error or output. This agrees with Codex's independent
parse. JSON syntax passes.

### Instruction 11/15 — complete

The human printed the number of benchmark entries with a one-line Python
command. It returned exactly `10`, matching the independently checked count.

### Instruction 12/15 — complete

The human ran `pytest tests/test_task.py -q` from the repository root. All six
Step 1 tests passed in 0.20 seconds, meeting the stage-specific test gate.

### Instruction 13/15 — complete

The human reported `6 passed` for `pytest -q`. Codex independently reran the
accumulated suite and saw `6 passed in 0.24s`. The benchmark JSON parser,
SHA256SUMS manifest, and whitespace checks also pass. All automated Step 1
validation gates are green.

### Instruction 14/15 — complete

Ask the human to explain, in their own words, why a Task is more than a chat
message; why the missing workspace fails before any model call; why benchmark
entries are templates rather than runnable Tasks; and what each of the three
Step 1 files contributes. Assess the explanation before advancing to the
review-and-commit instruction 15/15. Record any gap and request a short retry
under the same instruction number.

First teach-back: the human correctly connected workspace rejection to
Pydantic validation and the need for a real directory. Gaps: saying Task
"takes the contents of the chat" blurs the distinction between an explicit
task contract and conversation; saying benchmark entries omit `max_steps`
does not identify that `max_steps` is optional (default 30) while workspace
is required; the three file roles were not distinguished. Ask for a brief
retry on those points. Progress remains 13/15.

Second teach-back: the human named all six Task fields and correctly
distinguished `task.py` (contract and validation), `test_task.py` (behavior and
error checks), and `tasks.json` (saved templates). One precise gap remains:
the answer called benchmark entries templates but did not say which required
field is absent or distinguish it from optional `max_steps`. Ask only that
focused follow-up. Progress remains 13/15.

Final teach-back: the human correctly identified `workspace` as the required
field missing from benchmark templates and `max_steps` as optional with a
default of 30. Together with the earlier answers on the Task's six fields,
pre-model validation, and each file's role, this closes the Step 1
understanding gate with no remaining gap. The manual's deliberate failure was
observed in instruction 2; no event log or run loop exists yet, so generic
manual references to an event trace are N/A for this stage.

### Instruction 15/15 — complete

Codex reviewed the Task model, six tests, ten benchmark templates, animation,
manual embed, tutor-height guard, and governing documents against the Step 1
checkpoint. `pytest tests/test_task.py -q` and `pytest -q` both report six
passing tests; JSON syntax and count, checksum verification, compilation, and
whitespace checks pass. The benchmark examples are specific to this live repo
instead of the manual's generic examples but preserve the template contract.
The human committed the reviewed Step 1 files as `b965c88` (`step 1: define
the task contract`). An overlong `git add` command split the animation path
in the terminal and failed; `git add -A` recovered it, and the resulting
commit contains exactly the nine intended files. After the commit,
`pytest -q` reported six passing tests; JSON syntax, checksum verification,
and whitespace checks also passed. Step 1 is closed. No Step 2 work begins
until the human asks.

## Completed stage: Step 2 — Create the Model Adapter

Responsibility: give the harness one provider-neutral request/response contract,
with a deterministic fake for tests and a thin boundary for provider data.

Failure mode addressed: provider-specific response objects leaking into core
harness logic, or nondeterministic network calls being required to test it.

The conceptual animation at `docs/animations/step-02-model-adapter.html` is
embedded in the matching manual page. It shows the common `generate(messages,
tools)` interface, queued fake responses, inspectable calls, a structured
tool proposal that does not execute, an empty-queue failure, and provider
dictionary normalization. Its traces are illustrative; live Step 2 code,
tests, and the understanding gate have now been completed.
Headless Chrome checks at 1440, 768, and 390 pixels confirmed that scenes
5 → 6 → 5 keep the diagram, narration, and controls at identical positions
and sizes, with no horizontal overflow. The existing six tests, JavaScript
syntax check, checksum manifest, and whitespace check pass.

The human requested the animation first and then began the Step 2 code
sequence. There are 14 planned numbered instructions: 1 defines ToolCall and
ModelResponse; 2 adds the ModelAdapter protocol; 3 creates FakeModel; 4
creates CallableProviderAdapter; 5–8 add the four checkpoint tests one at a
time; 9 runs the focused tests; 10 runs the accumulated suite; 11 checks
provider isolation; 12 inspects FakeModel.calls and the empty-queue failure;
13 is the understanding gate; 14 reviews and commits the stage. Corrections
repeat the active number. All 14/14 instructions are complete.

### Instruction 1/14 — complete

Create `src/khosiness/models/base.py` with only the provider-neutral
`ToolCall` and `ModelResponse` data models. Wait for the saved file and
inspect it before adding the ModelAdapter protocol in instruction 2.

The human saved the file. Codex inspected it against the manual checkpoint
and imported both models. A structured tool call serialized with the expected
id, name, and arguments; optional response fields defaulted to `None` or an
empty list. Progress: 1/14.

### Instruction 2/14 — complete

Add the `ModelAdapter` protocol to the same file, with a
`generate(messages, tools) -> ModelResponse` signature. Do not add a
provider implementation yet.

The human reported another save and requested that the next instruction be
9/Y. Inspection found no protocol or later Step 2 files at that time. The
Step 2 sequence therefore remained at instruction 2/14.

The human then saved the protocol. Codex verified that it imports and has
the required `generate(messages, tools) -> ModelResponse` signature.
Progress: 2/14.

### Instruction 3/14 — complete

Create `src/khosiness/models/fake.py` with a deterministic response queue,
recorded calls, and an explicit empty-queue failure. Wait for the saved file
before moving to the provider adapter.

The human saved the checkpoint-equivalent fake. Codex imported it and observed
the first queued response and recorded inputs. A second call raised the
expected `RuntimeError("FakeModel has no queued response")`; the probe's
nonzero exit status came from that deliberate failure. Progress: 3/14.

### Instruction 4/14 — complete

Create `src/khosiness/models/provider.py` with a callable transport wrapper
that validates provider dictionaries into `ModelResponse`.

The human saved the wrapper. Codex imported it and verified that a transport
dictionary becomes a `ModelResponse` with its text and input-token count
intact. No provider SDK was introduced. Progress: 4/14.

### Instruction 5/14 — complete

Create `tests/test_model_adapter.py` with the first test: a queued fake
returns known text and records the supplied messages and tools.

The human saved the test. Codex inspected it and ran the focused adapter
suite: one test passed. Progress: 5/14.

### Instruction 6/14 — complete

Add a test that the fake preserves a structured `ToolCall` proposal,
including its name and arguments. Do not assert that any tool executes.

The human saved the test. Codex confirmed the saved structure and ran the
focused suite: two tests passed. The assertion checks proposed data only;
no file read occurs. Progress: 6/14.

### Instruction 7/14 — complete

Add a test for the fake's empty response queue and its explicit
`RuntimeError`.

The human saved the test. Codex ran the focused suite: three tests passed,
including the expected failure and the recorded attempted call. Progress:
7/14.

### Instruction 8/14 — complete

Add the provider-normalization test, asserting the callable transport's
dictionary becomes a `ModelResponse` with text and token count intact.

The human saved the test. Codex inspected it and confirmed the test file
compiles; the four adapter tests are ready for the stage-specific run.
Progress: 8/14.

### Instruction 9/14 — complete

Run the focused Step 2 test suite and report the result. Expected: four
passing tests.

The human ran `pytest tests/test_model_adapter.py -q` and reported
`4 passed in 0.13s`. Progress: 9/14.

### Instruction 10/14 — complete

Run the full accumulated test suite. Expected: all ten tests from Steps 1
and 2 pass.

The human reported `10 passed` for `pytest -q`. Progress: 10/14.

### Instruction 11/14 — complete

Check that the Python source has no direct OpenAI or Anthropic SDK references.
This stage uses a callable transport boundary, not a provider SDK.

The human ran the recursive Python-source search and reported no output.
Progress: 11/14.

### Instruction 12/14 — complete

In a Python REPL, inspect a FakeModel response and its recorded request, then
exhaust the queue and inspect the explicit error and second recorded request.
There is no event log yet; FakeModel.calls is the relevant trace at this stage.

The human pasted the REPL lines and the terminal inserted leading spaces,
causing `IndentationError` before the example ran. This is a command-entry
failure, not a harness failure. Repeat instruction 12/14 using a small script
saved through the editor, then inspect its output.
The human saved the temporary script but reran the four adapter tests instead
of executing it. The tests passed again; instruction 12 remains open. The
next command is `python /tmp/khosiness-step2-inspect.py`.

The human then ran the script. It printed `ModelResponse(text='done', ...)`,
showed messages and the offered `read_file` description in the first call,
raised `FakeModel has no queued response` on the second, and showed both
calls in `fake.calls`. This satisfies the stage's manual trace inspection;
the event-log clause is N/A until Step 3. Progress: 12/14.

### Instruction 13/14 — complete

Ask the human to explain the adapter boundary in their own words: what the
protocol promises, why FakeModel and CallableProviderAdapter can be exchanged,
why a ToolCall is not execution authority, and what the empty-queue trace
proved. Assess the answer before closing the stage.

First teach-back: the human correctly described replaceable models sharing
one contract and the fake producing known outputs. Gaps: the provider adapter
receives a dictionary and returns a `ModelResponse`, not a normalized
dictionary; a `ToolCall` is a structured proposal, not a benchmark template;
and the empty-queue observation shows an explicit error plus a recorded
attempt, rather than merely proving the general adapter boundary. Ask for
a focused retry on those points. Progress remains 12/14.

Second teach-back: the human correctly said the provider transport returns a
dictionary and the adapter returns a `ModelResponse`. The human identified
the tool call as a structured proposal, although execution would require
later harness validation/permission and a tool runtime, not merely a loop.
The human named the empty-queue `RuntimeError` but omitted that
`FakeModel.calls` retains the attempted second request. Ask only for those
two final distinctions. Progress remains 12/14.

Final teach-back: the human correctly explained that `FakeModel.generate()`
records the attempted request before checking the queue, so the failed
request remains in `fake.calls`. The human also stated that later harness
validation and policy permission must precede tool-runtime dispatch; a
model proposal has no execution authority. This resolves the remaining
understanding gaps. Progress: 13/14.

### Instruction 14/14 — complete

Codex compared the live files with the Step 2 checkpoint, corrected minor
formatting and stale animation wording, and reran final validation. The
human committed the eight intended files as `d2e521c` (`step 2: create the
model adapter`). Codex verified the commit contents and clean working tree.
After the commit, `pytest -q` reported ten passing tests, the checksum
manifest passed, and the whitespace check was clean. Step 2 is closed.
No Step 3 work begins until the human asks.
