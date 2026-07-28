#!/usr/bin/env python3
"""Start the local Claude SEO workbench and open it in a browser."""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from ui import server  # noqa: E402


def fetch_runtime(url: str):
    try:
        with urllib.request.urlopen(f"{url}/api/runtime", timeout=2) as response:
            if response.status == 200:
                return json.load(response)
    except (OSError, ValueError, urllib.error.URLError):
        pass
    return None


def existing_workbench(url: str) -> bool:
    return fetch_runtime(url) is not None


def service_paths(port: int):
    directory = Path.home() / ".cache" / "claude-seo"
    return directory, directory / f"workbench-{port}.pid", directory / f"workbench-{port}.log"


def read_pid(pid_path: Path):
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
        return pid if pid > 0 else None
    except (OSError, ValueError):
        return None


def start_background(port: int, open_browser: bool) -> int:
    url = f"http://localhost:{port}"
    if existing_workbench(url):
        print(f"工作台已经在运行：{url}")
        if open_browser:
            webbrowser.open(url)
        return 0

    directory, _, log_path = service_paths(port)
    directory.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--foreground",
        "--no-browser",
        "--port",
        str(port),
    ]
    popen_options = {
        "cwd": PROJECT_ROOT,
        "stdin": subprocess.DEVNULL,
        "start_new_session": os.name != "nt",
    }
    if os.name == "nt":
        popen_options["creationflags"] = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        )
    with log_path.open("a", encoding="utf-8") as log_file:
        subprocess.Popen(
            command,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            **popen_options,
        )

    for _ in range(50):
        if existing_workbench(url):
            print(f"Claude SEO 本地工作台已在后台启动：{url}")
            print(f"运行日志：{log_path}")
            if open_browser:
                webbrowser.open(url)
            return 0
        time.sleep(0.1)
    print(f"后台启动失败，请查看日志：{log_path}", file=sys.stderr)
    return 1


def stop_background(port: int) -> int:
    url = f"http://localhost:{port}"
    runtime = fetch_runtime(url)
    _, pid_path, _ = service_paths(port)
    pid = read_pid(pid_path)
    if runtime is None:
        pid_path.unlink(missing_ok=True)
        print("工作台当前没有运行。")
        return 0
    if Path(runtime.get("workspace", "")).resolve() != PROJECT_ROOT:
        print(f"端口 {port} 上运行的不是当前项目，拒绝停止。", file=sys.stderr)
        return 1
    if pid is None:
        print("找不到工作台进程记录，无法安全停止。", file=sys.stderr)
        return 1
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pid_path.unlink(missing_ok=True)
        print("工作台已经停止。")
        return 0
    except OSError as error:
        print(f"停止工作台失败：{error}", file=sys.stderr)
        return 1
    for _ in range(30):
        if not existing_workbench(url):
            pid_path.unlink(missing_ok=True)
            print("工作台已停止。")
            return 0
        time.sleep(0.1)
    print("停止请求已发送，但服务仍在响应。", file=sys.stderr)
    return 1


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

    directory, pid_path, _ = service_paths(port)
    directory.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()), encoding="utf-8")
    print("Claude SEO 本地工作台已启动", flush=True)
    print(f"访问地址：{url}", flush=True)
    print("SEO/文件任务使用 Codex；文章创作使用 Claude。", flush=True)
    print("按 Ctrl+C 停止。", flush=True)
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
        if read_pid(pid_path) == os.getpid():
            pid_path.unlink(missing_ok=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="启动 Claude SEO 本地工作台")
    parser.add_argument("--port", type=int, default=7777)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--check", action="store_true", help="只检查 Codex、Claude 和技能状态")
    parser.add_argument("--foreground", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--status", action="store_true", help="检查本地服务是否正在运行")
    parser.add_argument("--stop", action="store_true", help="停止后台工作台")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("端口必须在 1 到 65535 之间")
    if args.check:
        return print_check()
    if args.status:
        url = f"http://localhost:{args.port}"
        if existing_workbench(url):
            print(f"工作台正在运行：{url}")
            return 0
        print("工作台没有运行。")
        return 1
    if args.stop:
        return stop_background(args.port)
    if args.foreground:
        return serve(args.port, not args.no_browser)
    return start_background(args.port, not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
