"""Tests for workbench task lifecycle and cancellation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.tasks import (  # noqa: E402
    TaskCapacityError,
    TaskManager,
    TaskNotCancellableError,
)


class FakeSession:
    def __init__(self):
        self.terminated = False

    def terminate(self):
        self.terminated = True


class TaskManagerTests(unittest.TestCase):
    def test_create_bind_finish_lifecycle(self):
        manager = TaskManager()
        record = manager.create()
        session = FakeSession()

        self.assertRegex(record.task_id, r"^task_[0-9a-f]{32}$")
        self.assertEqual(record.status, "starting")
        self.assertEqual(manager.bind_session(record.task_id, session)["status"], "running")
        self.assertEqual(manager.finish(record.task_id, "completed")["status"], "completed")
        self.assertIsNone(manager.get(record.task_id).runtime_session)

    def test_cancel_terminates_bound_runtime_session(self):
        manager = TaskManager()
        record = manager.create()
        session = FakeSession()
        manager.bind_session(record.task_id, session)

        snapshot = manager.cancel(record.task_id)

        self.assertEqual(snapshot["status"], "cancel_requested")
        self.assertTrue(session.terminated)
        self.assertEqual(manager.finish(record.task_id, "failed")["status"], "cancelled")

    def test_cancel_before_runtime_bind_terminates_session_when_bound(self):
        manager = TaskManager()
        record = manager.create()
        manager.cancel(record.task_id)
        session = FakeSession()

        snapshot = manager.bind_session(record.task_id, session)

        self.assertEqual(snapshot["status"], "cancel_requested")
        self.assertTrue(session.terminated)

    def test_terminal_task_cannot_be_cancelled(self):
        manager = TaskManager()
        record = manager.create()
        manager.finish(record.task_id, "completed")

        with self.assertRaises(TaskNotCancellableError):
            manager.cancel(record.task_id)

    def test_capacity_rejects_new_active_task(self):
        manager = TaskManager(max_records=1)
        manager.create()

        with self.assertRaises(TaskCapacityError):
            manager.create()


if __name__ == "__main__":
    unittest.main()
