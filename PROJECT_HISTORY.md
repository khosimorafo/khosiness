# khosiness — project history and intent

## 1. Origin

This work began as an attempt to learn **harness engineering from first principles**, not merely how to use an agent framework. The immediate learning goal was to understand the machinery around frontier models: task contracts, model adapters, event histories, agent loops, tool execution, context policy, sandboxes, permissions, state, recovery, memory, skills, delegation, evaluation and recursive improvement.

The original implementation approach was deliberately Python-first and framework-light. The engineer is already proficient in Python and initially chose VS Code rather than a coding agent so that none of the fundamental machinery would be hidden.

The manual evolved into a detailed implementation course. Each stage now contains:

- the conceptual reason the component exists;
- the files to create or modify;
- ordered implementation steps;
- code scaffolding;
- tests and deliberate failure exercises;
- a cumulative project tree with current-stage files highlighted;
- a complete end-state snapshot of every file touched in the stage;
- a validation gate with exact commands, expected results and a manual understanding/trace check.

## 2. Naming history

The generic project was first called a harness. The personal-harness concept was briefly called `khosi`. The final project identity is now:

- **Project / harness:** `khosiness`
- **Python package:** `khosiness`
- **Repository directory:** `khosiness/`
- **Command-line shorthand:** `kness`

Do not reintroduce the old package path `src/harness`, imports from `harness.*`, or the old product name `khosi` for the software. `Khosi` may still refer to the human engineer where the manual explicitly discusses the person.

## 3. Phase I — build the substrate

Phase I is the first-principles harness curriculum. The sequence is:

- Project Setup
- Step 0 — The Mental Model
- Step 1 — Define the Task Contract
- Step 2 — Create the Model Adapter
- Step 3 — Build the Event Log
- Step 4 — Implement the Agent Loop
- Step 5 — Build the Tool System
- Step 6 — Engineer the Context
- Step 7 — Repository Navigation
- Step 8 — Shell Execution and Sandbox
- Step 9 — Policy and Human Approval
- Step 10 — State, Checkpoints and Recovery
- Step 11 — Memory
- Step 12 — Context Compaction
- Step 13 — Skills and Progressive Disclosure
- Step 14 — Subagents
- Step 15 — Evaluation
- Step 16 — The Harness Learning Loop
- Step 17 — Assemble the First-Generation Architecture
- Step 18 — 12-Week Build Plan / complete Phase I

Phase I intentionally postpones high-level frameworks and premature complexity. The engineer should be able to explain and test each underlying mechanism before adopting abstractions that hide it.

## 4. Architectural principles established so far

1. **The model is not the system.** The model proposes; khosiness controls what is visible, valid, executable, persistent, permitted and considered complete.
2. **Task is not conversation.** A run begins from an explicit bounded task contract.
3. **History is not context.** Record generously; inject selectively.
4. **State is not memory.** Current-run continuity and cross-run durable knowledge have different lifetimes.
5. **Capability is not authority.** A tool existing does not mean the model may use it automatically.
6. **Event history should exist early.** Observability, replay, recovery, evaluation and learning all depend on factual traces.
7. **Execution is infrastructure.** Shell/runtime access is a security boundary with cwd, timeout, environment, output and permission controls.
8. **Subagents are primarily context-isolation and delegation mechanisms, not personas.**
9. **Evaluation precedes recursive improvement.** Change one variable at a time and rerun fixed benchmarks.
10. **Autonomy must be earned per capability, not granted globally.**

## 5. Part II — the target beyond Step 18

The project then became more ambitious: a **truly personal agentic operating harness built by one software engineer purely for their own use**.

The target definition is:

> **khosiness is a continuously evolving computational extension of one software engineer: preserving context, amplifying capability, extending operational reach, improving the engineer's own skills, and progressively earning authority to act.**

The unit of optimization is not agent performance alone. It is:

> **Engineer + khosiness**

The long-term system therefore has two learning loops:

- **Work reach loop:** understand → plan → act → observe → verify → report → learn.
- **Engineer loop:** observe the engineer → diagnose → teach → challenge → measure → adapt.

The system must avoid becoming a crutch that silently compensates for weaknesses while the engineer's own capability decays.

Three collaboration modes are intended:

- **Learning mode:** keep important cognitive work with the engineer and use khosiness to teach/challenge.
- **Collaboration mode:** divide reasoning and execution between engineer and harness.
- **Execution mode:** let khosiness complete established work reliably inside a known envelope.

The autonomy ladder is:

- L0 Observe
- L1 Advise
- L2 Prepare
- L3 Execute with approval
- L4 Execute by policy
- L5 Drive bounded objectives

Authority should be capability-specific and evidence-based. For example, routine patch dependency updates may eventually be L4 while production database migrations remain L1 or L2.

Before deep personalization or meaningful autonomy, Part II begins with a **Khosiness Constitution** defining what the system exists to optimize, what it must never optimize away, how it may learn about the engineer, how memories can be challenged/corrected, and how authority is earned or revoked.

## 6. Implementation state at the original handoff

This section is a historical snapshot. For current progress, read
`STAGE_TRACKER.md` and inspect the repository.

Project Setup has been completed and validated in the real repository.

Observed working state:

- repository directory: `/home/l/working/github.com/khosiness`
- editable install succeeds with `python -m pip install -e ".[dev]"`
- package import resolves to `src/khosiness/__init__.py`
- `kness --version` prints `khosiness 0.1.0`
- pytest runs successfully; there are intentionally no tests yet at the end of Project Setup
- generated `*.egg-info/`, `__pycache__/`, `.venv/` and similar artifacts are ignored by Git
- the Git working tree was clean after the final setup validation

The visible setup commits immediately before the handoff were `04d9628` (`chore: initialize khosiness project`) and `253a3db` (`chore: ignore generated package metadata`). The latter cleaned previously tracked `*.egg-info/` files; a subsequent editable install recreated them locally but Git correctly ignored them, leaving a clean working tree.

The next curriculum stage is **Step 0 — The Mental Model**. It is deliberately documentation/architecture-first; behavior-bearing code begins at Step 1 with the Task Contract.

## 7. Why Codex is being introduced now

The project is now moving into terminal Codex. This changes the implementation workflow, not the educational objective.

Codex should act as a disciplined senior pair engineer and implementation partner. It may edit and test code, but it must not erase the first-principles learning sequence by replacing the project with a large framework or racing several stages ahead. Each stage should still be understood, implemented, tested, traced and explicitly closed before the next stage begins.
