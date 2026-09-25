from khosiness.event_store import JsonlEventStore
from khosiness.events import Event


def test_empty_store_loads_as_empty_list(tmp_path):
    store = JsonlEventStore(tmp_path / "events.jsonl")

    assert store.load_all() == []


def test_event_store_preserves_order(tmp_path):
    store = JsonlEventStore(tmp_path / "events.jsonl")

    store.append(Event(run_id="r1", type="first"))
    store.append(Event(run_id="r1", type="second"))

    assert [event.type for event in store.load_all()] == [
        "first",
        "second",
    ]


def test_event_payload_round_trips(tmp_path):
    store = JsonlEventStore(tmp_path / "events.jsonl")
    store.append(
        Event(
            run_id="r1",
            type="tool_completed",
            payload={"tool": "read_file", "ok": True},
        )
    )

    restored = store.load_all()[0]

    assert restored.payload == {
        "tool": "read_file",
        "ok": True,
    }


def test_many_events_round_trip(tmp_path):
    store = JsonlEventStore(tmp_path / "events.jsonl")

    for index in range(1000):
        store.append(
            Event(
                run_id="r1",
                type="tick",
                payload={"index": index},
            )
        )

    events = store.load_all()

    assert len(events) == 1000
    assert events[-1].payload["index"] == 999
