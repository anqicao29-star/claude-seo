"""Tests for the dependency-free Markdown renderer used by the workbench."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_JS = ROOT / "ui" / "markdown.js"
INDEX_HTML = ROOT / "ui" / "index.html"
NODE = shutil.which("node")


def render(markdown: str) -> str:
    script = f"""
const fs = require('fs');
eval(fs.readFileSync({json.dumps(str(MARKDOWN_JS))}, 'utf8'));
process.stdout.write(ClaudeSeoMarkdown.render({json.dumps(markdown)}));
"""
    return subprocess.run(
        [NODE, "-e", script],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


@unittest.skipUnless(NODE, "node is not available")
class MarkdownRendererTests(unittest.TestCase):
    def test_renders_common_markdown_blocks(self) -> None:
        output = render(
            "# 标题\n\n**重点**\n\n- 第一项\n- 第二项\n\n"
            "| 名称 | 状态 |\n| --- | --- |\n| 页面 | 完成 |\n\n"
            "```python\nprint('ok')\n```"
        )

        self.assertIn("<h1>标题</h1>", output)
        self.assertIn("<strong>重点</strong>", output)
        self.assertIn("<ul><li>第一项</li><li>第二项</li></ul>", output)
        self.assertIn("<table>", output)
        self.assertIn("<td>完成</td>", output)
        self.assertIn('<code class="language-python">print(&#39;ok&#39;)</code>', output)


    def test_escapes_html_and_rejects_unsafe_links(self) -> None:
        output = render(
            '<img src=x onerror="alert(1)">\n\n'
            '[危险链接](javascript:alert(1))\n\n'
            '[安全链接](https://example.com/path?a=1&b=2)'
        )

        self.assertNotIn("<img", output)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", output)
        self.assertNotIn('href="javascript:', output)
        self.assertIn('href="https://example.com/path?a=1&amp;b=2"', output)


    def test_workbench_uses_markdown_for_saved_and_streamed_assistant_messages(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('<script src="/markdown.js"></script>', html)
        self.assertIn("ClaudeSeoMarkdown.render(cleanDisplayedText(message.text))", html)
        self.assertIn("ClaudeSeoMarkdown.render(cleanDisplayedText(result.text))", html)


if __name__ == "__main__":
    unittest.main()
