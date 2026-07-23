"""Characterization tests for the local AI workbench.

These tests intentionally exercise the current public behavior before the
workbench is split into modules. They use a fake Codex process and never invoke
the real CLI, access the network, or modify project files.
"""

from __future__ import annotations

import http.client
import importlib.util
import io
import json
import threading
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = REPO_ROOT / "ui" / "server.py"
SERVER_SPEC = importlib.util.spec_from_file_location("workbench_server", SERVER_PATH)
server = importlib.util.module_from_spec(SERVER_SPEC)
assert SERVER_SPEC.loader is not None
SERVER_SPEC.loader.exec_module(server)


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
    def __init__(self, stdout_lines=None, stderr_text="", return_code=0):
        self.stdin = CapturingStdin()
        self.stdout = iter(stdout_lines or [])
        self.stderr = io.StringIO(stderr_text)
        self.return_code = return_code
        self.terminated = False

    def wait(self):
        return self.return_code

    def poll(self):
        return self.return_code

    def terminate(self):
        self.terminated = True


class WorkbenchFunctionTests(unittest.TestCase):
    def test_build_prompt_adds_guidance_for_new_thread(self):
        prompt = server.build_prompt("审计 example.com", "seo-audit", True)

        self.assertIn("用户任务：\n审计 example.com", prompt)
        self.assertIn("skills/seo-audit/SKILL.md", prompt)
        self.assertIn("claude-seo 项目根目录", prompt)

    def test_build_prompt_passes_resume_message_through(self):
        self.assertEqual(
            server.build_prompt("继续上一项任务", "seo-audit", False),
            "继续上一项任务",
        )

    def test_normalize_event_maps_thread_and_terminal_events(self):
        self.assertEqual(
            server.normalize_event({"type": "thread.started", "thread_id": "thread-1"}),
            {"type": "thread", "thread_id": "thread-1"},
        )
        self.assertEqual(
            server.normalize_event({"type": "turn.completed", "usage": {"tokens": 3}}),
            {"type": "completed", "usage": {"tokens": 3}},
        )
        self.assertEqual(
            server.normalize_event(
                {"type": "turn.failed", "error": {"message": "runtime failed"}}
            ),
            {"type": "error", "message": "runtime failed"},
        )

    def test_normalize_event_maps_agent_and_activity_items(self):
        self.assertEqual(
            server.normalize_event(
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": "完成"},
                }
            ),
            {"type": "assistant", "text": "完成"},
        )
        self.assertEqual(
            server.normalize_event(
                {
                    "type": "item.started",
                    "item": {
                        "type": "command_execution",
                        "command": "python3 check.py",
                        "status": "in_progress",
                    },
                }
            ),
            {
                "type": "activity",
                "kind": "command",
                "text": "python3 check.py",
                "status": "in_progress",
            },
        )

    def test_normalize_event_ignores_unknown_input(self):
        self.assertIsNone(server.normalize_event({"type": "future.event"}))

    def test_api_runtime_uses_last_output_lines(self):
        outputs = [
            (0, "notice\ncodex-cli 1.2.3"),
            (0, "notice\nLogged in using ChatGPT"),
        ]
        with patch.object(server, "command_output", side_effect=outputs) as command:
            result = server.api_runtime()

        self.assertTrue(result["codex_available"])
        self.assertTrue(result["logged_in"])
        self.assertEqual(result["codex_version"], "codex-cli 1.2.3")
        self.assertEqual(result["login_status"], "Logged in using ChatGPT")
        self.assertEqual(result["max_sandbox"], server.MAX_SANDBOX)
        self.assertEqual(
            command.call_args_list[0].args[0],
            [server.CODEX_BIN, "--version"],
        )
        self.assertEqual(
            command.call_args_list[1].args[0],
            [server.CODEX_BIN, "login", "status"],
        )


class WorkbenchHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        payload = response.read()
        result = response.status, dict(response.getheaders()), payload
        connection.close()
        return result

    def post_json(self, payload):
        return self.request(
            "POST",
            "/api/chat",
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

    def test_unknown_api_route_returns_json_404(self):
        status, headers, body = self.request(
            "POST",
            "/api/unknown",
            body=b"{}",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(status, 404)
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(json.loads(body), {"error": "未找到接口"})
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_chat_rejects_malformed_json(self):
        status, _, body = self.request(
            "POST",
            "/api/chat",
            body=b"{",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body), {"error": "请求不是有效 JSON"})

    def test_chat_rejects_non_json_cross_site_and_foreign_host_requests(self):
        status, _, body = self.request(
            "POST",
            "/api/chat",
            body=b'{"message":"test"}',
            headers={"Content-Type": "text/plain"},
        )
        self.assertEqual(status, 415)
        self.assertEqual(json.loads(body), {"error": "仅支持 application/json"})

        status, _, body = self.request(
            "POST",
            "/api/chat",
            body=b'{"message":"test"}',
            headers={
                "Content-Type": "application/json",
                "Origin": "https://attacker.example",
            },
        )
        self.assertEqual(status, 403)
        self.assertEqual(json.loads(body), {"error": "拒绝跨站请求"})

        status, _, body = self.request(
            "POST",
            "/api/chat",
            body=b'{"message":"test"}',
            headers={
                "Content-Type": "application/json",
                "Host": "attacker.example",
            },
        )
        self.assertEqual(status, 403)
        self.assertEqual(json.loads(body), {"error": "拒绝非本机请求"})

    def test_chat_defaults_to_read_only_server_policy(self):
        with patch.object(server, "MAX_SANDBOX", "read-only"):
            status, _, body = self.post_json(
                {"message": "test", "sandbox": "workspace-write"}
            )

        self.assertEqual(status, 403)
        self.assertEqual(json.loads(body), {"error": "服务当前仅允许只读任务"})

    def test_chat_rejects_invalid_thread_sandbox_and_skill(self):
        cases = [
            (
                {"message": "test", "thread_id": "../escape"},
                "会话 ID 不正确",
            ),
            (
                {"message": "test", "sandbox": "danger-full-access"},
                "不支持的权限模式",
            ),
            (
                {"message": "test", "skill": "seo-does-not-exist"},
                "选择的技能不存在",
            ),
        ]

        for payload, message in cases:
            with self.subTest(payload=payload):
                status, _, body = self.post_json(payload)
                self.assertEqual(status, 400)
                self.assertEqual(json.loads(body), {"error": message})

    def test_new_chat_builds_current_codex_command_and_streams_ndjson(self):
        process = FakeProcess(
            stdout_lines=[
                json.dumps({"type": "thread.started", "thread_id": "thread-1"}) + "\n",
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "完成"},
                    },
                    ensure_ascii=False,
                )
                + "\n",
                json.dumps({"type": "turn.completed", "usage": {"tokens": 5}})
                + "\n",
            ]
        )

        with patch.object(server.subprocess, "Popen", return_value=process) as popen:
            status, headers, body = self.post_json(
                {
                    "message": "分析这个页面",
                    "skill": "seo-page",
                    "sandbox": "read-only",
                }
            )

        self.assertEqual(status, 200)
        self.assertIn("application/x-ndjson", headers["Content-Type"])
        events = [json.loads(line) for line in body.decode("utf-8").splitlines()]
        self.assertEqual(events[0], {"type": "thread", "thread_id": "thread-1"})
        self.assertEqual(events[1], {"type": "assistant", "text": "完成"})
        self.assertEqual(events[2]["type"], "completed")
        command = popen.call_args.args[0]
        self.assertEqual(
            command,
            [
                server.CODEX_BIN,
                "exec",
                "--model",
                server.CODEX_MODEL,
                "--json",
                "--color",
                "never",
                "--sandbox",
                "read-only",
                "-c",
                'approval_policy="never"',
                "--skip-git-repo-check",
                "-",
            ],
        )
        self.assertIn("用户任务：\n分析这个页面", process.stdin.text)
        self.assertTrue(process.stdin.closed)

    def test_resume_chat_uses_thread_id_and_requested_sandbox(self):
        process = FakeProcess(
            stdout_lines=[
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "继续完成"},
                    },
                    ensure_ascii=False,
                )
                + "\n"
            ]
        )

        with patch.object(server, "MAX_SANDBOX", "workspace-write"):
            with patch.object(server.subprocess, "Popen", return_value=process) as popen:
                status, _, _ = self.post_json(
                    {
                        "message": "继续",
                        "thread_id": "thread_123",
                        "sandbox": "workspace-write",
                    }
                )

        self.assertEqual(status, 200)
        self.assertEqual(
            popen.call_args.args[0],
            [
                server.CODEX_BIN,
                "exec",
                "resume",
                "--model",
                server.CODEX_MODEL,
                "--json",
                "--skip-git-repo-check",
                "-c",
                'sandbox_mode="workspace-write"',
                "-c",
                'approval_policy="never"',
                "thread_123",
                "-",
            ],
        )
        self.assertEqual(process.stdin.text, "继续")

    def test_process_failure_falls_back_to_recent_stderr(self):
        process = FakeProcess(stderr_text="diagnostic line\n", return_code=7)

        with patch.object(server.subprocess, "Popen", return_value=process):
            status, _, body = self.post_json({"message": "test"})

        self.assertEqual(status, 200)
        self.assertEqual(
            [json.loads(line) for line in body.decode("utf-8").splitlines()],
            [{"type": "error", "message": "diagnostic line"}],
        )


if __name__ == "__main__":
    unittest.main()
