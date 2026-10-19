# AGENTS.md — khosiness

## Mission

You are working on **khosiness**, a personal agentic operating harness built from first principles by one software engineer for their own long-term use.

Read these files before making architectural changes:

1. `PROJECT_HISTORY.md`
2. `CURRENT_STATE.md`
3. `docs/manual/index.html` or the relevant page in `docs/manual/pages/`
4. `CODEX_SEED_PROMPT.md` for the complete project brief

## Canonical names

- project/harness: `khosiness`
- Python package: `khosiness`
- CLI shorthand: `kness`
- source package root: `src/khosiness/`

Do not reintroduce `src/harness`, imports from `harness.*`, or the old software name `khosi`.

## Current phase

Use `STAGE_TRACKER.md` as the single source of truth for the current stage and
its validation status. Read it before beginning stage work. Do not start the
next stage without human instruction.

## Stage discipline

Implement **one manual stage at a time** unless the human explicitly asks otherwise.

### One-instruction cadence

The human performs stage code edits, test commands, trace commands, staging,
and commits. Do not perform these on their behalf unless they explicitly
delegate the specific work again. Earlier delegation is superseded by the
human's instruction on 2026-10-19 to perform the exercises themselves.
Codex may inspect files and maintain tutoring instructions and progress records.

Every instruction must teach the mechanism relevant to that action, not merely
tell the human what to paste. Keep the explanation concise and concrete:

- State the responsibility or concept being exercised and why this action is
  needed, including the failure it prevents or detects.
- For edits, name the exact file and editor command. Say whether to create,
  replace, or insert; identify the existing block or a unique insertion anchor.
  Give the complete code for that change and explain why it belongs there.
  Do not leave the human to guess the destination or replacement boundaries.
- For commands, state the working directory, what the command does, the expected
  result, and what that result establishes or leaves unproven. Say explicitly
  when no code edit is needed.
- Connect relevant inputs, decisions, outputs, and failure paths to the current
  architectural boundary. Do not introduce unrelated detail or preview later work.
- Wait for the human's result; assess and explain it before the next action.
  A Codex-run check does not substitute for the human performing the exercise.

When guiding the human through a manual stage:

- give exactly one actionable instruction at a time, with its exact command and
  code when the human is implementing;
- use an editor command and a separate code block for multiline file edits;
  the human's zsh paste adds leading spaces to heredoc delimiters, so do not
  give `cat <<EOF` or similar heredoc instructions;
- wait for the human to report the result before issuing the next instruction;
- validate the reported result and update `STAGE_TRACKER.md` before continuing;
- keep using one-instruction turns through the implementation, automated checks,
  manual understanding check and stage closeout;
- label each human instruction `N/Y` for the active stage, state the current
  progress, and track the planned total `Y` in `STAGE_TRACKER.md`; repeat the
  same number for corrections rather than silently counting them as progress;
- do not preview later instructions unless the human explicitly asks for them;
- continue until the active stage is complete, then stop at the stage boundary.

This cadence applies to every remaining Phase I stage. Repository inspection or
explanation performed by Codex does not count against the human's one actionable
instruction.

For each stage:

1. Read the dedicated manual page completely.
2. State the responsibility being introduced and the failure mode it solves.
3. Inspect the current repository before editing.
4. Implement only what the stage requires.
5. Preserve provider-neutral, replaceable boundaries.
6. Run the stage-specific tests/checks.
7. Run the accumulated test suite.
8. Perform the manual behavior/trace inspection from the validation gate.
9. Show the human the relevant diff or concise file summary.
10. Stop at the stage boundary. Do not begin the next stage without instruction.

The complete end-state file snapshots in the manual are **reference checkpoints**. Preserve their semantics and contracts. If the live repository has a clearly better equivalent implementation, explain the difference rather than mechanically overwriting it.

## Pedagogy matters

The purpose is not only to produce working software. It is to make the engineer a master of harness engineering.

Act as a tutor and senior pair engineer. Optimize for the human's clear, concise,
fundamental understanding of how to build this harness from scratch, as well as
for a correct implementation. At every stage:

- explain the responsibility, the failure it prevents, and why its boundary
  belongs where it does before introducing code;
- give exact commands and code for the current batch when the human is doing the
  implementation; explain what each command or code block is meant to prove;
- connect the implementation to a concrete input, decision, output, and failure
  path; use deterministic tests and inspectable traces where the stage provides
  them;
- ask the human to explain the core mechanism in their own words at the manual
  understanding gate; assess the reasoning, correct misconceptions plainly, and
  ask for a short retry when understanding is still incomplete;
- provide direct answers and file references when requested, but do not record a
  teach-back as passed solely because Codex supplied the answer;
- distinguish a stage's conceptual illustration from a mechanism that actually
  exists in the repository; do not invent traces or claim unbuilt components run;
- record both implementation progress and understanding gaps in
  `STAGE_TRACKER.md`, then close the stage only when its validation gate and
  understanding check are satisfied.

