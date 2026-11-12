"""Regression tests for runtime process-tree cleanup."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.runtime.processes import terminate_process_tree  # noqa: E402


def process_is_running(pid: int) -> bool:
    result = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)],
        capture_output=True,
        text=True,
        check=False,
    )
    status = result.stdout.strip()
    return result.returncode == 0 and bool(status) and not status.startswith("Z")


@unittest.skipIf(os.name == "nt", "POSIX process-group regression")
class RuntimeProcessTreeTests(unittest.TestCase):
    def test_terminate_cleans_descendant_in_separate_session(self):
        script = (
            "import subprocess, sys, time; "
            "child = subprocess.Popen([sys.executable, '-c', "
            "'import time; time.sleep(60)'], start_new_session=True); "
            "print(child.pid, flush=True); time.sleep(60)"
        )
        parent = subprocess.Popen(
            [sys.executable, "-u", "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        child_pid = int(parent.stdout.readline().strip())
        self.assertTrue(process_is_running(child_pid))

        try:
            terminate_process_tree(parent, grace_seconds=0.5)
            parent.wait(timeout=3)
            deadline = time.monotonic() + 3
            while process_is_running(child_pid) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertFalse(process_is_running(child_pid))
        finally:
            if parent.poll() is None:
                parent.kill()
            if process_is_running(child_pid):
                os.kill(child_pid, 9)
            parent.stdout.close()
            parent.stderr.close()


if __name__ == "__main__":
    unittest.main()
