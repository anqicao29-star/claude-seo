"""Claude Code CLI adapter for article-writing tasks."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .base import RuntimeAdapter, RuntimeEvent, RuntimeRequest, RuntimeSession, RuntimeStatus


def _text_blocks(message: Dict[str, Any]) -> str:
    content = message.get("content") or []
    return "\n".join(
        str(block.get("text", ""))
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ).strip()


def normalize_claude_event(event: Dict[str, Any]) -> List[RuntimeEvent]:
    """Convert Claude stream-json messages to runtime-neutral events."""
    event_type = event.get("type", "")
    if event_type == "system" and event.get("subtype") == "init":
        session_id = str(event.get("session_id", ""))
        events = []
        if session_id:
            events.append(RuntimeEvent("thread", {"thread_id": session_id}))
        events.append(RuntimeEvent("status", {"text": "Claude 已开始创作文章"}))
        return events
    if event_type == "assistant":
        message = event.get("message") or {}
        events = []
        text = _text_blocks(message)
        if text:
            events.append(RuntimeEvent("assistant", {"text": text}))
        for block in message.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            events.append(
                RuntimeEvent(
                    "activity",
                    {
                        "kind": "tool",
                        "text": str(block.get("name") or "Claude 工具"),
                        "status": "in_progress",
                    },
                )
            )
        return events
    if event_type == "result":
        if event.get("is_error") or event.get("subtype") not in ("success", None):
            return [
                RuntimeEvent(
                    "error",
                    {"message": str(event.get("result") or "Claude 文章任务执行失败")},
                )
            ]
        return [RuntimeEvent("completed", {"usage": event.get("usage") or {}})]
    return []


class ClaudeCliSession(RuntimeSession):
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
            yield from normalize_claude_event(raw_event)

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


class ClaudeCliRuntime(RuntimeAdapter):
    def __init__(self, executable: str, model: str, workspace: Path):
        self.executable = executable
        self.model = model
        self.workspace = workspace

    def command(self, request: RuntimeRequest) -> List[str]:
        permission_args = (
            ["--permission-mode", "plan", "--allowedTools", "Read,Glob,Grep,WebFetch,WebSearch"]
            if request.sandbox == "read-only"
            else ["--permission-mode", "acceptEdits"]
        )
        command = [
            self.executable,
            "--print",
            "--output-format",
            "stream-json",
            "--verbose",
            "--model",
            self.model,
            *permission_args,
        ]
        if request.thread_id:
            command.extend(["--resume", request.thread_id])
        return command

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
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except (OSError, subprocess.TimeoutExpired) as error:
            return 1, "", str(error)

    def status(self) -> RuntimeStatus:
        version_code, version, version_error = self._command_output(
            [self.executable, "--version"]
        )
        auth_code, auth_output, auth_error = self._command_output(
            [self.executable, "auth", "status", "--json"]
        )
        authenticated = False
        auth_status = auth_output or auth_error or "未登录"
        if auth_code == 0 and auth_output:
            try:
                auth_data = json.loads(auth_output)
                authenticated = bool(auth_data.get("loggedIn"))
                auth_status = "已登录" if authenticated else "未登录"
            except json.JSONDecodeError:
                authenticated = "logged" in auth_output.lower()
        return RuntimeStatus(
            available=version_code == 0,
            version=(version or version_error or "未检测到").splitlines()[-1],
            authenticated=authenticated,
            authentication_status=auth_status.splitlines()[-1],
            model=self.model,
        )

    def start(self, request: RuntimeRequest) -> RuntimeSession:
        process = subprocess.Popen(
            self.command(request),
            cwd=self.workspace,
            env=os.environ.copy(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
        try:
            return ClaudeCliSession(process, request.prompt)
        except Exception:
            if process.poll() is None:
                process.terminate()
            raise