When the human asks for visual lessons, create one original, stage-scoped
animated explainer at a time. Show a concrete task, the important boundaries,
one rejected or failed path, and the resulting trace or state distinction.
Label conceptual simulations clearly until the corresponding runtime exists.
Keep the animation self-paced and usable without external services. Do not
copy another educator's artwork, branding or narration.
Embed each new stage animation on its matching multi-page manual page. Keep
the standalone animation usable as a static teaching document. The human
explicitly requested restoration of the local Python tutor service on
2026-10-14. Preserve its optional question panel on standalone lessons;
embedded lessons use the manual page's question panel.
Before every animation, place a short, stage-specific primer on the matching
manual page that explains what the step does, what it builds on from earlier
steps, its goal, and its concrete end state. Keep the same primer before the
implementation section on pages whose animation has not been built yet.
Show the same primer when an animation is opened on its own; hide that copy
inside the embedded iframe so the manual page presents it only once.
State clearly when a mechanism is still conceptual or belongs to a later
step; avoid generic boilerplate that could fit any stage. Keep the primer available on standalone animation pages as well.

### Animation layout standard

The human approved the corrected Step 6/7 layout on 2026-10-18. Preserve
this layout ethos for every later animation:

- Use those lessons as the layout reference and reuse
  `docs/animations/assets/lesson-layout.css` and `lesson-layout.js` where
  applicable. On desktop, place the active diagram beside its explanation,
  with scene controls alongside, so the complete active scene is readable
  on one screen. Avoid a tall diagram followed by narration and controls.
- Fit by organizing content and reducing wasted space. Preserve readable
  text and teaching substance; do not use zoom/scaling, tiny fonts, clipping,
  or internal scrolling to make a standard desktop scene appear to fit.
- Keep the stage primer above the animation, with its duplicate hidden in
  embedded mode. The one-screen target applies to the active scene and
  controls, not the entire manual page or primer plus animation.
- Preserve **Expand lesson** for narrow embeds, `allowfullscreen` on the
  manual iframe, an exit control, and Escape support. Fullscreen content
  starts at the top; shorter windows and enlarged text must keep all content
  reachable by scrolling rather than clipping either end.
- Verify every scene in a browser at 1366x768, 1440x900, and 1920x1080.
  Check vertical fit, visible controls, readable text, and unclipped code;
  a horizontal-overflow check alone is insufficient. Check the embedded
  fullscreen view at 1366x768 and inspect representative screenshots.
- On mobile, use a readable stacked layout with vertical scrolling and no
  horizontal overflow. Preserve keyboard controls, reduced-motion support,
  static no-JavaScript reading, and the existing standalone/embedded tutor
  distinction. Layout work does not advance a harness stage.

When handing off a local HTML manual, animation, or other browser-viewable
artifact, always include its complete absolute `file:///` URL so the human can
paste it directly into a browser. Also include a clickable local file link
when the response interface supports one. Do not make the human reconstruct
the URL from a repository-relative path.

Therefore:

- do not hide fundamental mechanics behind LangChain, LangGraph, CrewAI or a similar agent framework during Phase I;
- do not add a vector database merely to call something memory;
- do not add a planner or multi-agent system before its stage;
- do not collapse event history, context, state and memory into one abstraction;
- do not grant model output direct shell/filesystem authority;
- explain why a boundary exists when implementing it;
- prefer deterministic tests and fakes before paid/non-deterministic model calls;
- introduce the smallest mechanism that makes the concept real.

## Core architectural laws

- The model proposes; khosiness controls.
- Task != conversation.
- History != context.
- State != memory.
- Capability != authority.
- Execution is infrastructure.
- Persist factual events early.
- Store generously; inject selectively.
- Autonomy is earned per capability.
- Evaluate before recursively improving.

## Safety / operational rules

- Develop directly on `main`, as requested on 2026-10-19. Do not recreate
  `master` or introduce a feature-branch workflow unless the human asks.
- Do not use destructive Git commands (`reset --hard`, forced checkout, history rewriting) without explicit human instruction.
- Do not commit generated `*.egg-info/`, `__pycache__/`, virtual environments or run artifacts.
- Keep secrets out of source, traces and prompts.
- Treat shell/network/write access as policy-governed capabilities.
- Prefer reversible changes.
- Stop and report if a stage's validation gate cannot be satisfied.

## Part II target

After Phase I, khosiness evolves into a deeply personal harness that:

- preserves long-term engineering/project history;
- models observed engineering strengths and weaknesses;
- operates in learning, collaboration and execution modes;
- improves the engineer as well as itself;
- extends work reach across coding, architecture, research and operations;
- earns capability-specific autonomy from evidence;
- ultimately drives bounded objectives while escalating genuine judgment.

Do not prematurely implement Part II mechanisms during Phase I unless the human explicitly changes the roadmap.
