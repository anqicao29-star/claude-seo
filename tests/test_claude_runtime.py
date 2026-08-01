"""Unit tests for the Claude Code CLI runtime adapter."""

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
from workbench.runtime.claude_cli import (  # noqa: E402
    ClaudeCliRuntime,
    normalize_claude_event,
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
    def __init__(self, stdout_lines=None, stderr_text="", return_code=0, poll_result=0):
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


class ClaudeEventTests(unittest.TestCase):
    def test_normalizes_session_text_tool_and_completion(self):
        init = normalize_claude_event(
            {"type": "system", "subtype": "init", "session_id": "claude-session"}
        )
        assistant = normalize_claude_event(
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "text", "text": "# 标题"},
                        {"type": "tool_use", "name": "Read", "input": {}},
                    ]
                },
            }
        )
        completed = normalize_claude_event(
            {"type": "result", "subtype": "success", "usage": {"tokens": 4}}
        )

        self.assertEqual(init[0].legacy_payload(), {"type": "thread", "thread_id": "claude-session"})
        self.assertEqual(init[1].type, "status")
        self.assertEqual(assistant[0].legacy_payload(), {"type": "assistant", "text": "# 标题"})
        self.assertEqual(assistant[1].data["text"], "Read")
        self.assertEqual(completed[0].legacy_payload(), {"type": "completed", "usage": {"tokens": 4}})

    def test_normalizes_failed_result(self):
        events = normalize_claude_event(
            {"type": "result", "subtype": "error_max_turns", "is_error": True, "result": "超出轮次"}
        )
        self.assertEqual(events[0].legacy_payload(), {"type": "error", "message": "超出轮次"})


class ClaudeCliRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = ClaudeCliRuntime("claude-test", "sonnet", REPO_ROOT)

    def test_builds_read_only_and_resume_commands(self):
        new_command = self.runtime.command(RuntimeRequest(prompt="文章", sandbox="read-only"))
        resume_command = self.runtime.command(
            RuntimeRequest(
                prompt="修改标题",
                thread_id="claude-session",
                sandbox="workspace-write",
            )
        )

        self.assertEqual(
            new_command,
            [
                "claude-test",
                "--print",
                "--output-format",
                "stream-json",
                "--verbose",
                "--model",
                "sonnet",
                "--effort",
                "medium",
                "--permission-mode",
                "plan",
                "--allowedTools",
                "Read,Glob,Grep,WebFetch,WebSearch",
            ],
        )
        self.assertEqual(resume_command[-4:], ["--permission-mode", "acceptEdits", "--resume", "claude-session"])

    def test_start_writes_prompt_and_streams_normalized_events(self):
        process = FakeProcess(
            stdout_lines=[
                json.dumps({"type": "system", "subtype": "init", "session_id": "session-1"}) + "\n",
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {"content": [{"type": "text", "text": "正文"}]},
                    },
                    ensure_ascii=False,
                )
                + "\n",
                json.dumps({"type": "result", "subtype": "success", "usage": {}}) + "\n",
            ],
            stderr_text="diagnostic\n",
        )

        with patch.object(subprocess, "Popen", return_value=process) as popen:
            session = self.runtime.start(RuntimeRequest(prompt="完整提示词"))
            events = [event.legacy_payload() for event in session.events()]
            return_code = session.wait()

        self.assertEqual(return_code, 0)
        self.assertEqual(events[0], {"type": "thread", "thread_id": "session-1"})
        self.assertIn({"type": "assistant", "text": "正文"}, events)
        self.assertEqual(process.stdin.text, "完整提示词")
        self.assertTrue(process.stdin.closed)
        self.assertEqual(session.stderr_tail(), "diagnostic")
        self.assertEqual(popen.call_args.kwargs["cwd"], REPO_ROOT)

    def test_status_uses_claude_auth_json(self):
        results = [
            SimpleNamespace(returncode=0, stdout="2.1.199 (Claude Code)", stderr=""),
            SimpleNamespace(
                returncode=0,
                stdout=json.dumps({"loggedIn": True, "authMethod": "claude.ai"}),
                stderr="",
            ),
        ]
        with patch.object(subprocess, "run", side_effect=results):
            status = self.runtime.status()

        self.assertTrue(status.available)
        self.assertTrue(status.authenticated)
        self.assertEqual(status.version, "2.1.199 (Claude Code)")
        self.assertEqual(status.authentication_status, "已登录")
        self.assertEqual(status.model, "sonnet")

    def test_status_reports_logged_out_json_cleanly(self):
        results = [
            SimpleNamespace(returncode=0, stdout="2.1.199 (Claude Code)", stderr=""),
            SimpleNamespace(
                returncode=1,
                stdout=json.dumps({"loggedIn": False, "authMethod": "none"}, indent=2),
                stderr="",
            ),
        ]
        with patch.object(subprocess, "run", side_effect=results):
            status = self.runtime.status()

        self.assertTrue(status.available)
        self.assertFalse(status.authenticated)
        self.assertEqual(status.authentication_status, "未登录")


if __name__ == "__main__":
    unittest.main()
