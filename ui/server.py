#!/usr/bin/env python3
"""claude-seo 本地 AI 工作台。

提供静态网页、技能信息 API，以及一个将浏览器请求桥接到本机 Codex CLI
的 NDJSON 流式接口。服务仅监听 127.0.0.1，不向局域网或公网暴露。

用法:
    python3 ui/server.py [port]     # 默认 7777
"""
import json
import os
import re
import sqlite3
import sys
import threading
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

from workbench.config import load_config
from workbench.errors import ErrorCode, error_payload
from workbench.protocol import EventStream
from workbench.runtime import ClaudeCliRuntime, CodexCliRuntime, RuntimeRequest
from workbench.sessions import SessionManager
from workbench.tasks import (
    TaskCapacityError,
    TaskManager,
    TaskNotCancellableError,
    TaskNotFoundError,
)


CONFIG = load_config(Path(__file__))
HOME = CONFIG.home
PROJECT_DIR = CONFIG.project_dir
SKILLS_DIR = CONFIG.skills_dir
AGENTS_DIR = CONFIG.agents_dir
DRIFT_DB = CONFIG.drift_db
CODEX_BIN = CONFIG.codex_bin
CODEX_MODEL = CONFIG.codex_model
CLAUDE_BIN = CONFIG.claude_bin
CLAUDE_MODEL = CONFIG.claude_model
MAX_SANDBOX = CONFIG.max_sandbox
MAX_REQUEST_BYTES = CONFIG.max_request_bytes
MAX_MESSAGE_CHARS = CONFIG.max_message_chars
MAX_CONCURRENT_TASKS = CONFIG.max_concurrent_tasks
TASK_TIMEOUT_SECONDS = CONFIG.task_timeout_seconds
MAX_CONCURRENT_TASKS_LIMIT = 4
RUNTIME = CodexCliRuntime(CODEX_BIN, CODEX_MODEL, PROJECT_DIR)
CLAUDE_RUNTIME = ClaudeCliRuntime(CLAUDE_BIN, CLAUDE_MODEL, PROJECT_DIR)
TASKS = TaskManager(max_active=MAX_CONCURRENT_TASKS)
SESSIONS = SessionManager()
LOCAL_HOST_PATTERN = re.compile(r"\A(?:127\.0\.0\.1|localhost)(?::\d{1,5})?\Z", re.IGNORECASE)
TASK_CANCEL_PATTERN = re.compile(r"\A/api/tasks/(task_[0-9a-f]{32})/cancel\Z")
SESSION_ID_PATTERN = re.compile(r"\Asession_[0-9a-f]{32}\Z")
TASK_TYPES = {"general": "codex", "article": "claude"}

CATEGORIES = {
    "编排": ["seo"],
    "分析审计": ["seo-audit", "seo-page", "seo-technical", "seo-content",
                 "seo-schema", "seo-sitemap", "seo-images", "seo-geo",
                 "seo-sxo", "seo-hreflang"],
    "策略规划": ["seo-plan", "seo-programmatic", "seo-competitor-pages",
                 "seo-content-brief", "seo-cluster", "seo-flow"],
    "本地与地图": ["seo-local", "seo-maps"],
    "电商": ["seo-ecommerce"],
    "监控": ["seo-drift"],
    "数据源扩展": ["seo-google", "seo-backlinks", "seo-dataforseo",
                   "seo-ahrefs", "seo-bing", "seo-firecrawl", "seo-profound",
                   "seo-seranking", "seo-unlighthouse", "seo-image-gen"],
}
CATEGORY_OF = {name: cat for cat, names in CATEGORIES.items() for name in names}


