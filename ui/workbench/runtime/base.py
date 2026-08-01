"""Runtime-neutral contracts for AI task execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable


@dataclass(frozen=True)
class RuntimeRequest:
    prompt: str
    thread_id: str = ""
    sandbox: str = "read-only"
    effort: str = "medium"


@dataclass(frozen=True)
class RuntimeStatus:
    available: bool
    version: str
    authenticated: bool
    authentication_status: str
    model: str


@dataclass(frozen=True)
class RuntimeEvent:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)

    def legacy_payload(self) -> Dict[str, Any]:
        """Return the current browser event shape during protocol migration."""
        return {"type": self.type, **self.data}


class RuntimeSession(ABC):
    @abstractmethod
    def events(self) -> Iterable[RuntimeEvent]:
        """Yield normalized runtime events."""

    @abstractmethod
    def wait(self) -> int:
        """Wait for the runtime process and return its exit code."""

    @abstractmethod
    def stderr_tail(self, limit: int = 5) -> str:
        """Return recent diagnostic lines."""

    @abstractmethod
    def terminate(self) -> None:
        """Stop the runtime and any child process group."""


class RuntimeAdapter(ABC):
    @abstractmethod
    def status(self) -> RuntimeStatus:
        """Inspect runtime availability and authentication."""

    @abstractmethod
    def start(self, request: RuntimeRequest) -> RuntimeSession:
        """Start one runtime task."""
