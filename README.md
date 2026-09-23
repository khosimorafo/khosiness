# khosiness — Harness Engineering From Scratch

A first-principles Python agent harness built one responsibility at a time.

## System definition

A harness is a control system that repeatedly:

1. selects the context a model may see;
2. asks the model what to do next;
3. validates the proposed action;
4. executes only permitted actions;
5. records what happened;
6. updates durable run state;
7. repeats until the task is complete.

## Governing rule

The model proposes.

The harness decides:

- what context is visible;
- what tools exist;
- whether a proposed action is valid;
- whether an action requires approval;
- what actually executes;
- what is persisted;
- what is remembered across runs;
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

The project deliberately adds those capabilities only after the simpler system
can be observed and tested.

A task is a bounded objective with completion criteria, not the conversation
that happens while solving it. Event history is the factual record of a run;
model context is the smaller view selected for one decision.

## Example tasks

Version 0 should be able to:

1. find where the CLI version is defined and report every reference;
2. list the Python package structure and explain each file's responsibility;
3. inspect `pyproject.toml` and explain how the `kness` command is installed.

## Visual lesson

[Watch the Step 0 mental model animation](docs/animations/step-00-mental-model.html).
It is a conceptual walkthrough; the loop and tools are implemented in later stages.
