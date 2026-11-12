"""Tests for isolated workbench writes, Diff confirmation and undo."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.write_previews import (  # noqa: E402
    PreviewConflictError,
    PreviewStateError,
    WritePreviewManager,
)


class WritePreviewManagerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.cache = self.root / "cache"
        self.workspace.mkdir()
        (self.workspace / "article.md").write_text("# Old\n", encoding="utf-8")
        (self.workspace / "remove.txt").write_text("remove me\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        subprocess.run(
            ["git", "add", "article.md", "remove.txt"],
            cwd=self.workspace,
            check=True,
        )
        self.manager = WritePreviewManager(self.cache)

    def tearDown(self):
        self.temporary.cleanup()

    def create_changed_preview(self):
        preview = self.manager.create("task_test", self.workspace)
        stage = self.manager.workspace(preview["preview_id"])
        (stage / "article.md").write_text("# New\n\nUpdated.\n", encoding="utf-8")
        (stage / "remove.txt").unlink()
        (stage / "added.md").write_text("new file\n", encoding="utf-8")
        return preview, self.manager.capture(preview["preview_id"])

    def test_preview_does_not_touch_original_until_apply_and_supports_undo(self):
        preview, captured = self.create_changed_preview()

        self.assertEqual(captured["status"], "pending")
        self.assertEqual(
            {item["kind"] for item in captured["files"]},
            {"added", "modified", "deleted"},
        )
        self.assertIn("--- a/article.md", captured["diff"])
        self.assertEqual((self.workspace / "article.md").read_text(), "# Old\n")
        self.assertTrue((self.workspace / "remove.txt").exists())
        self.assertFalse((self.workspace / "added.md").exists())

        applied = self.manager.apply(preview["preview_id"])
        self.assertEqual(applied["status"], "applied")
        self.assertEqual((self.workspace / "article.md").read_text(), "# New\n\nUpdated.\n")
        self.assertFalse((self.workspace / "remove.txt").exists())
        self.assertEqual((self.workspace / "added.md").read_text(), "new file\n")

        undone = self.manager.undo(preview["preview_id"])
        self.assertEqual(undone["status"], "undone")
        self.assertEqual((self.workspace / "article.md").read_text(), "# Old\n")
        self.assertEqual((self.workspace / "remove.txt").read_text(), "remove me\n")
        self.assertFalse((self.workspace / "added.md").exists())

    def test_apply_refuses_to_overwrite_concurrent_changes(self):
        preview, captured = self.create_changed_preview()
        self.assertEqual(captured["status"], "pending")
        (self.workspace / "article.md").write_text("changed elsewhere\n", encoding="utf-8")

        with self.assertRaises(PreviewConflictError):
            self.manager.apply(preview["preview_id"])

        self.assertEqual(
            (self.workspace / "article.md").read_text(),
            "changed elsewhere\n",
        )

    def test_sensitive_and_symlink_changes_are_blocked(self):
        preview = self.manager.create("task_test", self.workspace)
        stage = self.manager.workspace(preview["preview_id"])
        (stage / ".env").write_text("SECRET=value\n", encoding="utf-8")
        (stage / "outside-link").symlink_to(self.root / "outside")

        captured = self.manager.capture(preview["preview_id"])

        self.assertEqual(captured["status"], "blocked")
        self.assertTrue(any("敏感路径" in item for item in captured["blocked"]))
        self.assertTrue(any("符号链接" in item for item in captured["blocked"]))
        with self.assertRaises(PreviewStateError):
            self.manager.apply(preview["preview_id"])

    def test_discard_leaves_original_untouched(self):
        preview, captured = self.create_changed_preview()
        self.assertEqual(captured["status"], "pending")

        discarded = self.manager.discard(preview["preview_id"])

        self.assertEqual(discarded["status"], "discarded")
        self.assertEqual((self.workspace / "article.md").read_text(), "# Old\n")
        with self.assertRaises(PreviewStateError):
            self.manager.apply(preview["preview_id"])

    def test_pending_preview_survives_manager_restart(self):
        preview, captured = self.create_changed_preview()
        self.assertEqual(captured["status"], "pending")

        restarted_manager = WritePreviewManager(self.cache)
        recovered = restarted_manager.get(preview["preview_id"])
        self.assertEqual(recovered["status"], "pending")

        restarted_manager.apply(preview["preview_id"])
        self.assertEqual((self.workspace / "article.md").read_text(), "# New\n\nUpdated.\n")
        restarted_manager.undo(preview["preview_id"])
        self.assertEqual((self.workspace / "article.md").read_text(), "# Old\n")


if __name__ == "__main__":
    unittest.main()
