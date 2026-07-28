#!/usr/bin/env python3
"""Start the local Claude SEO workbench and open it in a browser."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from ui import server  # noqa: E402


def existing_workbench(url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/api/runtime", timeout=2) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def print_check() -> int:
    runtime = server.api_runtime()
    result = {
        "ready": bool(
            runtime["codex_available"]
            and runtime["logged_in"]
            and runtime["claude_available"]
            and runtime["claude_logged_in"]
        ),
        "codex": {
            "installed": runtime["codex_available"],
            "logged_in": runtime["logged_in"],
            "version": runtime["codex_version"],
        },
        "claude": {
            "installed": runtime["claude_available"],
            "logged_in": runtime["claude_logged_in"],
            "version": runtime["claude_version"],
        },
        "skills": len(server.api_skills()["skills"]),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not runtime["codex_available"]:
        print("\n缺少 Codex CLI。安装后运行：codex login")
    elif not runtime["logged_in"]:
        print("\nCodex 尚未登录。请运行：codex login")
    if not runtime["claude_available"]:
        print("\n缺少 Claude Code。安装后运行：claude auth login")
    elif not runtime["claude_logged_in"]:
        print("\nClaude 尚未登录。请运行：claude auth login")
    return 0 if result["ready"] else 1


def serve(port: int, open_browser: bool) -> int:
    url = f"http://localhost:{port}"
    if existing_workbench(url):
        print(f"工作台已经在运行：{url}")
        if open_browser:
            webbrowser.open(url)
        return 0

    try:
        httpd = server.ThreadingHTTPServer(("127.0.0.1", port), server.Handler)
    except OSError as error:
        if isinstance(error, socket.error):
            print(f"无法使用端口 {port}：{error}", file=sys.stderr)
        else:
            print(f"无法启动工作台：{error}", file=sys.stderr)
        return 1

    print("Claude SEO 本地工作台已启动")
    print(f"访问地址：{url}")
    print("SEO/文件任务使用 Codex；文章创作使用 Claude。")
    print("保持此窗口打开；按 Ctrl+C 停止。")
    if open_browser:
        timer = threading.Timer(0.5, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n工作台已停止。")
    finally:
        httpd.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="启动 Claude SEO 本地工作台")
    parser.add_argument("--port", type=int, default=7777)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--check", action="store_true", help="只检查 Codex、Claude 和技能状态")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("端口必须在 1 到 65535 之间")
    if args.check:
        return print_check()
    return serve(args.port, not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
