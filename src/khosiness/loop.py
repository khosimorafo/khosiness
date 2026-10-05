from collections.abc import Callable

from .event_store import JsonlEventStore
from .events import Event
from .state import RunState
from .task import Task


def run(
    *,
    task: Task,
    state: RunState,
    model,
    context_builder,
    tools,
    events: JsonlEventStore,
    save_state: Callable[[RunState], None] | None = None,
) -> RunState:
    """Run a bounded observe → decide → act cycle."""

    save_state = save_state or (lambda _: None)

    while not state.finished and state.step < task.max_steps:
        state.step += 1
        messages = context_builder.build(task, state)

        events.append(
            Event(
                run_id=state.run_id,
                type="model_called",
                payload={"step": state.step},
            )
        )

        response = model.generate(
            messages=messages,
            tools=tools.schemas(),
        )

        events.append(
            Event(
                run_id=state.run_id,
                type="model_responded",
                payload={
                    "step": state.step,
                    "has_text": response.text is not None,
                    "tool_call_count": len(response.tool_calls),
                },
            )
        )

        if response.tool_calls:
            for call in response.tool_calls:
                events.append(
                    Event(
                        run_id=state.run_id,
                        type="tool_requested",
                        payload={
                            "name": call.name,
                            "arguments": call.arguments,
                        },
                    )
                )

                result = tools.execute(call)
                state.observations.append(
                    {
                        "tool": call.name,
                        "arguments": call.arguments,
                        "result": result.model_dump(),
                    }
                )

                events.append(
                    Event(
                        run_id=state.run_id,
                        type="tool_completed" if result.ok else "tool_failed",
                        payload={
                            "name": call.name,
                            "ok": result.ok,
                        },
                    )
                )

        elif response.text is not None:
            state.finished = True
            state.final_answer = response.text
            events.append(
                Event(
                    run_id=state.run_id,
                    type="task_completed",
                    payload={"step": state.step},
                )
            )

        save_state(state)

    if not state.finished and state.step >= task.max_steps:
        events.append(
            Event(
                run_id=state.run_id,
                type="step_limit_reached",
                payload={"max_steps": task.max_steps},
            )
        )

    return state
