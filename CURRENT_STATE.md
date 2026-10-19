# Current state

Project Setup's technical corrections are verified. The source package and
CLI report khosiness 0.1.0. The editable install in .venv includes the
runtime dependency Pydantic and development dependency pytest. The initially
empty setup suite returned status 5 as expected; Step 1 now has six tests.

Previously committed egg-info and bytecode are removed from Git tracking
and ignored. The corrective baseline was saved as commit 084ea70.
The human setup understanding check and formal closeout remain pending.
On 2026-10-15 the human explicitly requested Step 0. It is now complete:
6/6 instructions, documentation validation, expected empty test collection,
and human ownership/history/context/rejection understanding checks verified.
README.md and docs/architecture.md are saved in commit 3832279.
Step 1 is complete: 10/10 instructions, six passing stage and accumulated
tests, ten validated benchmark templates, deliberate validation-error
inspection, and human understanding checks. Commit 69e85b7 contains the
Task model, tests, templates, and staged progress record.
Step 2 is complete: 12/12 instructions, four passing adapter tests and ten
accumulated exercise tests, provider-reference inspection, debugger input
and exhaustion-error inspection, and human understanding checks. Commit
ce29485 contains the model contracts, fake, callable provider wrapper, tests,
and staged progress record. No live provider transport is implemented.
Step 3 is complete: 11/11 instructions, four passing event-store tests and
fourteen accumulated tests, JSONL/newline inspection, completed-append
writer-termination check, malformed-record failure, and human understanding
checks. Commit f49e53f contains Event, JsonlEventStore, tests, and the staged
progress record. This event store provides no replay or power-loss guarantee.
Step 4 is complete: 12/12 instructions, four loop tests and eighteen
accumulated tests passed, actual success/failure/limit traces inspected,
debugger state transitions inspected, and human understanding checked.
Commit 40237f9 contains RunState, run(), local fake-based tests, and the
staged progress record. The loop accepts final text without tool calls;
it does not verify success criteria. Durable state checkpoint storage
and approval policy remain future work.
Step 5 is complete: 13/13 instructions, fourteen tool tests and thirty-two
accumulated tests passed, manual search and real-registry loop success/
rejection traces inspected, and human understanding checked. Commit 0b51887
contains Tool/ToolResult, ToolRegistry, validated and bounded read-only
filesystem tools, tests, and the staged progress record. These tools assume
a stable workspace; they are not an OS sandbox or approval system.
Step 6 is complete: 11/11 instructions, twelve context cases and forty-four
accumulated tests passed, exact message/source-state and real-loop integration
inspected, invalid-budget failure observed, and human understanding checked.
Commit 2e3f832 contains ContextBuilder/ContextStats, tests, and the staged
progress record. Selection preserves source observations; last_stats is
local latest-build metadata, not durable metrics or a global token budget.
The Setup understanding gap is deferred, not passed.
Step 7 — Repository Navigation is complete: 14/14 validated, saved and verified
in commit 90c9773. The human ran the stage and accumulated tests, inspected live
complete/incomplete/rejected tool traces, passed the understanding gate, and
staged, inspected, committed, and verified the five intended stage files.
The human performs stage edits and commands;
Codex provides precise instructions and maintains tutoring records. Strict bounded
arguments, configurable shallow listing, numbered reads, and structured search
are connected; accumulated tool regressions and deterministic navigation tests
are in place, along with fifteen fixture-specific repository benchmark rubrics.
All 92 accumulated exercise tests pass. Benchmarks define expected facts and
source ranges; no runner or automatic grader is implemented. The commit contains
filesystem tool changes, tool regressions, navigation tests, benchmark rubrics,
and the staged progress record. The final closeout record is a subsequent
documentation update; separate manual/animation/tutor work remains outside
this stage commit.
The human requested Step 8 — Shell Execution and Sandbox. It is active at
1/12 validated. The human created the sandbox directory; execution runtime
files are not implemented yet. The human performs the
implementation and commands; Codex supplies one precise teaching instruction
at a time. Step 9 onward remains pending.
Use the tracker for subsequent instruction results and understanding checks.

Use STAGE_TRACKER.md for the canonical instruction and validation record.
The manual and animations are reference material, not completed exercises.
The remote GitHub repository has not been changed by the restart.

Planned/runtime identity: khosiness; CLI: kness; source: src/khosiness/.

The human requested restoration of the optional manual Q&A service on
2026-10-14. This documentation companion is separate from the harness
runtime and does not advance stage progress or pass understanding checks.
