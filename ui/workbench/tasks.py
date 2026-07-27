"""Thread-safe in-memory task lifecycle management."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .runtime import RuntimeSession


TERMINAL_STATUSES = {"completed", "failed", "cancelled", "timed_out"}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class TaskNotFoundError(KeyError):
    pass


class TaskNotCancellableError(RuntimeError):
    pass


class TaskCapacityError(RuntimeError):
    pass


@dataclass
class TaskRecord:
    task_id: str
    status: str
    created_at: str
    updated_at: str
    runtime_session: Optional[RuntimeSession] = None

    def snapshot(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskManager:
    def __init__(self, max_records: int = 100, max_active: int = 1):
        self.max_records = max_records
        self.max_active = max_active
        self._records: Dict[str, TaskRecord] = {}
        self._lock = threading.RLock()

    def set_max_active(self, max_active: int) -> int:
        if not isinstance(max_active, int) or isinstance(max_active, bool):
            raise ValueError("max_active must be an integer")
        if max_active < 1 or max_active > 4:
            raise ValueError("max_active must be between 1 and 4")
        with self._lock:
            self.max_active = max_active
            return self.max_active

    def get_max_active(self) -> int:
        with self._lock:
            return self.max_active

    def _trim_terminal_records(self) -> None:
        terminal = [
            record
            for record in self._records.values()
            if record.status in TERMINAL_STATUSES
        ]
        terminal.sort(key=lambda record: record.updated_at)
        while len(self._records) >= self.max_records and terminal:
            record = terminal.pop(0)
            self._records.pop(record.task_id, None)

    def create(self) -> TaskRecord:
        with self._lock:
            self._trim_terminal_records()
            active_count = sum(
                record.status not in TERMINAL_STATUSES
                for record in self._records.values()
            )
            if active_count >= self.max_active:
                raise TaskCapacityError("active task limit reached")
            if len(self._records) >= self.max_records:
                raise TaskCapacityError("task registry is full")
            now = utc_timestamp()
            record = TaskRecord(
                task_id=f"task_{uuid.uuid4().hex}",
                status="starting",
                created_at=now,
                updated_at=now,
            )
            self._records[record.task_id] = record
            return record

    def get(self, task_id: str) -> TaskRecord:
        with self._lock:
            record = self._records.get(task_id)
            if record is None:
                raise TaskNotFoundError(task_id)
            return record

    def bind_session(self, task_id: str, session: RuntimeSession) -> Dict[str, Any]:
        should_terminate = False
        with self._lock:
            record = self.get(task_id)
            record.runtime_session = session
            if record.status == "cancel_requested":
                should_terminate = True
            elif record.status not in TERMINAL_STATUSES:
                record.status = "running"
                record.updated_at = utc_timestamp()
            snapshot = record.snapshot()
        if should_terminate:
            session.terminate()
        return snapshot

    def cancel(self, task_id: str) -> Dict[str, Any]:
        session = None
        with self._lock:
            record = self.get(task_id)
            if record.status in TERMINAL_STATUSES:
                raise TaskNotCancellableError(record.status)
            if record.status == "timeout_requested":
                raise TaskNotCancellableError(record.status)
            if record.status != "cancel_requested":
                record.status = "cancel_requested"
                record.updated_at = utc_timestamp()
            session = record.runtime_session
            snapshot = record.snapshot()
        if session is not None:
            session.terminate()
        return snapshot

    def request_timeout(self, task_id: str) -> Dict[str, Any]:
        session = None
        with self._lock:
            record = self.get(task_id)
            if record.status in TERMINAL_STATUSES:
                raise TaskNotCancellableError(record.status)
            if record.status != "cancel_requested":
                record.status = "timeout_requested"
                record.updated_at = utc_timestamp()
            session = record.runtime_session
            snapshot = record.snapshot()
        if session is not None:
            session.terminate()
        return snapshot

    def finish(self, task_id: str, status: str) -> Dict[str, Any]:
        if status not in TERMINAL_STATUSES:
            raise ValueError(f"invalid terminal status: {status}")
        with self._lock:
            record = self.get(task_id)
            if record.status == "cancel_requested":
                status = "cancelled"
            elif record.status == "timeout_requested":
                status = "timed_out"
            record.status = status
            record.runtime_session = None
            record.updated_at = utc_timestamp()
            return record.snapshot()

    def is_cancel_requested(self, task_id: str) -> bool:
        with self._lock:
            return self.get(task_id).status == "cancel_requested"

    def is_timeout_requested(self, task_id: str) -> bool:
        with self._lock:
            return self.get(task_id).status == "timeout_requested"

    def snapshots(self):
        with self._lock:
            return [record.snapshot() for record in self._records.values()]
