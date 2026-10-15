# khosiness stage tracker

Full local coding and Git reset requested on 2026-10-13. All setup,
implementation, validation, and teach-back progress is cleared. The earlier
Step 0 question is withdrawn. The human has now begun fresh Project Setup.

## Cadence

- Begin with Project Setup, one actionable instruction at a time.
- Record a planned total and label each instruction N/Y before starting.
- Use an editor command and separate code block for multiline file edits.
- Wait for the human's result, validate it, and record progress.
- Repeat the same number for corrections and stop at each stage boundary.

## Phase I progress

| Stage | Status |
| --- | --- |
| Project Setup | Technical checks passed; understanding and formal closeout deferred when the human requested Step 0 |
| Step 0 — The Mental Model | In progress — instruction 6/6 issued; 5/6 complete |
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

## Starting point at reset

Only the manual, animations, and project-instruction documents remain.
There is no .git, .gitignore, .venv, src, tests, benchmarks, pyproject.toml,
project README, or project LICENSE. The optional Python manual tutor service
has also been removed; the manual and animations work as static documents.

At that reset no setup command or understanding check had been completed.
Reference code in the manual is not live code. Subsequent progress is
recorded below.

## Reset verification

Verified on 2026-10-13: the listed coding paths are absent and no Python
source or bytecode remains under this project. Git reports that this is
not a repository; an external-to-sandbox check confirms .git is absent.
Retained manual/animation file links resolve, document JavaScript syntax
passes, and the refreshed checksum manifest passes. These checks establish
only the clean starting directory, not Project Setup completion.
The remote GitHub repository is outside this local reset and is unchanged.

## Prior stage: Project Setup — understanding and formal closeout pending

Responsibility: establish an isolated, installable Python project and an
inspectable Git baseline. Failure mode: mixing project dependencies with
the global environment or starting behavior without a reproducible layout.

Codex read the complete setup page and inspected the live directory before
issuing the next instruction. Planned total: 16 human instructions.

1. Initialize the local Git repository.
2. Create and activate .venv, and upgrade its pip.
3. Create the empty source/test/benchmark scaffold and setup files.
4. Define pyproject.toml.
5. Define .gitignore.
6. Define the package version in src/khosiness/__init__.py.
7. Define the version/help CLI in src/khosiness/cli.py.
8. Write the setup README.
9. Install the package and development dependencies in editable mode.
10. Check the CLI version.
11. Check the package import path.
12. Run the intentionally empty test suite.
13. Inspect the deliberate environment/import distinction.
14. Complete the setup understanding check.
15. Review the intended files and remove mistakenly tracked generated artifacts from the index.
16. Commit, verify the baseline, and close Project Setup.

### Instructions 1/16 and 2/16 — complete

The human reported git init and virtual-environment creation, activation,
and pip upgrade. Codex verified a fresh Git repository on master with no
commits, Python 3.14.0 in .venv, and pip 26.2.1 installed inside that
environment. The shell output confirms activation. These are the first
two completed instructions in the new pass.

### Instruction 3/16 — complete

The human asked whether the manual's mkdir/touch block is correct from
the existing khosiness directory. It is: create src/khosiness, tests, and
benchmarks, then the seven empty files named in the setup checkpoint.
Codex verified that those directories do not exist yet. Confirm the block
without running it on the human's behalf. Await the human's result before
introducing file contents. The human ran the block. Codex verified all
seven files exist and were empty before the requested edits below.

### Instructions 4/16, 5/16, and 8/16 — complete by explicit delegation

The human supplied the manual's pyproject.toml, .gitignore, and README.md
contents and explicitly asked Codex to fill those three files. Codex wrote
them exactly, verified TOML parsing, version 0.1.0, the kness entry point,
pytest as the dev extra, generated-artifact ignore rules, and whitespace.
This explicit batch request supersedes one-instruction editing for these
three files only. Progress: 6/16 complete; no new human instruction issued.

### Early commands requiring correction — historical observation

