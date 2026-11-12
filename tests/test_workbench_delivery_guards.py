"""Static delivery checks for runtime guidance and launchers."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class WorkbenchDeliveryGuardTests(unittest.TestCase):
    def test_ui_distinguishes_missing_runtime_from_logged_out_runtime(self):
        html = (ROOT / "ui" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Claude 尚未安装。请先安装 Claude Code", html)
        self.assertIn("Claude 尚未登录。请点击页面顶部", html)
        self.assertIn("Codex 尚未安装。请先安装 Codex CLI", html)
        self.assertIn("Codex 尚未登录。请先在终端运行 `codex login`", html)

    def test_launchers_require_python_310_or_newer(self):
        shell = (ROOT / "start-workbench.sh").read_text(encoding="utf-8")
        command = (ROOT / "start-workbench.command").read_text(encoding="utf-8")
        windows = (ROOT / "start-workbench.bat").read_text(encoding="utf-8")

        self.assertIn("sys.version_info >= (3, 10)", shell)
        self.assertIn("./start-workbench.sh", command)
        self.assertIn("sys.version_info ^>= (3, 10)", windows)


if __name__ == "__main__":
    unittest.main()
