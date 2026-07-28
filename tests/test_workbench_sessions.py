"""Tests for application-owned workbench sessions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.sessions import SessionManager  # noqa: E402


class SessionManagerTests(unittest.TestCase):
    def test_creates_application_session_without_exposing_runtime_id(self):
        manager = SessionManager()

        record = manager.get_or_create()
        snapshot = record.snapshot()

        self.assertRegex(record.session_id, r"^session_[0-9a-f]{32}$")
        self.assertFalse(snapshot["runtime_bound"])
        self.assertNotIn("runtime_thread_id", snapshot)

    def test_binds_private_runtime_thread_and_resumes_same_session(self):
        manager = SessionManager()
        record = manager.get_or_create()
        manager.bind_runtime_thread(record.session_id, "codex-thread-secret")

        resumed = manager.get_or_create(record.session_id)

        self.assertEqual(resumed.session_id, record.session_id)
        self.assertEqual(
            manager.runtime_thread_id(record.session_id),
            "codex-thread-secret",
        )
        self.assertTrue(resumed.snapshot()["runtime_bound"])
        self.assertNotIn("codex-thread-secret", str(resumed.snapshot()))

    def test_unknown_client_session_id_is_recreated_without_runtime_binding(self):
        manager = SessionManager()
        session_id = "session_" + ("a" * 32)

        record = manager.get_or_create(session_id)

        self.assertEqual(record.session_id, session_id)
        self.assertEqual(record.runtime_thread_id, "")

    def test_capacity_trims_oldest_session(self):
        manager = SessionManager(max_records=1)
        first = manager.get_or_create()
        second = manager.get_or_create()

        self.assertIsNone(manager.runtime_thread_id(first.session_id))
        self.assertEqual(manager.snapshot(second.session_id)["session_id"], second.session_id)

    def test_switching_runtime_creates_a_new_application_session(self):
        manager = SessionManager()
        codex = manager.get_or_create(runtime_name="codex")
        manager.bind_runtime_thread(codex.session_id, "codex-private")

        claude = manager.get_or_create(codex.session_id, runtime_name="claude")

        self.assertNotEqual(claude.session_id, codex.session_id)
        self.assertEqual(claude.runtime_name, "claude")
        self.assertEqual(claude.runtime_thread_id, "")


if __name__ == "__main__":
    unittest.main()