Before these files had contents, the human ran an editable install, import,
pytest, and a root commit. Codex observed khosiness 0.0.0 installed without
the dev extra, and no pytest package in .venv. The successful import only
established that the empty package could be found. These actions do not
pass the intended install, CLI, import, or test gates yet.
The root commit ff7bfa8 contains generated egg-info and bytecode because
.gitignore was empty at commit time. The new ignore rules prevent new
tracking but do not remove existing tracked files. Correct that in
instruction 15 and finish with a follow-up commit; do not rewrite history.
At that inspection src/khosiness/__init__.py and cli.py were empty. The
corrections below supersede those earlier defects.

### Instructions 6/16, 7/16, and 9/16–13/16 — complete by explicit delegation

The human asked Codex to make all necessary corrections before Step 0.
This authorizes the remaining technical setup work as a batch. Codex filled
the version and CLI files with the manual checkpoint and reinstalled
`.[dev]` into .venv, replacing version 0.0.0 with 0.1.0 and installing
Pydantic and pytest. The initial sandboxed pip attempt could not resolve
PyPI; the authorized unrestricted retry succeeded.

Checks passed: kness --version prints khosiness 0.1.0; help lists --version;
package import resolves to this src/khosiness/__init__.py; installed metadata
reports 0.1.0; pytest is installed in .venv; pip check finds no broken
requirements. The real .venv pytest collects zero tests and returns status 5,
which is expected at Setup. No dummy test was added.

For the deliberate import distinction, the same .venv interpreter succeeds
normally but raises ModuleNotFoundError with -I -S, which disables project
path and site-package discovery. This demonstrates source existence versus
import configuration; it does not establish that a separate global Python
installation lacks the package. The human understanding gate remains open.

### Instruction 15/16 — complete by explicit delegation

Codex reviewed the five setup-file changes, verified clean whitespace, and
removed previously tracked egg-info and bytecode with git rm --cached.
The files remain on disk and are ignored by the new rules; no history was
rewritten. No virtual-environment files were tracked.
Progress: 14/16 complete (instructions 1–13 and 15).

### Instruction 16/16 — in progress, corrective baseline commit

Commit the corrected technical baseline and documentation as a follow-up
commit, preserving ff7bfa8. Verify that generated files are absent from the
index and the working tree is clean. Formal stage closeout remains pending
until instruction 14's human understanding check passes.

### Instruction 14/16 — issued, awaiting human understanding

Ask the human to explain what .venv isolates and how the editable install
makes kness import the source package while declaring Pydantic and pytest
in separate dependency groups. Do not grant understanding credit from
Codex's own explanation. Step 0 remains pending.

The human's first answer identified Python-environment isolation and
described it as "sort of a sandbox." This is partial evidence: clarify that
.venv isolates installed Python dependencies and versions, not filesystem,
shell, or network authority. Ask for a short restatement of that boundary
under the same instruction number. Editable-install reasoning has not yet
been supplied. The understanding gate remains open; progress is 14/16.

### Restored manual Q&A companion — 2026-10-14

The human explicitly requested the removed local question tutor back.
Restored docs/manual/manual_qa_server.py, the manual.js question panel,
and manual-qa.css from the prior implementation without importing old Git
history into this new repository. This is documentation tooling only.
Current Setup understanding credit and stage progression are unchanged.

The restored service reads fresh tracker, selected-page, and bounded source/
reference evidence. It enforces one instruction at a time and editor-based
multiline edits, and keeps reference code distinct from implemented code.
The question panel is available on manual pages and standalone animations;
embedded animations defer to their parent page's panel.

Review corrections cover manual URL aliases, Unicode byte limits, resolved
reference/tracker containment including symlink directories, bounded manual
reads before parsing, and disabling host-access/delegation capabilities for
Codex tutor requests. Additional read-only/never-approve settings remain.
Browser checks pass for loading/error behavior, long-answer follow-up history,
text-only rendering, mobile expansion, standalone typing, static-file startup
instructions, and actual gpt-6-sol medium-effort answers. A request to read
an outside temporary canary file did not reveal its contents.

