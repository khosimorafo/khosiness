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
| Project Setup | In progress — instruction 3/16 issued; 2/16 complete |
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
15. Review the intended files and Git diff.
16. Commit, verify the baseline, and close Project Setup.

### Instructions 1/16 and 2/16 — complete

The human reported git init and virtual-environment creation, activation,
and pip upgrade. Codex verified a fresh Git repository on master with no
commits, Python 3.14.0 in .venv, and pip 26.2.1 installed inside that
environment. The shell output confirms activation. These are the first
two completed instructions in the new pass.

### Instruction 3/16 — issued, awaiting scaffold creation

The human asked whether the manual's mkdir/touch block is correct from
the existing khosiness directory. It is: create src/khosiness, tests, and
benchmarks, then the seven empty files named in the setup checkpoint.
Codex verified that those directories do not exist yet. Confirm the block
without running it on the human's behalf. Await the human's result before
introducing file contents. Progress: 2/16 complete.
