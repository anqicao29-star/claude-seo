"""Launch official local CLI authentication flows without handling credentials."""

from __future__ import annotations

import os
import subprocess
import threading
import time
from math import ceil
from pathlib import Path
from typing import Callable, Dict


CLAUDE_AUTH_MODES = {
    "claudeai": "--claudeai",
    "console": "--console",
}
DEFAULT_AUTH_TIMEOUT_SECONDS = 180
AUTH_TERMINATE_GRACE_SECONDS = 3


class ClaudeAuthLauncher:
    def __init__(
        self,
        executable: str,
        workspace: Path,
        timeout_seconds: int = DEFAULT_AUTH_TIMEOUT_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.executable = executable
        self.workspace = workspace
        self.timeout_seconds = max(30, int(timeout_seconds))
        self._clock = clock
        self._process = None
        self._started_at = None
        self._lock = threading.RLock()

    @staticmethod
    def _terminate_process(process) -> None:
        try:
            process.terminate()
        except OSError:
            return
        try:
            process.wait(timeout=AUTH_TERMINATE_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.wait(timeout=AUTH_TERMINATE_GRACE_SECONDS)
            except (OSError, subprocess.TimeoutExpired):
                pass

    def _clear_process(self, process) -> None:
        if self._process is process:
            self._process = None
            self._started_at = None

    def _watch_process(self, process) -> None:
        try:
            process.wait(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            with self._lock:
                if self._process is process and process.poll() is None:
                    self._terminate_process(process)
                self._clear_process(process)
        else:
            with self._lock:
                self._clear_process(process)

    def start(self, mode: str = "claudeai") -> Dict[str, object]:
        if mode not in CLAUDE_AUTH_MODES:
            raise ValueError("unsupported Claude authentication mode")
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                if self._started_at is None:
                    self._started_at = self._clock()
                elapsed = max(0.0, self._clock() - self._started_at)
                if elapsed < self.timeout_seconds:
                    return {
                        "started": False,
                        "already_running": True,
                        "mode": mode,
                        "expires_in_seconds": max(
                            0,
                            ceil(self.timeout_seconds - elapsed),
                        ),
                    }
                self._terminate_process(self._process)
                self._process = None
                self._started_at = None
            options = {
                "cwd": self.workspace,
                "env": os.environ.copy(),
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "start_new_session": os.name != "nt",
            }
            if os.name == "nt":
                options["creationflags"] = getattr(
                    subprocess,
                    "CREATE_NEW_PROCESS_GROUP",
                    0x00000200,
                )
            process = subprocess.Popen(
                [
                    self.executable,
                    "auth",
                    "login",
                    CLAUDE_AUTH_MODES[mode],
                ],
                **options,
            )
            self._process = process
            self._started_at = self._clock()
            watcher = threading.Thread(
                target=self._watch_process,
                args=(process,),
                daemon=True,
                name="claude-auth-timeout",
            )
            watcher.start()
            return {
                "started": True,
                "already_running": False,
                "mode": mode,
                "timeout_seconds": self.timeout_seconds,
            }
