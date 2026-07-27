"""Application-owned session IDs mapped to private Runtime thread IDs."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class SessionRecord:
    session_id: str
    runtime_thread_id: str
    created_at: str
    updated_at: str

    def snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "runtime_bound": bool(self.runtime_thread_id),
        }


class SessionManager:
    def __init__(self, max_records: int = 100):
        self.max_records = max_records
        self._records: Dict[str, SessionRecord] = {}
        self._lock = threading.RLock()

    def _trim_oldest(self) -> None:
        while len(self._records) >= self.max_records:
            oldest = min(self._records.values(), key=lambda record: record.updated_at)
            self._records.pop(oldest.session_id, None)

    def get_or_create(self, session_id: str = "") -> SessionRecord:
        with self._lock:
            if session_id and session_id in self._records:
                record = self._records[session_id]
                record.updated_at = utc_timestamp()
                return record
            self._trim_oldest()
            now = utc_timestamp()
            record = SessionRecord(
                session_id=session_id or f"session_{uuid.uuid4().hex}",
                runtime_thread_id="",
                created_at=now,
                updated_at=now,
            )
            self._records[record.session_id] = record
            return record

    def bind_runtime_thread(self, session_id: str, runtime_thread_id: str) -> Dict[str, Any]:
        with self._lock:
            record = self._records[session_id]
            record.runtime_thread_id = runtime_thread_id
            record.updated_at = utc_timestamp()
            return record.snapshot()

    def runtime_thread_id(self, session_id: str) -> Optional[str]:
        with self._lock:
            record = self._records.get(session_id)
            return record.runtime_thread_id if record else None

    def snapshot(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._records[session_id].snapshot()

