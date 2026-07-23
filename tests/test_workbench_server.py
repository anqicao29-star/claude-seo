"""Characterization tests for the local AI workbench.

These tests intentionally exercise the current public behavior before the
workbench is split into modules. They use a fake Codex process and never invoke
the real CLI, access the network, or modify project files.
"""

from __future__ import annotations

import http.client
import importlib.util
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

from workbench.runtime import RuntimeEvent, RuntimeStatus  # noqa: E402


class FakeRuntimeSession:
    def __init__(self, events=None, stderr_text="", return_code=0):
        self._events = events or []
        self.stderr_text = stderr_text
        self.return_code = return_code
        self.terminated = False

    def events(self):
        yield from self._events

    def wait(self):
        return self.return_code

    def stderr_tail(self, limit=5):
        return self.stderr_text

    def terminate(self):
        self.terminated = True


class FakeRuntime:
    def __init__(self, session=None, status=None):
        self.session = session or FakeRuntimeSession()
        self._status = status or RuntimeStatus(
            available=True,
            version="codex-cli test",
            authenticated=True,
            authentication_status="Logged in",
            model="test-model",
        )
        self.request = None

    def status(self):
        return self._status

    def start(self, request):
        self.request = request
        return self.session


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

    def test_api_runtime_uses_last_output_lines(self):
        runtime = FakeRuntime(
            status=RuntimeStatus(
                available=True,
                version="codex-cli 1.2.3",
                authenticated=True,
                authentication_status="Logged in using ChatGPT",
                model="test-model",
            )
        )
        with patch.object(server, "RUNTIME", runtime):
            result = server.api_runtime()

        self.assertTrue(result["codex_available"])
        self.assertTrue(result["logged_in"])
        self.assertEqual(result["codex_version"], "codex-cli 1.2.3")
        self.assertEqual(result["login_status"], "Logged in using ChatGPT")
        self.assertEqual(result["max_sandbox"], server.MAX_SANDBOX)
        self.assertEqual(result["model"], "test-model")


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

    def assert_api_error(self, body, code, message):
        error = json.loads(body)["error"]
        self.assertEqual(error["code"], code)
        self.assertEqual(error["message"], message)
        self.assertFalse(error["retryable"])
        self.assertRegex(error["request_id"], r"^req_[0-9a-f]{32}$")
        self.assertEqual(error["details"], {})

    def test_unknown_api_route_returns_json_404(self):
        status, headers, body = self.request(
            "POST",
            "/api/unknown",
            body=b"{}",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(status, 404)
        self.assertIn("application/json", headers["Content-Type"])
        self.assert_api_error(body, server.ErrorCode.ROUTE_NOT_FOUND, "未找到接口")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertRegex(headers["X-Request-ID"], r"^req_[0-9a-f]{32}$")

    def test_chat_rejects_malformed_json(self):
        status, _, body = self.request(
            "POST",
            "/api/chat",
            body=b"{",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assert_api_error(body, server.ErrorCode.INVALID_JSON, "请求不是有效 JSON")

    def test_chat_rejects_non_json_cross_site_and_foreign_host_requests(self):
        status, _, body = self.request(
            "POST",
            "/api/chat",
            body=b'{"message":"test"}',
            headers={"Content-Type": "text/plain"},
        )
        self.assertEqual(status, 415)
        self.assert_api_error(
            body,
            server.ErrorCode.UNSUPPORTED_MEDIA_TYPE,
            "仅支持 application/json",
        )

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
        self.assert_api_error(body, server.ErrorCode.ORIGIN_DENIED, "拒绝跨站请求")

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
        self.assert_api_error(body, server.ErrorCode.HOST_DENIED, "拒绝非本机请求")

    def test_chat_defaults_to_read_only_server_policy(self):
        with patch.object(server, "MAX_SANDBOX", "read-only"):
            status, _, body = self.post_json(
                {"message": "test", "sandbox": "workspace-write"}
            )

        self.assertEqual(status, 403)
        self.assert_api_error(
            body,
            server.ErrorCode.MODE_DENIED,
            "服务当前仅允许只读任务",
        )

    def test_chat_rejects_invalid_thread_sandbox_and_skill(self):
        cases = [
            (
                {"message": "test", "thread_id": "../escape"},
                server.ErrorCode.INVALID_FIELD,
                "会话 ID 不正确",
            ),
            (
                {"message": "test", "sandbox": "danger-full-access"},
                server.ErrorCode.INVALID_FIELD,
                "不支持的权限模式",
            ),
            (
                {"message": "test", "skill": "seo-does-not-exist"},
                server.ErrorCode.SKILL_NOT_FOUND,
                "选择的技能不存在",
            ),
        ]

        for payload, code, message in cases:
            with self.subTest(payload=payload):
                status, _, body = self.post_json(payload)
                self.assertEqual(status, 400)
                self.assert_api_error(body, code, message)

    def test_new_chat_builds_current_codex_command_and_streams_ndjson(self):
        session = FakeRuntimeSession(
            events=[
                RuntimeEvent("thread", {"thread_id": "thread-1"}),
                RuntimeEvent("assistant", {"text": "完成"}),
                RuntimeEvent("completed", {"usage": {"tokens": 5}}),
            ]
        )
        runtime = FakeRuntime(session=session)

        with patch.object(server, "RUNTIME", runtime):
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
        self.assertEqual(runtime.request.sandbox, "read-only")
        self.assertEqual(runtime.request.thread_id, "")
        self.assertIn("用户任务：\n分析这个页面", runtime.request.prompt)
        self.assertTrue(session.terminated)

    def test_resume_chat_uses_thread_id_and_requested_sandbox(self):
        runtime = FakeRuntime(
            session=FakeRuntimeSession(
                events=[RuntimeEvent("assistant", {"text": "继续完成"})]
            )
        )

        with patch.object(server, "MAX_SANDBOX", "workspace-write"):
            with patch.object(server, "RUNTIME", runtime):
                status, _, _ = self.post_json(
                    {
                        "message": "继续",
                        "thread_id": "thread_123",
                        "sandbox": "workspace-write",
                    }
                )

        self.assertEqual(status, 200)
        self.assertEqual(runtime.request.thread_id, "thread_123")
        self.assertEqual(runtime.request.sandbox, "workspace-write")
        self.assertEqual(runtime.request.prompt, "继续")

    def test_process_failure_falls_back_to_recent_stderr(self):
        runtime = FakeRuntime(
            session=FakeRuntimeSession(
                stderr_text="diagnostic line",
                return_code=7,
            )
        )

        with patch.object(server, "RUNTIME", runtime):
            status, _, body = self.post_json({"message": "test"})

        self.assertEqual(status, 200)
        self.assertEqual(
            [json.loads(line) for line in body.decode("utf-8").splitlines()],
            [{"type": "error", "message": "diagnostic line"}],
        )


if __name__ == "__main__":
    unittest.main()
