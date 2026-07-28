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
from workbench.sessions import SessionManager  # noqa: E402
from workbench.tasks import TaskManager  # noqa: E402


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


class BlockingRuntimeSession(FakeRuntimeSession):
    def __init__(self):
        super().__init__(return_code=143)
        self.released = threading.Event()

    def events(self):
        self.released.wait(timeout=3)
        return
        yield

    def terminate(self):
        super().terminate()
        self.released.set()


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
        self.started = threading.Event()

    def status(self):
        return self._status

    def start(self, request):
        self.request = request
        self.started.set()
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
        claude_runtime = FakeRuntime(
            status=RuntimeStatus(
                available=True,
                version="2.1.199 (Claude Code)",
                authenticated=True,
                authentication_status="已登录",
                model="sonnet",
            )
        )
        with (
            patch.object(server, "RUNTIME", runtime),
            patch.object(server, "CLAUDE_RUNTIME", claude_runtime),
        ):
            result = server.api_runtime()

        self.assertTrue(result["codex_available"])
        self.assertTrue(result["logged_in"])
        self.assertEqual(result["codex_version"], "codex-cli 1.2.3")
        self.assertEqual(result["login_status"], "Logged in using ChatGPT")
        self.assertEqual(result["max_sandbox"], server.MAX_SANDBOX)
        self.assertEqual(result["model"], "test-model")
        self.assertTrue(result["claude_available"])
        self.assertTrue(result["claude_logged_in"])
        self.assertEqual(result["claude_model"], "sonnet")
        self.assertEqual(result["routing"]["article"], "claude")
        self.assertEqual(
            result["max_concurrent_tasks"],
            server.MAX_CONCURRENT_TASKS,
        )
        self.assertEqual(result["task_timeout_seconds"], server.TASK_TIMEOUT_SECONDS)


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

    def setUp(self):
        self.task_manager = TaskManager()
        self.session_manager = SessionManager()
        self.tasks_patch = patch.object(server, "TASKS", self.task_manager)
        self.sessions_patch = patch.object(server, "SESSIONS", self.session_manager)
        self.tasks_patch.start()
        self.sessions_patch.start()

    def tearDown(self):
        self.sessions_patch.stop()
        self.tasks_patch.stop()

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

    def post_v1(self, payload):
        return self.request(
            "POST",
            "/api/v1/chat",
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

    def test_runtime_settings_update_concurrency_limit(self):
        status, _, body = self.request(
            "POST",
            "/api/settings/runtime",
            body=json.dumps({"max_concurrent_tasks": 3}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(status, 200)
        settings = json.loads(body)["settings"]
        self.assertEqual(settings["max_concurrent_tasks"], 3)
        self.assertEqual(settings["max_concurrent_tasks_limit"], 4)
        self.assertEqual(self.task_manager.get_max_active(), 3)

    def test_runtime_settings_reject_invalid_concurrency_values(self):
        for value in (0, 5, True, "2"):
            with self.subTest(value=value):
                status, _, body = self.request(
                    "POST",
                    "/api/settings/runtime",
                    body=json.dumps({"max_concurrent_tasks": value}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                self.assertEqual(status, 400)
                self.assert_api_error(
                    body,
                    server.ErrorCode.INVALID_FIELD,
                    "并发任务数必须是 1 到 4 的整数",
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
            (
                {"message": "test", "task_type": "video"},
                server.ErrorCode.INVALID_FIELD,
                "不支持的任务类型",
            ),
        ]

        for payload, code, message in cases:
            with self.subTest(payload=payload):
                status, _, body = self.post_json(payload)
                self.assertEqual(status, 400)
                self.assert_api_error(body, code, message)

    def test_v1_chat_rejects_runtime_thread_id_and_invalid_session_id(self):
        status, _, body = self.post_v1(
            {"message": "test", "thread_id": "codex-internal"}
        )
        self.assertEqual(status, 400)
        self.assert_api_error(
            body,
            server.ErrorCode.INVALID_FIELD,
            "v1 接口不接受 Runtime 会话 ID",
        )

        status, _, body = self.post_v1(
            {"message": "test", "session_id": "../invalid"}
        )
        self.assertEqual(status, 400)
        self.assert_api_error(
            body,
            server.ErrorCode.INVALID_FIELD,
            "应用会话 ID 不正确",
        )

    def test_v1_chat_uses_versioned_events_and_private_session_mapping(self):
        runtime = FakeRuntime(
            session=FakeRuntimeSession(
                events=[
                    RuntimeEvent("thread", {"thread_id": "codex-thread-private"}),
                    RuntimeEvent("status", {"text": "正在处理"}),
                    RuntimeEvent("assistant", {"text": "完成"}),
                    RuntimeEvent("completed", {"usage": {"tokens": 5}}),
                ]
            )
        )

        with patch.object(server, "RUNTIME", runtime):
            status, headers, body = self.post_v1(
                {"message": "分析页面", "sandbox": "read-only"}
            )

        self.assertEqual(status, 200)
        self.assertEqual(headers["X-Protocol-Version"], "1")
        self.assertRegex(headers["X-Session-ID"], r"^session_[0-9a-f]{32}$")
        events = [json.loads(line) for line in body.decode("utf-8").splitlines()]
        self.assertEqual(
            [event["type"] for event in events],
            [
                "session.bound",
                "task.started",
                "task.status",
                "assistant.message",
                "task.completed",
            ],
        )
        self.assertEqual(
            [event["sequence"] for event in events],
            list(range(1, len(events) + 1)),
        )
        self.assertTrue(all(event["protocol"] == "claude-seo.workbench" for event in events))
        self.assertEqual(sum(event["type"].startswith("task.") and event["type"] in {
            "task.completed", "task.failed", "task.cancelled"
        } for event in events), 1)
        self.assertNotIn("codex-thread-private", body.decode("utf-8"))
        self.assertEqual(
            self.session_manager.runtime_thread_id(headers["X-Session-ID"]),
            "codex-thread-private",
        )
        self.assertEqual(runtime.request.thread_id, "")

    def test_article_task_is_routed_to_claude(self):
        claude_runtime = FakeRuntime(
            session=FakeRuntimeSession(
                events=[
                    RuntimeEvent("thread", {"thread_id": "claude-private"}),
                    RuntimeEvent("assistant", {"text": "# 完整文章"}),
                    RuntimeEvent("completed", {"usage": {"tokens": 8}}),
                ]
            )
        )

        with patch.object(server, "CLAUDE_RUNTIME", claude_runtime):
            status, headers, body = self.post_v1(
                {
                    "message": "写一篇文章",
                    "task_type": "article",
                    "sandbox": "read-only",
                }
            )

        self.assertEqual(status, 200)
        self.assertEqual(headers["X-AI-Runtime"], "claude")
        self.assertIn("# 完整文章", body.decode("utf-8"))
        self.assertIn("真正完成用户要求的文章", claude_runtime.request.prompt)
        self.assertEqual(claude_runtime.request.thread_id, "")
        session_id = headers["X-Session-ID"]
        self.assertEqual(
            self.session_manager.runtime_thread_id(session_id),
            "claude-private",
        )
        self.assertEqual(
            self.session_manager.snapshot(session_id)["runtime"],
            "claude",
        )

    def test_v1_chat_resumes_using_private_runtime_mapping(self):
        session = self.session_manager.get_or_create()
        self.session_manager.bind_runtime_thread(
            session.session_id,
            "codex-thread-private",
        )
        runtime = FakeRuntime(
            session=FakeRuntimeSession(
                events=[
                    RuntimeEvent("assistant", {"text": "继续完成"}),
                    RuntimeEvent("completed", {"usage": {}}),
                ]
            )
        )

        with patch.object(server, "RUNTIME", runtime):
            status, headers, body = self.post_v1(
                {"message": "继续", "session_id": session.session_id}
            )

        self.assertEqual(status, 200)
        self.assertEqual(headers["X-Session-ID"], session.session_id)
        self.assertEqual(runtime.request.thread_id, "codex-thread-private")
        self.assertEqual(runtime.request.prompt, "继续")
        self.assertNotIn("codex-thread-private", body.decode("utf-8"))

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
        self.assertRegex(headers["X-Task-ID"], r"^task_[0-9a-f]{32}$")
        events = [json.loads(line) for line in body.decode("utf-8").splitlines()]
        self.assertEqual(events[0]["type"], "task")
        self.assertEqual(events[0]["task_id"], headers["X-Task-ID"])
        self.assertEqual(events[1], {"type": "thread", "thread_id": "thread-1"})
        self.assertEqual(events[2], {"type": "assistant", "text": "完成"})
        self.assertEqual(events[3]["type"], "completed")
        self.assertEqual(
            self.task_manager.get(headers["X-Task-ID"]).status,
            "completed",
        )
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
            [
                {
                    "type": "task",
                    "task_id": json.loads(body.decode("utf-8").splitlines()[0])["task_id"],
                },
                {"type": "error", "message": "diagnostic line"},
            ],
        )

    def test_cancel_endpoint_terminates_active_task(self):
        record = self.task_manager.create()
        session = FakeRuntimeSession()
        self.task_manager.bind_session(record.task_id, session)

        status, _, body = self.request(
            "POST",
            f"/api/tasks/{record.task_id}/cancel",
            body=b"{}",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["task"]["status"], "cancel_requested")
        self.assertTrue(session.terminated)

    def test_cancel_endpoint_stops_streaming_chat_end_to_end(self):
        session = BlockingRuntimeSession()
        runtime = FakeRuntime(session=session)
        result = {}

        def run_chat():
            result["response"] = self.post_v1({"message": "long task"})

        with patch.object(server, "RUNTIME", runtime):
            worker = threading.Thread(target=run_chat)
            worker.start()
            self.assertTrue(runtime.started.wait(timeout=1))
            task_id = self.task_manager.snapshots()[0]["task_id"]
            cancel_status, _, _ = self.request(
                "POST",
                f"/api/tasks/{task_id}/cancel",
                body=b"{}",
                headers={"Content-Type": "application/json"},
            )
            worker.join(timeout=3)

        self.assertFalse(worker.is_alive())
        self.assertEqual(cancel_status, 200)
        status, headers, body = result["response"]
        self.assertEqual(status, 200)
        self.assertEqual(headers["X-Task-ID"], task_id)
        events = [json.loads(line) for line in body.decode("utf-8").splitlines()]
        self.assertEqual(events[-1]["type"], "task.cancelled")
        self.assertEqual(events[-1]["task_id"], task_id)
        self.assertEqual(events[-1]["data"], {"reason": "user_requested"})
        self.assertTrue(
            all(event["protocol"] == "claude-seo.workbench" for event in events)
        )
        self.assertEqual(self.task_manager.get(task_id).status, "cancelled")
        self.assertTrue(session.terminated)

    def test_v1_chat_times_out_and_terminates_runtime(self):
        session = BlockingRuntimeSession()
        runtime = FakeRuntime(session=session)

        with patch.object(server, "RUNTIME", runtime):
            with patch.object(server, "TASK_TIMEOUT_SECONDS", 0.05):
                status, headers, body = self.post_v1({"message": "stuck task"})

        self.assertEqual(status, 200)
        task_id = headers["X-Task-ID"]
        events = [json.loads(line) for line in body.decode("utf-8").splitlines()]
        self.assertEqual(events[-1]["type"], "task.failed")
        self.assertEqual(events[-1]["data"]["code"], server.ErrorCode.TASK_TIMEOUT)
        self.assertIn("已自动停止", events[-1]["data"]["message"])
        self.assertEqual(self.task_manager.get(task_id).status, "timed_out")
        self.assertTrue(session.terminated)

    def test_second_active_chat_is_rejected_until_first_finishes(self):
        session = BlockingRuntimeSession()
        runtime = FakeRuntime(session=session)
        first_result = {}

        def run_first_chat():
            first_result["response"] = self.post_v1({"message": "first"})

        with patch.object(server, "RUNTIME", runtime):
            worker = threading.Thread(target=run_first_chat)
            worker.start()
            self.assertTrue(runtime.started.wait(timeout=1))
            status, _, body = self.post_v1({"message": "second"})
            task_id = self.task_manager.snapshots()[0]["task_id"]
            self.request(
                "POST",
                f"/api/tasks/{task_id}/cancel",
                body=b"{}",
                headers={"Content-Type": "application/json"},
            )
            worker.join(timeout=3)

        self.assertFalse(worker.is_alive())
        self.assertEqual(status, 429)
        error = json.loads(body)["error"]
        self.assertEqual(error["code"], server.ErrorCode.TASK_CAPACITY)
        self.assertTrue(error["retryable"])

    def test_cancel_endpoint_rejects_unknown_and_terminal_tasks(self):
        unknown_id = "task_" + ("0" * 32)
        status, _, body = self.request(
            "POST",
            f"/api/tasks/{unknown_id}/cancel",
            body=b"{}",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 404)
        self.assert_api_error(body, server.ErrorCode.TASK_NOT_FOUND, "任务不存在")

        record = self.task_manager.create()
        self.task_manager.finish(record.task_id, "completed")
        status, _, body = self.request(
            "POST",
            f"/api/tasks/{record.task_id}/cancel",
            body=b"{}",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 409)
        self.assert_api_error(
            body,
            server.ErrorCode.TASK_NOT_CANCELLABLE,
            "任务已经结束，无法取消",
        )


if __name__ == "__main__":
    unittest.main()
