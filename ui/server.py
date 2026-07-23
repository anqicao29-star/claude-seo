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
import shutil
import sqlite3
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOME = Path.home()
PROJECT_DIR = Path(__file__).resolve().parent.parent
UI_DIR = Path(__file__).resolve().parent
SKILLS_DIR = HOME / ".claude" / "skills"
AGENTS_DIR = HOME / ".claude" / "agents"
DRIFT_DB = HOME / ".cache" / "claude-seo" / "drift" / "baselines.db"
CODEX_BIN = os.environ.get("CLAUDE_SEO_CODEX_BIN") or shutil.which("codex") or "codex"
# 当前机器已验证 gpt-5.4 可与已安装 CLI 配合工作；可通过环境变量覆盖。
CODEX_MODEL = os.environ.get("CLAUDE_SEO_CODEX_MODEL", "gpt-5.4")
MAX_REQUEST_BYTES = 256 * 1024
MAX_MESSAGE_CHARS = 100_000

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


def command_output(args, timeout=8):
    try:
        result = subprocess.run(
            args, cwd=PROJECT_DIR, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, str(error)


def api_runtime():
    version_code, version = command_output([CODEX_BIN, "--version"])
    login_code, login = command_output([CODEX_BIN, "login", "status"])
    return {
        "codex_available": version_code == 0,
        "codex_version": version.splitlines()[-1] if version else "未检测到",
        "logged_in": login_code == 0,
        "login_status": login.splitlines()[-1] if login else "未登录",
        "model": CODEX_MODEL,
        "workspace": str(PROJECT_DIR),
    }


ROUTES = {
    "/api/skills": api_skills,
    "/api/agents": api_agents,
    "/api/overview": api_overview,
    "/api/drift": api_drift,
    "/api/runtime": api_runtime,
}


def build_prompt(message, skill, is_new_thread):
    if not is_new_thread:
        return message
    guidance = (
        "你正在 claude-seo 项目根目录中工作。请把用户的自然语言目标当作需要真正完成的任务，"
        "不要只介绍技能菜单。根据任务自主读取项目中的 AGENTS.md、skills/seo/SKILL.md 和相关技能文件，"
        "使用适用的脚本与工具；若用户要求修改文件，请先检查目标并只修改任务范围内的内容。"
    )
    if skill:
        guidance += f" 用户选择了 {skill}，请优先读取 skills/{skill}/SKILL.md 并遵循其中的工作流。"
    return f"{guidance}\n\n用户任务：\n{message}"


def normalize_event(event):
    event_type = event.get("type", "")
    if event_type == "thread.started":
        return {"type": "thread", "thread_id": event.get("thread_id", "")}
    if event_type == "turn.started":
        return {"type": "status", "text": "Codex 已开始处理任务"}
    if event_type == "turn.completed":
        return {"type": "completed", "usage": event.get("usage", {})}
    if event_type == "turn.failed":
        error = event.get("error") or {}
        return {"type": "error", "message": error.get("message", "任务执行失败")}
    if event_type == "error":
        return {"type": "error", "message": event.get("message", "Codex 返回错误")}
    if event_type in ("item.started", "item.updated", "item.completed"):
        item = event.get("item") or {}
        item_type = item.get("type", "")
        if item_type == "agent_message" and event_type == "item.completed":
            return {"type": "assistant", "text": item.get("text", "")}
        if item_type == "command_execution":
            command = item.get("command") or "正在执行命令"
            status = item.get("status") or event_type.removeprefix("item.")
            return {"type": "activity", "kind": "command", "text": command, "status": status}
        if item_type in ("file_change", "file_changes"):
            return {"type": "activity", "kind": "file", "text": "正在处理项目文件", "status": item.get("status", "")}
        if item_type == "mcp_tool_call":
            name = item.get("tool") or item.get("name") or "MCP 工具"
            return {"type": "activity", "kind": "tool", "text": str(name), "status": item.get("status", "")}
        if item_type == "web_search":
            return {"type": "activity", "kind": "web", "text": item.get("query", "正在搜索网页"), "status": item.get("status", "")}
        if item_type == "error" and event_type == "item.completed":
            return {"type": "warning", "message": item.get("message", "Codex 警告")}
    return None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = self.path.split("?")[0]
        if route in ROUTES:
            self.send_json(200, ROUTES[route]())
        else:
            super().do_GET()

    def do_POST(self):
        route = self.path.split("?")[0]
        if route != "/api/chat":
            self.send_json(404, {"error": "未找到接口"})
            return
        self.handle_chat()

    def handle_chat(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self.send_json(400, {"error": "请求大小不正确"})
            return
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "请求不是有效 JSON"})
            return

        message = str(payload.get("message", "")).strip()
        thread_id = str(payload.get("thread_id", "")).strip()
        skill = str(payload.get("skill", "")).strip()
        sandbox = str(payload.get("sandbox", "read-only"))
        if not message or len(message) > MAX_MESSAGE_CHARS:
            self.send_json(400, {"error": "请输入有效任务内容"})
            return
        if thread_id and not re.fullmatch(r"[A-Za-z0-9_-]{1,160}", thread_id):
            self.send_json(400, {"error": "会话 ID 不正确"})
            return
        if sandbox not in ("read-only", "workspace-write"):
            self.send_json(400, {"error": "不支持的权限模式"})
            return
        if skill:
            skill_path = PROJECT_DIR / "skills" / skill / "SKILL.md"
            if not re.fullmatch(r"seo(?:-[a-z0-9-]+)?", skill) or not skill_path.is_file():
                self.send_json(400, {"error": "选择的技能不存在"})
                return

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

        process = None

        def emit(event):
            data = (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")
            self.wfile.write(data)
            self.wfile.flush()

        try:
            if thread_id:
                command = [
                    CODEX_BIN, "exec", "resume", "--model", CODEX_MODEL,
                    "--json", "--skip-git-repo-check",
                    "-c", f'sandbox_mode="{sandbox}"',
                    "-c", 'approval_policy="never"', thread_id, "-",
                ]
            else:
                command = [
                    CODEX_BIN, "exec", "--model", CODEX_MODEL, "--json",
                    "--color", "never", "--sandbox", sandbox,
                    "-c", 'approval_policy="never"',
                    "--skip-git-repo-check", "-",
                ]

            environment = os.environ.copy()
            environment.setdefault("RUST_LOG", "error")
            process = subprocess.Popen(
                command,
                cwd=PROJECT_DIR,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                start_new_session=True,
            )
            stderr_lines = []

            def collect_stderr():
                for stderr_line in process.stderr:
                    stderr_lines.append(stderr_line.rstrip())
                    if len(stderr_lines) > 30:
                        del stderr_lines[0]

            stderr_thread = threading.Thread(target=collect_stderr, daemon=True)
            stderr_thread.start()
            process.stdin.write(build_prompt(message, skill, not thread_id))
            process.stdin.close()

            emitted_error = False
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                client_event = normalize_event(event)
                if client_event:
                    if client_event["type"] == "error":
                        emitted_error = True
                    emit(client_event)

            return_code = process.wait()
            stderr_thread.join(timeout=1)
            if return_code != 0 and not emitted_error:
                detail = "\n".join(stderr_lines[-5:]).strip()
                emit({"type": "error", "message": detail or f"Codex 退出，状态码 {return_code}"})
        except BrokenPipeError:
            if process and process.poll() is None:
                process.terminate()
        except (OSError, subprocess.SubprocessError) as error:
            try:
                emit({"type": "error", "message": f"无法启动 Codex：{error}"})
            except BrokenPipeError:
                pass
        finally:
            if process and process.poll() is None:
                process.terminate()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7777
    print(f"claude-seo AI 工作台: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
