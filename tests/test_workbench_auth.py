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
        self.terminated = False
        self.killed = False

    def poll(self):
        return self.poll_result

    def wait(self, timeout=None):
        if timeout is not None and self.poll_result is None:
            raise subprocess.TimeoutExpired("claude-test", timeout)
        return 0

    def terminate(self):
        self.terminated = True
        self.poll_result = -15

    def kill(self):
        self.killed = True
        self.poll_result = -9


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
        thread.return_value.start.assert_called_once()
        self.assertEqual(result["timeout_seconds"], 180)

    def test_reuses_running_login_process(self):
        launcher = ClaudeAuthLauncher("claude-test", REPO_ROOT)
        launcher._process = FakeProcess(poll_result=None)

        with patch.object(subprocess, "Popen") as popen:
            result = launcher.start("claudeai")

        self.assertFalse(result["started"])
        self.assertTrue(result["already_running"])
        self.assertGreater(result["expires_in_seconds"], 0)
        popen.assert_not_called()

    def test_expired_login_process_is_terminated_and_restarted(self):
        launcher = ClaudeAuthLauncher(
            "claude-test",
            REPO_ROOT,
            timeout_seconds=60,
            clock=lambda: 200.0,
        )
        expired_process = FakeProcess(poll_result=None)
        replacement_process = FakeProcess(poll_result=None)
        launcher._process = expired_process
        launcher._started_at = 100.0

        with (
            patch.object(subprocess, "Popen", return_value=replacement_process) as popen,
            patch("workbench.auth.threading.Thread"),
        ):
            result = launcher.start("claudeai")

        self.assertTrue(expired_process.terminated)
        self.assertTrue(result["started"])
        self.assertIs(launcher._process, replacement_process)
        popen.assert_called_once()

    def test_watcher_terminates_login_when_timeout_expires(self):
        launcher = ClaudeAuthLauncher(
            "claude-test",
            REPO_ROOT,
            timeout_seconds=60,
        )
        process = FakeProcess(poll_result=None)
        launcher._process = process
        launcher._started_at = 100.0

        launcher._watch_process(process)

        self.assertTrue(process.terminated)
        self.assertIsNone(launcher._process)
        self.assertIsNone(launcher._started_at)

    def test_rejects_unknown_authentication_mode(self):
        launcher = ClaudeAuthLauncher("claude-test", REPO_ROOT)

        with self.assertRaises(ValueError):
            launcher.start("password")


if __name__ == "__main__":
    unittest.main()
