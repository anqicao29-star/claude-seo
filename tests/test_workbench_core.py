"""Tests for the workbench configuration, error, and protocol modules."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.config import load_config  # noqa: E402
from workbench.errors import ErrorCode, error_payload  # noqa: E402
from workbench.protocol import (  # noqa: E402
    PROTOCOL_NAME,
    PROTOCOL_VERSION,
    EventStream,
)


class ConfigTests(unittest.TestCase):
    def test_load_config_uses_explicit_runtime_values(self):
        config = load_config(
            REPO_ROOT / "ui" / "server.py",
            {
                "CLAUDE_SEO_CODEX_BIN": "/opt/codex",
                "CLAUDE_SEO_CODEX_MODEL": "test-model",
                "CLAUDE_SEO_MAX_SANDBOX": "workspace-write",
            },
        )

        self.assertEqual(config.project_dir, REPO_ROOT)
        self.assertEqual(config.ui_dir, UI_DIR)
        self.assertEqual(config.codex_bin, "/opt/codex")
        self.assertEqual(config.codex_model, "test-model")
        self.assertEqual(config.max_sandbox, "workspace-write")

    def test_invalid_sandbox_configuration_fails_closed(self):
        config = load_config(
            REPO_ROOT / "ui" / "server.py",
            {"CLAUDE_SEO_MAX_SANDBOX": "danger-full-access"},
        )

        self.assertEqual(config.max_sandbox, "read-only")


class ErrorTests(unittest.TestCase):
    def test_error_payload_has_stable_machine_fields(self):
        payload = error_payload(
            ErrorCode.INVALID_JSON,
            "请求不是有效 JSON",
            "req_test",
        )

        self.assertEqual(
            payload,
            {
                "error": {
                    "code": "request.invalid_json",
                    "message": "请求不是有效 JSON",
                    "retryable": False,
                    "request_id": "req_test",
                    "details": {},
                }
            },
        )


class ProtocolTests(unittest.TestCase):
    def test_event_stream_emits_versioned_ordered_events(self):
        stream = EventStream(task_id="task_test", clock=lambda: "2026-07-23T00:00:00Z")

        started = stream.event("task.started", {"status": "running"})
        completed = stream.event("task.completed", {"usage": {"tokens": 3}})

        self.assertEqual(started["protocol"], PROTOCOL_NAME)
        self.assertEqual(started["version"], PROTOCOL_VERSION)
        self.assertEqual(started["task_id"], "task_test")
        self.assertEqual(started["sequence"], 1)
        self.assertEqual(started["type"], "task.started")
        self.assertEqual(started["timestamp"], "2026-07-23T00:00:00Z")
        self.assertRegex(started["event_id"], r"^evt_[0-9a-f]{32}$")
        self.assertEqual(completed["sequence"], 2)
        self.assertEqual(completed["type"], "task.completed")

    def test_event_stream_rejects_unknown_and_post_terminal_events(self):
        stream = EventStream(task_id="task_test")

        with self.assertRaisesRegex(ValueError, "unsupported event type"):
            stream.event("runtime.raw")
        stream.event("task.failed", {"code": "runtime.process_failed"})
        with self.assertRaisesRegex(RuntimeError, "after the terminal event"):
            stream.event("task.status", {"text": "late"})


if __name__ == "__main__":
    unittest.main()
