"""Codex CLI adapter for the local workbench."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .base import RuntimeAdapter, RuntimeEvent, RuntimeRequest, RuntimeSession, RuntimeStatus


def normalize_codex_event(event: Dict[str, Any]) -> Optional[RuntimeEvent]:
    """Convert Codex-specific JSON events to runtime-neutral events."""
    event_type = event.get("type", "")
    if event_type == "thread.started":
        return RuntimeEvent("thread", {"thread_id": event.get("thread_id", "")})
    if event_type == "turn.started":
        return RuntimeEvent("status", {"text": "Codex 已开始处理任务"})
    if event_type == "turn.completed":
        return RuntimeEvent("completed", {"usage": event.get("usage", {})})
    if event_type == "turn.failed":
        error = event.get("error") or {}
        return RuntimeEvent("error", {"message": error.get("message", "任务执行失败")})
    if event_type == "error":
        return RuntimeEvent("error", {"message": event.get("message", "Codex 返回错误")})
    if event_type not in ("item.started", "item.updated", "item.completed"):
        return None

    item = event.get("item") or {}
    item_type = item.get("type", "")
    if item_type == "agent_message" and event_type == "item.completed":
        return RuntimeEvent("assistant", {"text": item.get("text", "")})
    if item_type == "command_execution":
        command = item.get("command") or "正在执行命令"
        status = item.get("status") or event_type.removeprefix("item.")
        return RuntimeEvent(
            "activity",
            {"kind": "command", "text": command, "status": status},
        )
    if item_type in ("file_change", "file_changes"):
        return RuntimeEvent(
            "activity",
            {
                "kind": "file",
                "text": "正在处理项目文件",
                "status": item.get("status", ""),
            },
        )
    if item_type == "mcp_tool_call":
        name = item.get("tool") or item.get("name") or "MCP 工具"
        return RuntimeEvent(
            "activity",
            {"kind": "tool", "text": str(name), "status": item.get("status", "")},
        )
    if item_type == "web_search":
        return RuntimeEvent(
            "activity",
            {
                "kind": "web",
                "text": item.get("query", "正在搜索网页"),
                "status": item.get("status", ""),
            },
        )
    if item_type == "error" and event_type == "item.completed":
        return RuntimeEvent("warning", {"message": item.get("message", "Codex 警告")})
    return None


class CodexCliSession(RuntimeSession):
    def __init__(self, process: subprocess.Popen, prompt: str):
        self.process = process
        self._stderr_lines: List[str] = []
        self._stderr_thread = threading.Thread(target=self._collect_stderr, daemon=True)
        self._stderr_thread.start()
        self.process.stdin.write(prompt)
        self.process.stdin.close()

    def _collect_stderr(self) -> None:
        for line in self.process.stderr:
            self._stderr_lines.append(line.rstrip())
            if len(self._stderr_lines) > 30:
                del self._stderr_lines[0]

    def events(self) -> Iterable[RuntimeEvent]:
        for line in self.process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                raw_event = json.loads(line)
            except json.JSONDecodeError:
                continue
            event = normalize_codex_event(raw_event)
            if event is not None:
                yield event

    def wait(self) -> int:
        return_code = self.process.wait()
        self._stderr_thread.join(timeout=1)
        return return_code

    def stderr_tail(self, limit: int = 5) -> str:
        return "\n".join(self._stderr_lines[-limit:]).strip()

    def terminate(self) -> None:
        if self.process.poll() is not None:
            return
        pid = getattr(self.process, "pid", None)
        if pid is not None and hasattr(os, "killpg") and hasattr(os, "getpgid"):
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                return
            except (OSError, ProcessLookupError):
                pass
        self.process.terminate()


class CodexCliRuntime(RuntimeAdapter):
    def __init__(self, executable: str, model: str, workspace: Path):
        self.executable = executable
        self.model = model
        self.workspace = workspace

    def command(self, request: RuntimeRequest) -> List[str]:
        if request.thread_id:
            return [
                self.executable,
                "exec",
                "resume",
                "--model",
                self.model,
                "--json",
                "--skip-git-repo-check",
                "-c",
                f'sandbox_mode="{request.sandbox}"',
                "-c",
                'approval_policy="never"',
                "-c",
                f'model_reasoning_effort="{request.effort}"',
                request.thread_id,
                "-",
            ]
        return [
            self.executable,
            "exec",
            "--model",
            self.model,
            "--json",
            "--color",
            "never",
            "--sandbox",
            request.sandbox,
            "-c",
            'approval_policy="never"',
            "-c",
            f'model_reasoning_effort="{request.effort}"',
            "--skip-git-repo-check",
            "-",
        ]

    def _command_output(self, args: List[str], timeout: int = 8):
        try:
            result = subprocess.run(
                args,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return result.returncode, (result.stdout + result.stderr).strip()
        except (OSError, subprocess.TimeoutExpired) as error:
            return 1, str(error)

    def status(self) -> RuntimeStatus:
        version_code, version = self._command_output([self.executable, "--version"])
        login_code, login = self._command_output([self.executable, "login", "status"])
        return RuntimeStatus(
            available=version_code == 0,
            version=version.splitlines()[-1] if version else "未检测到",
            authenticated=login_code == 0,
            authentication_status=login.splitlines()[-1] if login else "未登录",
            model=self.model,
        )

    def start(self, request: RuntimeRequest) -> RuntimeSession:
        environment = os.environ.copy()
        environment.setdefault("RUST_LOG", "error")
        process = subprocess.Popen(
            self.command(request),
            cwd=self.workspace,
            env=environment,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
        try:
            return CodexCliSession(process, request.prompt)
        except Exception:
            if process.poll() is None:
                process.terminate()
            raise