Documentation tests are kept in docs/manual/tests, separate from Phase I's
exercise suite: 28 documentation checks pass; the accumulated setup exercise
suite still correctly collects no tests and returns status 5. No harness
runtime feature or human understanding gate was completed by this work.

The final general review reports no actionable defects. Security-review
findings and the follow-up regression-test finding are resolved and verified.
Checksums, JavaScript syntax, and whitespace pass. The test server and
browser were stopped after verification; the human can start the restored
service with python docs/manual/manual_qa_server.py.

### Tutor keyboard submission — 2026-10-14

At the human's request, Enter in the question textarea now submits;
Shift+Enter inserts a newline. Composition Enter is left to the input
method. Native Chrome keyboard checks passed for submission, newline,
empty input, composition, Ctrl+Enter, and the Ask button's Enter behavior.
The placeholder documents the shortcuts. No harness-stage progress changed.

## Active stage: Step 0 — The Mental Model

On 2026-10-15 the human explicitly requested "LEts do step 0". Proceed with
that stage while retaining the unpassed Setup understanding check as a
deferred gap. Do not mark Setup understanding or formal closeout passed.
This is a human-directed transition, not inferred completion.

Responsibility: define who owns proposals, context, validation, permission,
execution, history, state, memory, and completion before adding behavior.
Failure mode: treating the model as the undefined owner of the whole agent
and letting a plausible proposal stand in for authority or verified success.

Codex read the complete dedicated page and inspected the live repository:
README.md still contains its setup text; docs/architecture.md is absent.
The existing uncommitted manual/tutor work is separate documentation tooling.
No Step 0 exercise document has been changed in this pass.

Planned total: six human instructions.

1. Explain the proposal, permission, and execution boundary for one file read.
2. Write README.md with the system definition, v0 scope, and example tasks.
3. Write docs/architecture.md with the six planes and ownership table.
4. Run stage-specific documentation checks and accumulated setup checks.
5. Complete the manual ownership/understanding check and rejected-action example.
6. Review the stage diff, commit, verify, and close Step 0.

### Instruction 1/6 — issued, awaiting answer

Introduce "The model proposes; khosiness controls" as a design rule, not an
existing runtime. Ask who should decide whether a model-proposed file read
outside the workspace is permitted, and which layer would perform an allowed
read. No understanding credit has yet been awarded. Progress: 0/6 complete.

The human answered: "The harness decides based on policy." This correctly
identifies the owner and basis of the permission decision. The execution
layer was not named; ask who performs an allowed read under the same
instruction number. Permission ownership is demonstrated; instruction 1/6
remains open pending the execution distinction. Progress: 0/6 complete.

The human then answered "Tool runtime." Together the two answers correctly
distinguish policy permission from execution. Instruction 1/6 is complete.
Progress: 1/6 complete. This is conceptual understanding, not implemented
policy or tool-runtime behavior.

### Instruction 2/6 — issued, awaiting README edit

Ask the human to edit README.md using an editor command and a separate
complete Markdown block. Define the intended system, governing rule,
read-only v0 scope, non-goals, and three concrete repository tasks. Keep the
animation link and label the future runtime as planned. The inspected README
still contains the setup baseline. Await the saved-file report before
validating or issuing instruction 3/6.

The human reported "saved". Codex inspected README.md and confirmed the
system definition, proposal/control rule, tool/runtime dispatch boundary,
read-only v0 scope, non-goals, three example tasks, and conceptual animation
link. The text explicitly distinguishes planned behavior from implemented
runtime. Instruction 2/6 is complete. Progress: 2/6 complete.

### Instruction 3/6 — issued, awaiting architecture document

Codex confirmed docs/architecture.md is absent. Ask the human to create it
with the six responsibility planes, system boundary, ownership table, and
Stage 0 non-goals. Keep run state, durable history, selected context, and
future cross-run memory distinct. This documents the intended architecture;
it introduces no runtime. Await the saved-file report before validation.

