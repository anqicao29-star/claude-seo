"""Tests for the cross-platform workbench launcher."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import run_workbench  # noqa: E402


class WorkbenchLauncherTests(unittest.TestCase):
    def test_service_paths_are_scoped_by_port(self):
        directory, pid_path, log_path = run_workbench.service_paths(7788)

        self.assertEqual(pid_path.parent, directory)
        self.assertEqual(log_path.parent, directory)
        self.assertEqual(pid_path.name, "workbench-7788.pid")
        self.assertEqual(log_path.name, "workbench-7788.log")

    def test_existing_background_service_is_reused(self):
        with (
            patch.object(run_workbench, "existing_workbench", return_value=True),
            patch.object(run_workbench.webbrowser, "open") as open_browser,
            patch.object(run_workbench.subprocess, "Popen") as popen,
        ):
            status = run_workbench.start_background(7777, open_browser=True)

        self.assertEqual(status, 0)
        open_browser.assert_called_once_with("http://localhost:7777")
        popen.assert_not_called()

    def test_stop_refuses_a_foreign_service(self):
        with (
            patch.object(
                run_workbench,
                "fetch_runtime",
                return_value={"workspace": "/tmp/not-this-project"},
            ),
            patch.object(run_workbench, "read_pid", return_value=1234),
            patch.object(run_workbench.os, "kill") as kill,
        ):
            status = run_workbench.stop_background(7777)

        self.assertEqual(status, 1)
        kill.assert_not_called()


if __name__ == "__main__":
    unittest.main()
