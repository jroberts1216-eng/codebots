from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Event:
    ts: float
    type: str
    payload: dict[str, Any]

    @staticmethod
    def now(event_type: str, **payload: Any) -> "Event":
        return Event(ts=time.time(), type=event_type, payload=payload)


class EventLogger:
    def __init__(self, path: Path):
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: Event) -> None:
        line = json.dumps(
            {"ts": event.ts, "type": event.type, "payload": event.payload}, ensure_ascii=False
        )
        with self._path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
