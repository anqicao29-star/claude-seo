"""Versioned event envelopes exposed by the workbench API."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional


PROTOCOL_NAME = "claude-seo.workbench"
PROTOCOL_VERSION = 1
EVENT_TYPES = {
    "session.bound",
    "task.started",
    "task.status",
    "task.activity",
    "assistant.message",
    "task.warning",
    "task.completed",
    "task.failed",
    "task.cancelled",
}
TERMINAL_EVENT_TYPES = {
    "task.completed",
    "task.failed",
    "task.cancelled",
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class EventStream:
    """Create ordered event envelopes and enforce one terminal event."""

    def __init__(
        self,
        task_id: Optional[str] = None,
        clock: Callable[[], str] = utc_timestamp,
    ):
        self.task_id = task_id or f"task_{uuid.uuid4().hex}"
        self.clock = clock
        self.sequence = 0
        self.terminal = False

    def event(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event type: {event_type}")
        if self.terminal:
            raise RuntimeError("cannot emit an event after the terminal event")

        self.sequence += 1
        envelope = {
            "protocol": PROTOCOL_NAME,
            "version": PROTOCOL_VERSION,
            "task_id": self.task_id,
            "event_id": f"evt_{uuid.uuid4().hex}",
            "sequence": self.sequence,
            "type": event_type,
            "timestamp": self.clock(),
            "data": data or {},
        }
        if event_type in TERMINAL_EVENT_TYPES:
            self.terminal = True
        return envelope