def parse_frontmatter(path):
    """解析 SKILL.md / agent md 的 YAML frontmatter（宽松实现）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    frontmatter, result, current_key = match.group(1), {}, None
    for line in frontmatter.splitlines():
        key_match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if key_match:
            current_key, value = key_match.group(1), key_match.group(2).strip()
            if value in (">", "|", ">-", "|-"):
                value = ""
            result[current_key] = value.strip('"').strip("'")
        elif current_key and line.startswith((" ", "\t")):
            result[current_key] = (result[current_key] + " " + line.strip()).strip()
    return result


def count_resources(skill_dir):
    total = 0
    for _, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in (".venv", "__pycache__", "node_modules")]
        total += len(files)
    return total


def api_skills():
    skills = []
    if SKILLS_DIR.is_dir():
        for directory in sorted(SKILLS_DIR.iterdir()):
            if not directory.is_dir() or not (directory.name == "seo" or directory.name.startswith("seo-")):
                continue
            frontmatter = parse_frontmatter(directory / "SKILL.md")
            skills.append({
                "name": directory.name,
                "description": frontmatter.get("description", ""),
                "version": frontmatter.get("version", ""),
                "argument_hint": frontmatter.get("argument-hint", ""),
                "user_invocable": frontmatter.get("user-invocable", "") == "true",
                "category": CATEGORY_OF.get(directory.name, "其他"),
                "resources": count_resources(directory),
            })
    return {"skills": skills, "categories": list(CATEGORIES.keys())}


def api_agents():
    agents = []
    if AGENTS_DIR.is_dir():
        for path in sorted(AGENTS_DIR.glob("seo-*.md")):
            frontmatter = parse_frontmatter(path)
            agents.append({
                "name": frontmatter.get("name", path.stem),
                "description": frontmatter.get("description", ""),
                "tools": [t.strip() for t in frontmatter.get("tools", "").split(",") if t.strip()],
                "model": frontmatter.get("model", ""),
            })
    return {"agents": agents}


def api_overview():
    skills = api_skills()["skills"]
    venv = SKILLS_DIR / "seo" / ".venv"
    package_count = 0
    site = venv / "lib"
    if site.is_dir():
        for site_packages in site.glob("python*/site-packages"):
            package_count = len(list(site_packages.glob("*.dist-info")))
    scripts_dir = SKILLS_DIR / "seo" / "scripts"
    return {
        "skill_count": len(skills),
        "agent_count": len(list(AGENTS_DIR.glob("seo-*.md"))) if AGENTS_DIR.is_dir() else 0,
        "script_count": len(list(scripts_dir.glob("*.py"))) if scripts_dir.is_dir() else 0,
        "package_count": package_count,
        "venv_ok": (venv / "bin" / "python").exists(),
        "drift_db": DRIFT_DB.exists(),
    }


def api_drift():
    if not DRIFT_DB.exists():
        return {"available": False, "baselines": []}
    try:
        connection = sqlite3.connect(f"file:{DRIFT_DB}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        rows = []
        if "baselines" in tables:
            rows = [dict(row) for row in connection.execute(
                "SELECT * FROM baselines ORDER BY rowid DESC LIMIT 50")]
        connection.close()
        return {"available": True, "tables": tables, "baselines": rows}
    except sqlite3.Error as error:
        return {"available": False, "error": str(error), "baselines": []}


def api_runtime():
    codex_status = RUNTIME.status()
    claude_status = CLAUDE_RUNTIME.status()
    return {
        "codex_available": codex_status.available,
        "codex_version": codex_status.version,
        "logged_in": codex_status.authenticated,
        "login_status": codex_status.authentication_status,
        "model": codex_status.model,
        "claude_available": claude_status.available,
        "claude_version": claude_status.version,
        "claude_logged_in": claude_status.authenticated,
        "claude_login_status": claude_status.authentication_status,
        "claude_model": claude_status.model,
        "routing": {
            "general": "codex",
            "article": "claude",
        },
        "workspace": str(PROJECT_DIR),
        "max_sandbox": MAX_SANDBOX,
        "max_concurrent_tasks": TASKS.get_max_active(),
        "max_concurrent_tasks_limit": MAX_CONCURRENT_TASKS_LIMIT,
        "task_timeout_seconds": TASK_TIMEOUT_SECONDS,
    }


ROUTES = {
    "/api/skills": api_skills,
    "/api/agents": api_agents,
    "/api/overview": api_overview,
    "/api/drift": api_drift,
    "/api/runtime": api_runtime,
}


def build_prompt(message, skill, is_new_thread, task_type="general"):
    if not is_new_thread:
        return message
    if task_type == "article":
        guidance = (
            "你是本地 Claude SEO 工作台的文章创作引擎。请真正完成用户要求的文章，"
            "不要把任务转交给 Codex，也不要只给写作建议或提纲。"
            "根据需要读取项目中的 CLAUDE.md、skills/seo/SKILL.md 和相关内容技能。"
            "优先输出可直接交付的完整 Markdown 正文；如果用户明确要求保存文件且当前权限允许，"
            "再写入用户指定的位置。不要读取或输出任何登录凭据。"
        )
    else:
        guidance = (
            "你正在 claude-seo 项目根目录中工作。请把用户的自然语言目标当作需要真正完成的任务，"
            "不要只介绍技能菜单。根据任务自主读取项目中的 AGENTS.md、skills/seo/SKILL.md 和相关技能文件，"
            "使用适用的脚本与工具；若用户要求修改文件，请先检查目标并只修改任务范围内的内容。"
        )
    if skill:
        guidance += f" 用户选择了 {skill}，请优先读取 skills/{skill}/SKILL.md 并遵循其中的工作流。"
    return f"{guidance}\n\n用户任务：\n{message}"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.request_id = f"req_{uuid.uuid4().hex}"
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def end_headers(self):
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; "
            "form-action 'none'; frame-ancestors 'none'",
        )
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Request-ID", self.request_id)
        super().end_headers()

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_api_error(self, status, code, message, *, retryable=False, details=None):
        self.send_json(
            status,
            error_payload(
                code,
                message,
                self.request_id,
                retryable=retryable,
                details=details,
            ),
        )

    def has_allowed_host(self):
        host = self.headers.get("Host", "").strip()
        return bool(LOCAL_HOST_PATTERN.fullmatch(host))

    def has_allowed_origin(self):
        origin = self.headers.get("Origin")
        if origin is None:
            return True
        host = self.headers.get("Host", "").strip()
        return origin.lower() == f"http://{host}".lower()

    def do_GET(self):
        if not self.has_allowed_host():
            self.send_api_error(403, ErrorCode.HOST_DENIED, "拒绝非本机请求")
            return
        route = self.path.split("?")[0]
        if route in ROUTES:
            self.send_json(200, ROUTES[route]())
        else:
            super().do_GET()

    def do_POST(self):
        if not self.has_allowed_host():
            self.send_api_error(403, ErrorCode.HOST_DENIED, "拒绝非本机请求")
            return
        route = self.path.split("?")[0]
        cancel_match = TASK_CANCEL_PATTERN.fullmatch(route)
        if (
            route not in (
                "/api/chat",
                "/api/v1/chat",
                "/api/settings/runtime",
            )
            and cancel_match is None
        ):
            self.send_api_error(404, ErrorCode.ROUTE_NOT_FOUND, "未找到接口")
            return
        media_type = self.headers.get("Content-Type", "").partition(";")[0].strip().lower()
        if media_type != "application/json":
            self.send_api_error(
                415,
                ErrorCode.UNSUPPORTED_MEDIA_TYPE,
                "仅支持 application/json",
            )
            return
        if not self.has_allowed_origin():
            self.send_api_error(403, ErrorCode.ORIGIN_DENIED, "拒绝跨站请求")
            return
        if cancel_match is not None:
            self.handle_cancel(cancel_match.group(1))
        elif route == "/api/settings/runtime":
            self.handle_runtime_settings()
        else:
            self.handle_chat(versioned=route == "/api/v1/chat")

    def read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self.send_api_error(400, ErrorCode.INVALID_SIZE, "请求大小不正确")
            return None
        try:
            return json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_api_error(400, ErrorCode.INVALID_JSON, "请求不是有效 JSON")
            return None

    def handle_runtime_settings(self):
        payload = self.read_json_body()
        if payload is None:
            return
        max_concurrent_tasks = payload.get("max_concurrent_tasks")
        if (
            not isinstance(max_concurrent_tasks, int)
            or isinstance(max_concurrent_tasks, bool)
            or max_concurrent_tasks < 1
            or max_concurrent_tasks > MAX_CONCURRENT_TASKS_LIMIT
        ):
            self.send_api_error(
                400,
                ErrorCode.INVALID_FIELD,
                "并发任务数必须是 1 到 4 的整数",
            )
            return
        TASKS.set_max_active(max_concurrent_tasks)
        self.send_json(
            200,
            {
                "settings": {
                    "max_concurrent_tasks": TASKS.get_max_active(),
                    "max_concurrent_tasks_limit": MAX_CONCURRENT_TASKS_LIMIT,
                }
            },
        )

    def handle_cancel(self, task_id):
        try:
            task = TASKS.cancel(task_id)
        except TaskNotFoundError:
            self.send_api_error(404, ErrorCode.TASK_NOT_FOUND, "任务不存在")
            return
        except TaskNotCancellableError:
            self.send_api_error(
                409,
                ErrorCode.TASK_NOT_CANCELLABLE,
                "任务已经结束，无法取消",
            )
            return
        self.send_json(200, {"task": task})

    def handle_chat(self, versioned=False):
        payload = self.read_json_body()
        if payload is None:
            return

        message = str(payload.get("message", "")).strip()
        thread_id = str(payload.get("thread_id", "")).strip()
        session_id = str(payload.get("session_id", "")).strip()
        skill = str(payload.get("skill", "")).strip()
        sandbox = str(payload.get("sandbox", "read-only"))
        task_type = str(payload.get("task_type", "general")).strip()
        if not message or len(message) > MAX_MESSAGE_CHARS:
            self.send_api_error(400, ErrorCode.INVALID_FIELD, "请输入有效任务内容")
            return
        if versioned and thread_id:
            self.send_api_error(
                400,
                ErrorCode.INVALID_FIELD,
                "v1 接口不接受 Runtime 会话 ID",
            )
            return
        if not versioned and thread_id and not re.fullmatch(r"[A-Za-z0-9_-]{1,160}", thread_id):
            self.send_api_error(400, ErrorCode.INVALID_FIELD, "会话 ID 不正确")
            return
        if versioned and session_id and not SESSION_ID_PATTERN.fullmatch(session_id):
            self.send_api_error(400, ErrorCode.INVALID_FIELD, "应用会话 ID 不正确")
            return
        if sandbox not in ("read-only", "workspace-write"):
            self.send_api_error(400, ErrorCode.INVALID_FIELD, "不支持的权限模式")
            return
        if task_type not in TASK_TYPES:
            self.send_api_error(400, ErrorCode.INVALID_FIELD, "不支持的任务类型")
            return
        if sandbox == "workspace-write" and MAX_SANDBOX != "workspace-write":
            self.send_api_error(403, ErrorCode.MODE_DENIED, "服务当前仅允许只读任务")
            return
        if skill:
            skill_path = PROJECT_DIR / "skills" / skill / "SKILL.md"
            if not re.fullmatch(r"seo(?:-[a-z0-9-]+)?", skill) or not skill_path.is_file():
                self.send_api_error(400, ErrorCode.SKILL_NOT_FOUND, "选择的技能不存在")
                return
        runtime_name = TASK_TYPES[task_type]
        runtime = CLAUDE_RUNTIME if runtime_name == "claude" else RUNTIME
        app_session = (
            SESSIONS.get_or_create(session_id, runtime_name)
            if versioned
            else None
        )
        runtime_thread_id = (
            app_session.runtime_thread_id if app_session is not None else thread_id
        )
        try:
            task = TASKS.create()
        except TaskCapacityError:
            self.send_api_error(
                429,
                ErrorCode.TASK_CAPACITY,
                "当前任务过多，请稍后重试",
                retryable=True,
            )
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("X-Task-ID", task.task_id)
        self.send_header("X-AI-Runtime", runtime_name)
        if versioned:
            self.send_header("X-Protocol-Version", "1")
            self.send_header("X-Session-ID", app_session.session_id)
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

        runtime_session = None
        timeout_timer = None
        protocol_stream = EventStream(task.task_id) if versioned else None

        def emit(event):
            data = (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")
            self.wfile.write(data)
            self.wfile.flush()

        def emit_v1(event_type, data=None):
            emit(protocol_stream.event(event_type, data))

        try:
            if versioned:
                emit_v1(
                    "session.bound",
                    {
                        "session_id": app_session.session_id,
                        "runtime_bound": bool(runtime_thread_id),
                    },
                )
                emit_v1(
                    "task.started",
                    {
                        "session_id": app_session.session_id,
                        "sandbox": sandbox,
                        "runtime": runtime_name,
                        "task_type": task_type,
                    },
                )
            else:
                emit({"type": "task", "task_id": task.task_id})
            runtime_session = runtime.start(
                RuntimeRequest(
                    prompt=build_prompt(
                        message,
                        skill,
                        not runtime_thread_id,
                        task_type,
                    ),
                    thread_id=runtime_thread_id,
                    sandbox=sandbox,
                )
            )
            TASKS.bind_session(task.task_id, runtime_session)

            def request_timeout():
                try:
                    TASKS.request_timeout(task.task_id)
                except (TaskNotFoundError, TaskNotCancellableError):
                    pass

            timeout_timer = threading.Timer(TASK_TIMEOUT_SECONDS, request_timeout)
            timeout_timer.daemon = True
            timeout_timer.start()

            emitted_error = False
            failure_message = ""
            usage = {}
            for runtime_event in runtime_session.events():
                if versioned:
                    if runtime_event.type == "thread":
                        runtime_id = runtime_event.data.get("thread_id", "")
                        if runtime_id:
                            SESSIONS.bind_runtime_thread(
                                app_session.session_id,
                                runtime_id,
                            )
                    elif runtime_event.type == "status":
                        emit_v1("task.status", runtime_event.data)
                    elif runtime_event.type == "activity":
                        emit_v1("task.activity", runtime_event.data)
                    elif runtime_event.type == "assistant":
                        emit_v1("assistant.message", runtime_event.data)
                    elif runtime_event.type == "warning":
                        emit_v1("task.warning", runtime_event.data)
                    elif runtime_event.type == "error":
                        failure_message = runtime_event.data.get(
                            "message",
                            "任务执行失败",
                        )
                    elif runtime_event.type == "completed":
                        usage = runtime_event.data.get("usage", {})
                    continue
                client_event = runtime_event.legacy_payload()
                if client_event["type"] == "error":
                    emitted_error = True
                emit(client_event)

            return_code = runtime_session.wait()
            if TASKS.is_timeout_requested(task.task_id):
                TASKS.finish(task.task_id, "timed_out")
                message = f"任务运行超过 {TASK_TIMEOUT_SECONDS} 秒，已自动停止"
                if versioned:
                    emit_v1(
                        "task.failed",
                        {"code": ErrorCode.TASK_TIMEOUT, "message": message},
                    )
                else:
                    emit({"type": "error", "message": message})
            elif TASKS.is_cancel_requested(task.task_id):
                TASKS.finish(task.task_id, "cancelled")
                if versioned:
                    emit_v1("task.cancelled", {"reason": "user_requested"})
                else:
                    emit({"type": "cancelled", "task_id": task.task_id})
            elif return_code != 0 and not emitted_error:
                detail = runtime_session.stderr_tail()
                TASKS.finish(task.task_id, "failed")
                runtime_label = "Claude" if runtime_name == "claude" else "Codex"
                message = detail or f"{runtime_label} 退出，状态码 {return_code}"
                if versioned:
                    emit_v1(
                        "task.failed",
                        {"code": "runtime.process_failed", "message": message},
                    )
                else:
                    emit({"type": "error", "message": message})
            elif versioned and failure_message:
                TASKS.finish(task.task_id, "failed")
                emit_v1(
                    "task.failed",
                    {"code": "runtime.task_failed", "message": failure_message},
                )
            elif emitted_error:
                TASKS.finish(task.task_id, "failed")
            else:
                TASKS.finish(task.task_id, "completed")
                if versioned:
                    emit_v1("task.completed", {"usage": usage})
        except BrokenPipeError:
            if runtime_session:
                runtime_session.terminate()
            TASKS.finish(task.task_id, "cancelled")
        except OSError as error:
            TASKS.finish(task.task_id, "failed")
            try:
                if versioned:
                    emit_v1(
                        "task.failed",
                        {
                            "code": "runtime.unavailable",
                            "message": (
                                f"无法启动 {'Claude' if runtime_name == 'claude' else 'Codex'}：{error}"
                            ),
                        },
                    )
                else:
                    runtime_label = "Claude" if runtime_name == "claude" else "Codex"
                    emit({"type": "error", "message": f"无法启动 {runtime_label}：{error}"})
            except BrokenPipeError:
                pass
        finally:
            if timeout_timer:
                timeout_timer.cancel()
            if runtime_session:
                runtime_session.terminate()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7777
    print(f"claude-seo AI 工作台: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
