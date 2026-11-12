"""Unit tests for the Codex CLI runtime adapter."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.runtime import RuntimeRequest  # noqa: E402
from workbench.runtime.codex_cli import (  # noqa: E402
    CodexCliRuntime,
    normalize_codex_event,
)


class CapturingStdin:
    def __init__(self):
        self.text = ""
        self.closed = False

    def write(self, value):
        self.text += value
        return len(value)

    def close(self):
        self.closed = True


class FakeProcess:
    def __init__(
        self,
        stdout_lines=None,
        stderr_text="",
        return_code=0,
        poll_result=0,
    ):
        self.stdin = CapturingStdin()
        self.stdout = iter(stdout_lines or [])
        self.stderr = io.StringIO(stderr_text)
        self.return_code = return_code
        self.poll_result = poll_result
        self.terminated = False
        self.pid = None

    def wait(self):
        return self.return_code

    def poll(self):
        return self.poll_result

    def terminate(self):
        self.terminated = True


class CodexEventTests(unittest.TestCase):
    def test_normalize_codex_event_maps_public_runtime_events(self):
        cases = [
            (
                {"type": "thread.started", "thread_id": "thread-1"},
                {"type": "thread", "thread_id": "thread-1"},
            ),
            (
                {"type": "turn.completed", "usage": {"tokens": 3}},
                {"type": "completed", "usage": {"tokens": 3}},
            ),
            (
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": "完成"},
                },
                {"type": "assistant", "text": "完成"},
            ),
            (
                {
                    "type": "item.started",
                    "item": {
                        "type": "command_execution",
                        "command": "python3 check.py",
                        "status": "in_progress",
                    },
                },
                {
                    "type": "activity",
                    "kind": "command",
                    "text": "python3 check.py",
                    "status": "in_progress",
                },
            ),
        ]

        for raw, expected in cases:
            with self.subTest(raw=raw):
                event = normalize_codex_event(raw)
                self.assertIsNotNone(event)
                self.assertEqual(event.legacy_payload(), expected)

    def test_normalize_codex_event_ignores_unknown_event(self):
        self.assertIsNone(normalize_codex_event({"type": "future.event"}))


class CodexCliRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = CodexCliRuntime("codex-test", "test-model", REPO_ROOT)

    def test_builds_new_and_resume_commands(self):
        new_command = self.runtime.command(
            RuntimeRequest(prompt="test", sandbox="read-only")
        )
        resume_command = self.runtime.command(
            RuntimeRequest(
                prompt="继续",
                thread_id="thread_123",
                sandbox="workspace-write",
            )
        )

        self.assertEqual(
            new_command,
            [
                "codex-test",
                "exec",
                "--model",
                "test-model",
                "--json",
                "--color",
                "never",
                "--sandbox",
                "read-only",
                "-c",
                'approval_policy="never"',
                "-c",
                'model_reasoning_effort="medium"',
                "--skip-git-repo-check",
                "-",
            ],
        )
        self.assertEqual(
            resume_command,
            [
                "codex-test",
                "exec",
                "resume",
                "--model",
                "test-model",
                "--json",
                "--skip-git-repo-check",
                "-c",
                'sandbox_mode="workspace-write"',
                "-c",
                'approval_policy="never"',
                "-c",
                'model_reasoning_effort="medium"',
                "thread_123",
                "-",
            ],
        )

    def test_start_writes_prompt_and_normalizes_json_stream(self):
        process = FakeProcess(
            stdout_lines=[
                "not-json\n",
                json.dumps({"type": "thread.started", "thread_id": "thread-1"}) + "\n",
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "完成"},
                    },
                    ensure_ascii=False,
                )
                + "\n",
            ],
            stderr_text="diagnostic\n",
        )

        with patch.object(subprocess, "Popen", return_value=process) as popen:
            session = self.runtime.start(
                RuntimeRequest(prompt="完整提示词", sandbox="read-only")
            )
            events = [event.legacy_payload() for event in session.events()]
            return_code = session.wait()

        self.assertEqual(return_code, 0)
        self.assertEqual(
            events,
            [
                {"type": "thread", "thread_id": "thread-1"},
                {"type": "assistant", "text": "完成"},
            ],
        )
        self.assertEqual(process.stdin.text, "完整提示词")
        self.assertTrue(process.stdin.closed)
        self.assertEqual(session.stderr_tail(), "diagnostic")
        self.assertEqual(popen.call_args.kwargs["cwd"], REPO_ROOT)
        self.assertTrue(popen.call_args.kwargs["start_new_session"])

    def test_fast_mode_skips_user_plugins_and_automatic_rules(self):
        command = self.runtime.command(
            RuntimeRequest(prompt="快速回答", effort="low")
        )

        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn('model_reasoning_effort="low"', command)

    def test_omits_model_flag_when_using_account_default(self):
        runtime = CodexCliRuntime("codex-test", "", REPO_ROOT)

        command = runtime.command(RuntimeRequest(prompt="使用默认模型"))

        self.assertNotIn("--model", command)

    def test_status_reports_last_cli_output_lines(self):
        results = [
            SimpleNamespace(returncode=0, stdout="notice\ncodex-cli 1.2.3", stderr=""),
            SimpleNamespace(returncode=0, stdout="notice\nLogged in", stderr=""),
        ]
        with patch.object(subprocess, "run", side_effect=results):
            status = self.runtime.status()

        self.assertTrue(status.available)
        self.assertTrue(status.authenticated)
        self.assertEqual(status.version, "codex-cli 1.2.3")
        self.assertEqual(status.authentication_status, "Logged in")
        self.assertEqual(status.model, "test-model")

    def test_session_termination_falls_back_to_direct_process(self):
        process = FakeProcess(poll_result=None)

        with patch.object(subprocess, "Popen", return_value=process):
            session = self.runtime.start(RuntimeRequest(prompt="test"))
            session.terminate()

        self.assertTrue(process.terminated)


if __name__ == "__main__":
    unittest.main()
