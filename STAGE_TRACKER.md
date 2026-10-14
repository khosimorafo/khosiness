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
| Project Setup | In progress — 14/16 complete; technical corrections verified; understanding and closeout pending |
| Step 0 — The Mental Model | Pending |
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

## Active stage: Project Setup

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
