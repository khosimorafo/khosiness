# Architecture — Stage 0

This document defines the intended architecture. The agent runtime is not
implemented yet.

## The six planes

### 1. Cognition

The model reasons over supplied context and proposes the next action.

### 2. Context

The harness selects what information reaches the model for each call.
Stored information is not automatically included.

### 3. Action

The tool/runtime layer performs operations dispatched by the harness after
validation and permission checks.

### 4. Control

The harness uses validation, policy, budgets, and approvals to constrain
what may execute and when a run must stop.

### 5. Continuity

Separate mechanisms keep work coherent over time:

- run state tracks the current working position;
- event history records factual occurrences;
- checkpoints preserve recoverable state;
- memory, once introduced, preserves selected knowledge across runs.

### 6. Measurement

Traces and evaluations use recorded evidence to assess behavior and
whether task criteria were met.

## First system boundary

```text
user task
    |
    v
  harness -----> model
    |              |
    | <---- proposed action
    |
 validation and policy
    |
 permitted dispatch
    v
read-only tools -----> workspace
    |
 result
    v
  harness
```

The model does not access the workspace directly.
The harness decides whether an action may proceed.
The tool/runtime layer performs the permitted operation.

## Ownership table

| Responsibility             | Owner                                    |
| -------------------------- | ---------------------------------------- |
| Reasoning and proposals    | Model                                    |
| Context selection          | Harness context builder                  |
| Proposed-action validation | Harness                                  |
| Permissions and approvals  | Harness policy                           |
| Tool execution             | Tool/runtime layer                       |
| Current run state          | Harness                                  |
| Durable event history      | Event store                              |
| Cross-run memory           | Memory subsystem, once introduced        |
| Completion decision        | Harness, evaluated against task criteria |

A model's final answer is a proposal to finish. It does not by itself prove
that the task's success criteria were satisfied.

## Stage 0 non-goals

This stage documents boundaries; it implements no agent behavior.

Version 0 is planned as a local, read-only repository assistant.
File writes, shell execution, network access, persistent memory, skills,
and subagents remain outside its initial scope.