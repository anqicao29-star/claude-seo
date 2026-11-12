"""Static integration checks for write-preview controls in the workbench UI."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "ui" / "index.html"


class WorkbenchWriteUiTests(unittest.TestCase):
    def test_ui_exposes_diff_confirmation_apply_discard_and_undo(self):
        html = INDEX.read_text(encoding="utf-8")

        self.assertIn("允许修改（先预览 Diff）", html)
        self.assertIn("原项目尚未修改；确认后才会写入", html)
        self.assertIn("确认应用修改", html)
        self.assertIn("放弃修改", html)
        self.assertIn("撤销本次修改", html)
        self.assertIn('"write.preview": "write_preview"', html)
        self.assertIn("/api/write-previews/", html)


if __name__ == "__main__":
    unittest.main()
