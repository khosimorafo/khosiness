from pathlib import Path

from .events import Event


class JsonlEventStore:
    """Append-only JSON Lines event store."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")
            handle.flush()

    def load_all(self) -> list[Event]:
        if not self.path.exists():
            return []

        events: list[Event] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    events.append(Event.model_validate_json(line))
        return events
