"""Launch official local CLI authentication flows without handling credentials."""

from __future__ import annotations

import os
import subprocess
import threading
from pathlib import Path
from typing import Dict


CLAUDE_AUTH_MODES = {
    "claudeai": "--claudeai",
    "console": "--console",
}


class ClaudeAuthLauncher:
    def __init__(self, executable: str, workspace: Path):
        self.executable = executable
        self.workspace = workspace
        self._process = None
        self._lock = threading.RLock()

    def start(self, mode: str = "claudeai") -> Dict[str, object]:
        if mode not in CLAUDE_AUTH_MODES:
            raise ValueError("unsupported Claude authentication mode")
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                return {"started": False, "already_running": True, "mode": mode}
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
            self._process = subprocess.Popen(
                [
                    self.executable,
                    "auth",
                    "login",
                    CLAUDE_AUTH_MODES[mode],
                ],
                **options,
            )
            reaper = threading.Thread(target=self._process.wait, daemon=True)
            reaper.start()
            return {"started": True, "already_running": False, "mode": mode}