The human reported "saved", but Codex could not find docs/architecture.md
or another architecture-named file in the repository. Instruction 3/6
remains open; progress stays 2/6 complete. Ask the human to save the supplied
document at the exact repository path before proceeding to validation.

The next saved-file report is verified: docs/architecture.md now exists and
contains all six planes, ownership table, completion distinction, and v0
non-goals. The system-boundary diagram lacks Markdown code fences, so its
spacing will collapse when rendered. Ask for that formatting correction
under instruction 3/6; progress remains 2/6 complete pending verification.

After the next "saved" report, disk inspection still shows no code fences
around the diagram. Keep instruction 3/6 open and give the two literal fence
lines with an editor command. Progress remains 2/6 complete.

The latest saved-file report is verified: the diagram now has its opening
text fence and closing fence. Instruction 3/6 is complete. Progress: 3/6.

### Instruction 4/6 — validation in progress

Codex inspected both stage documents: governing rule, six planes, ownership
table, scope, and conceptual/runtime distinction are present. The animation
link points to the retained Step 0 lesson. Whitespace checks on tracked
stage edits pass. Ask the human to run the accumulated exercise suite using
.venv/bin/python -m pytest -q. No tests should be collected; exit status 5
is expected at this documentation-only stage, not a passing runtime suite.
Await the output before recording validation as complete.

The human reported running .venv/bin/python -m pytest -q from the repository
root: "no tests ran in 0.01s". This matches expected empty exercise-suite
collection at Step 0; it is not evidence of runtime tests passing. Combined
with the inspected stage documents, instruction 4/6 is complete. Progress:
4/6 complete.

### Instruction 5/6 — understanding gate issued

Ask the human, without consulting the documents, to identify who owns
reasoning, permissions, current run state, cross-run memory, and execution.
Assess their answer before continuing under the same instruction number
with the history/context distinction and conceptual rejected-action example.
Do not grant understanding credit from supplied reference text. Progress:
4/6 complete; stage closeout remains pending.

The human answered, in order: "Model, Harness Policy, Harness, Memory
Subsystem, Tool Runtime layer". All five ownership mappings are correct.
This part of the understanding gate is satisfied; cross-run memory remains
a planned subsystem, not implemented behavior. Continue instruction 5/6
with one question about why recording an event does not automatically make
it visible to the model. The rejected-action example remains pending.
Progress: 4/6 complete.

The human answered "No. A filtering algorithm will be implemented later".
This correctly distinguishes recorded history from selected model context.
Clarified that the harness context builder chooses the messages for each
call; simple selection rules suffice, and no special filtering algorithm
is required. This mechanism is planned, not implemented at Step 0.
Continue instruction 5/6 with a conceptual malformed tool-request example
to check validation ownership, execution prevention, and factual recording.
Progress remains 4/6 complete pending the final understanding example.

The human explained that a proposal grants no permission, the harness
validates it, and the invalid call does not execute. These boundaries are
correct. They also proposed raising an exception: clarify that this is an
implementation choice, not a Stage 0 contract; a structured error is also
possible, and an uncaught exception need not terminate the run. Factual
recording was omitted. Ask what should be recorded and which component
owns that durable record. Instruction 5/6 remains open, progress 4/6.

The human answered "The structured error with the reason. The event store
owns the record". This correctly identifies rejection evidence and durable
history ownership. Together with prior answers, the conceptual ownership,
history/context, and rejected-action understanding checks are satisfied.
Instruction 5/6 is complete; progress 5/6. No runtime trace is claimed.

### Instruction 6/6 — closeout in progress

Codex reviewed the README diff and complete architecture document. README
defines intended behavior, read-only scope and example tasks; architecture
assigns six planes and ownership and distinguishes final text from proven
success. These are the two Step 0 exercise documents. Other uncommitted
manual/tutor changes predate this stage and remain separate.
Ask the human to stage only README.md, docs/architecture.md and this tracker.
Verify the index before issuing the commit command under instruction 6/6.
Stage completion remains pending commit and verification. Setup's deferred
understanding check remains open.
