"""Tests for launching the official Claude authentication flow."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.auth import ClaudeAuthLauncher  # noqa: E402


class FakeProcess:
    def __init__(self, poll_result=None):
        self.poll_result = poll_result

    def poll(self):
        return self.poll_result

    def wait(self):
        return 0


class ClaudeAuthLauncherTests(unittest.TestCase):
    def test_starts_official_subscription_login_without_capturing_credentials(self):
        launcher = ClaudeAuthLauncher("claude-test", REPO_ROOT)
        process = FakeProcess()

        with (
            patch.object(subprocess, "Popen", return_value=process) as popen,
            patch("workbench.auth.threading.Thread") as thread,
        ):
            result = launcher.start("claudeai")

        self.assertTrue(result["started"])
        self.assertEqual(
            popen.call_args.args[0],
            ["claude-test", "auth", "login", "--claudeai"],
        )
        self.assertIs(popen.call_args.kwargs["stdin"], subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs["stdout"], subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs["stderr"], subprocess.DEVNULL)
        thread.assert_called_once()

    def test_reuses_running_login_process(self):
        launcher = ClaudeAuthLauncher("claude-test", REPO_ROOT)
        launcher._process = FakeProcess(poll_result=None)

        with patch.object(subprocess, "Popen") as popen:
            result = launcher.start("claudeai")

        self.assertFalse(result["started"])
        self.assertTrue(result["already_running"])
        popen.assert_not_called()

    def test_rejects_unknown_authentication_mode(self):
        launcher = ClaudeAuthLauncher("claude-test", REPO_ROOT)

        with self.assertRaises(ValueError):
            launcher.start("password")


if __name__ == "__main__":
    unittest.main()
