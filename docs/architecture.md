# Architecture — Stage 0

## The six planes

### 1. Cognition

The model reasons and proposes the next action.

### 2. Context

The harness decides what information reaches the model.

### 3. Action

Tools translate validated model requests into operations against the outside
world.

### 4. Control

Policy, validation, budgets and approvals constrain actions.

### 5. Continuity

State, checkpoints, history and memory keep work coherent over time.

### 6. Measurement

Events, traces and evaluations reveal whether the system is reliable.

## First system boundary

```text
user task
   |
   v
harness
   |----> model
   |
   `----> read-only tools ----> workspace
```

The model never touches the workspace directly.
Harness validation and policy sit inside this control boundary. The tool/runtime
layer executes an action only after that boundary permits it.

## Ownership table

| Responsibility | Owner |
| --- | --- |
| reasoning | model |
| context selection | harness |
| tool validation | harness |
| tool execution | tool/runtime layer |
| permissions | harness policy |
| current run state | harness |
| durable history | event store |
| cross-run memory | memory subsystem, once introduced |
| completion | harness + task criteria |

## Stage 0 non-goals

No shell execution, file writes, network access, persistent memory, skills or
subagents yet.
