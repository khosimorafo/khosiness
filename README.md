# khosiness — Harness Engineering From Scratch

A first-principles Python agent harness built one responsibility at a time.

## System definition

The intended harness will repeatedly:

1. select the context a model may see;
2. ask the model what to do next;
3. validate the proposed action;
4. dispatch permitted actions to the tool/runtime layer;
5. record outcomes and update run state;
6. continue within limits until completion criteria are met or the run stops.

This describes the planned architecture. The agent loop and tools are not
implemented yet.

## Governing rule

The model proposes. The harness controls.

The harness decides:

- what context is visible;
- what tools are available;
- whether proposed actions are valid and permitted;
- whether approval is required;
- what executes through the tool/runtime layer;
- what is persisted or remembered;
- when the task is considered complete.

## Version 0 scope

Version 0 will become a local, read-only repository assistant.

Initial capabilities:

- list directories;
- search text;
- read selected file ranges.

Initial non-goals:

- file writes;
- shell execution;
- network access;
- persistent memory;
- skills;
- subagents.

These capabilities will be introduced in later stages.

A task is a bounded objective with completion criteria, distinct from the
conversation about it. Event history records what happened; model context
is the information selected for one model call.

## Example tasks

Version 0 should be able to:

1. find where the CLI version is defined and report its references;
2. list the Python package structure and explain each file's responsibility;
3. inspect `pyproject.toml` and explain how the `kness` command is installed.

## Visual lesson

[Watch the Step 0 mental model animation](docs/animations/step-00-mental-model.html).

This is a conceptual walkthrough of mechanisms introduced in later stages.