"""Isolated file-write previews with conflict checks, backups and undo."""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_FALLBACK_COPY_BYTES = 64 * 1024 * 1024
MAX_CHANGED_FILES = 200
MAX_DIFF_CHARS = 200_000
IGNORED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
}
SENSITIVE_NAMES = {
    ".env",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> Optional[str]:
    if not path.is_file() or path.is_symlink():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sensitive(relative: Path) -> bool:
    parts = relative.parts
    if any(part in IGNORED_DIRS for part in parts):
        return True
    name = relative.name.lower()
    if name in SENSITIVE_NAMES or name.endswith((".pem", ".key", ".p12", ".pfx")):
        return True
    if name.startswith(".env.") and name not in (".env.example", ".env.sample"):
        return True
    return False


def safe_relative(value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise PreviewUnsafeError(f"不安全的文件路径：{value}")
    if is_sensitive(relative):
        raise PreviewUnsafeError(f"敏感文件不允许通过预览写入：{value}")
    return relative


def safe_destination(workspace: Path, relative: Path) -> Path:
    destination = workspace / relative
    resolved_workspace = workspace.resolve()
    resolved_parent = destination.parent.resolve()
    if resolved_parent != resolved_workspace and resolved_workspace not in resolved_parent.parents:
        raise PreviewUnsafeError(f"目标路径逃逸工作目录：{relative}")
    if destination.is_symlink():
        raise PreviewUnsafeError(f"符号链接不允许自动写入：{relative}")
    return destination


def read_text_file(path: Path) -> tuple[bytes, list[str]]:
    data = path.read_bytes()
    if len(data) > MAX_FILE_BYTES:
        raise PreviewUnsafeError(f"文件超过 2 MB，拒绝自动写入：{path.name}")
    if b"\0" in data:
        raise PreviewUnsafeError(f"二进制文件不允许自动写入：{path.name}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PreviewUnsafeError(f"非 UTF-8 文件不允许自动写入：{path.name}") from error
    return data, text.splitlines(keepends=True)


class PreviewError(RuntimeError):
    pass


class PreviewNotFoundError(PreviewError):
    pass


class PreviewStateError(PreviewError):
    pass


class PreviewConflictError(PreviewError):
    pass


class PreviewUnsafeError(PreviewError):
    pass


class WritePreviewManager:
    """Create and apply isolated write previews.

    Git workspaces copy tracked working-tree files only. This avoids copying
    generated output directories and, more importantly, never exposes ignored
    credential files to the runtime staging area. Non-git workspaces use a
    conservative size-capped copy.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            self.cache_dir.chmod(0o700)
        except OSError:
            pass
        self._lock = threading.RLock()

    def _root(self, preview_id: str) -> Path:
        if not re.fullmatch(r"preview_[0-9a-f]{32}", preview_id):
            raise PreviewNotFoundError(preview_id)
        return self.cache_dir / preview_id

    def _meta_path(self, preview_id: str) -> Path:
        return self._root(preview_id) / "meta.json"

    def _load(self, preview_id: str) -> Dict[str, Any]:
        path = self._meta_path(preview_id)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PreviewNotFoundError(preview_id) from error

    def _save(self, meta: Dict[str, Any]) -> None:
        path = self._meta_path(meta["preview_id"])
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(temporary, path)

    def _git_files(self, workspace: Path) -> Optional[list[Path]]:
        try:
            result = subprocess.run(
                ["git", "ls-files", "-z", "--cached"],
                cwd=workspace,
                capture_output=True,
                check=False,
            )
        except OSError:
            return None
        if result.returncode != 0:
            return None
        files = []
        for raw in result.stdout.split(b"\0"):
            if not raw:
                continue
            try:
                relative = Path(raw.decode("utf-8"))
            except UnicodeDecodeError:
                continue
            if not is_sensitive(relative):
                files.append(relative)
        return files

    def _fallback_files(self, workspace: Path) -> list[Path]:
        files: list[Path] = []
        total = 0
        for current, dirs, names in os.walk(workspace):
            current_path = Path(current)
            relative_dir = current_path.relative_to(workspace)
            dirs[:] = [
                name
                for name in dirs
                if not is_sensitive(relative_dir / name)
                and not (current_path / name).is_symlink()
            ]
            for name in names:
                source = current_path / name
                relative = source.relative_to(workspace)
                if source.is_symlink() or not source.is_file() or is_sensitive(relative):
                    continue
                total += source.stat().st_size
                if total > MAX_FALLBACK_COPY_BYTES:
                    raise PreviewUnsafeError(
                        "非 Git 工作目录超过 64 MB，请先缩小目录范围或初始化 Git"
                    )
                files.append(relative)
        return files

    def create(self, task_id: str, workspace: Path) -> Dict[str, Any]:
        workspace = workspace.resolve()
        if not workspace.is_dir():
            raise PreviewUnsafeError("工作目录不存在")
        preview_id = f"preview_{uuid.uuid4().hex}"
        root = self._root(preview_id)
        stage = root / "workspace"
        stage.mkdir(parents=True, mode=0o700)
        files = self._git_files(workspace)
        source_mode = "git-tracked" if files is not None else "directory"
        if files is None:
            files = self._fallback_files(workspace)

        baseline: Dict[str, str] = {}
        for relative in files:
            source = workspace / relative
            if not source.is_file() or source.is_symlink():
                continue
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            digest = file_hash(source)
            if digest is not None:
                baseline[relative.as_posix()] = digest

        meta: Dict[str, Any] = {
            "preview_id": preview_id,
            "task_id": task_id,
            "workspace": str(workspace),
            "stage": str(stage),
            "source_mode": source_mode,
            "status": "editing",
            "created_at": utc_timestamp(),
            "updated_at": utc_timestamp(),
            "baseline": baseline,
            "changes": [],
            "diff": "",
            "blocked": [],
        }
        self._save(meta)
        return self.snapshot(meta)

    def workspace(self, preview_id: str) -> Path:
        return Path(self._load(preview_id)["stage"])

    def _stage_files(self, stage: Path) -> Iterable[Path]:
        for path in stage.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(stage)
            yield relative

    def capture(self, preview_id: str) -> Dict[str, Any]:
        with self._lock:
            meta = self._load(preview_id)
            if meta["status"] != "editing":
                raise PreviewStateError("预览不在可收集状态")
            workspace = Path(meta["workspace"])
            stage = Path(meta["stage"])
            baseline: Dict[str, str] = meta["baseline"]
            staged = {path.as_posix(): path for path in self._stage_files(stage)}
            candidates = sorted(set(baseline) | set(staged))
            changes = []
            blocked = []
            diffs: list[str] = []

            for path in stage.rglob("*"):
                if path.is_symlink():
                    blocked.append(f"符号链接不允许自动写入：{path.relative_to(stage)}")

            for value in candidates:
                relative = Path(value)
                source_path = workspace / relative
                stage_path = stage / relative
                old_hash = baseline.get(value)
                new_hash = file_hash(stage_path)
                if old_hash == new_hash:
                    continue
                if len(changes) >= MAX_CHANGED_FILES:
                    blocked.append("修改文件超过 200 个，拒绝自动应用")
                    break
                if is_sensitive(relative):
                    blocked.append(f"敏感路径：{value}")
                    continue
                current_hash = file_hash(source_path)
                if current_hash != old_hash:
                    blocked.append(f"原文件在任务期间发生变化：{value}")
                    continue
                try:
                    old_data, old_lines = (
                        read_text_file(source_path) if old_hash is not None else (b"", [])
                    )
                    new_data, new_lines = (
                        read_text_file(stage_path) if new_hash is not None else (b"", [])
                    )
                except PreviewUnsafeError as error:
                    blocked.append(f"{value}：{error}")
                    continue
                kind = "added" if old_hash is None else "deleted" if new_hash is None else "modified"
                changes.append(
                    {
                        "path": value,
                        "kind": kind,
                        "old_hash": old_hash,
                        "new_hash": new_hash,
                        "old_size": len(old_data),
                        "new_size": len(new_data),
                    }
                )
                diffs.extend(
                    difflib.unified_diff(
                        old_lines,
                        new_lines,
                        fromfile=f"a/{value}",
                        tofile=f"b/{value}",
                    )
                )

            diff = "".join(diffs)
            if len(diff) > MAX_DIFF_CHARS:
                blocked.append("Diff 超过 200,000 个字符，拒绝自动应用")
                diff = diff[:MAX_DIFF_CHARS] + "\n… Diff 已截断 …\n"
            meta["changes"] = changes
            meta["blocked"] = blocked
            meta["diff"] = diff
            meta["status"] = "blocked" if blocked else "pending" if changes else "empty"
            meta["updated_at"] = utc_timestamp()
            self._save(meta)
            return self.snapshot(meta)

    def snapshot(self, meta_or_id: Any) -> Dict[str, Any]:
        meta = self._load(meta_or_id) if isinstance(meta_or_id, str) else meta_or_id
        return {
            "preview_id": meta["preview_id"],
            "task_id": meta["task_id"],
            "status": meta["status"],
            "source_mode": meta["source_mode"],
            "files": [
                {
                    "path": change["path"],
                    "kind": change["kind"],
                    "old_size": change["old_size"],
                    "new_size": change["new_size"],
                }
                for change in meta.get("changes", [])
            ],
            "diff": meta.get("diff", ""),
            "blocked": meta.get("blocked", []),
            "created_at": meta["created_at"],
            "updated_at": meta["updated_at"],
        }

    def get(self, preview_id: str) -> Dict[str, Any]:
        with self._lock:
            return self.snapshot(self._load(preview_id))

    def _validate_pending(self, meta: Dict[str, Any]) -> None:
        if meta["status"] != "pending":
            raise PreviewStateError("只有等待确认的预览可以应用")
        workspace = Path(meta["workspace"])
        for change in meta["changes"]:
            relative = safe_relative(change["path"])
            destination = safe_destination(workspace, relative)
            if change["old_hash"] is None and destination.exists():
                raise PreviewConflictError(f"目标文件已经存在，请重新生成预览：{relative}")
            if file_hash(destination) != change["old_hash"]:
                raise PreviewConflictError(f"文件已变化，请重新生成预览：{relative}")

    def _restore_backup(self, meta: Dict[str, Any], require_applied_hash: bool) -> None:
        workspace = Path(meta["workspace"])
        backup = self._root(meta["preview_id"]) / "backup"
        for change in reversed(meta["changes"]):
            relative = safe_relative(change["path"])
            destination = safe_destination(workspace, relative)
            if require_applied_hash and file_hash(destination) != change["new_hash"]:
                raise PreviewConflictError(f"文件应用后又被修改，拒绝覆盖：{relative}")
            original = backup / relative
            if change["old_hash"] is None:
                if destination.exists() and not destination.is_symlink():
                    destination.unlink()
            else:
                if not original.is_file() or original.is_symlink():
                    raise PreviewStateError(f"备份缺失：{relative}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary = destination.with_name(f".{destination.name}.restore-{uuid.uuid4().hex}")
                shutil.copy2(original, temporary)
                os.replace(temporary, destination)

    def apply(self, preview_id: str) -> Dict[str, Any]:
        with self._lock:
            meta = self._load(preview_id)
            self._validate_pending(meta)
            workspace = Path(meta["workspace"])
            stage = Path(meta["stage"])
            backup = self._root(preview_id) / "backup"
            backup.mkdir(parents=True, exist_ok=True, mode=0o700)
            for change in meta["changes"]:
                relative = safe_relative(change["path"])
                source = workspace / relative
                if change["old_hash"] is not None:
                    target = backup / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
            try:
                for change in meta["changes"]:
                    relative = safe_relative(change["path"])
                    destination = safe_destination(workspace, relative)
                    staged = stage / relative
                    if change["new_hash"] is None:
                        destination.unlink()
                        continue
                    if not staged.is_file() or staged.is_symlink():
                        raise PreviewStateError(f"预览文件缺失：{relative}")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temporary = destination.with_name(f".{destination.name}.apply-{uuid.uuid4().hex}")
                    shutil.copy2(staged, temporary)
                    os.replace(temporary, destination)
            except Exception:
                self._restore_backup(meta, require_applied_hash=False)
                raise
            meta["status"] = "applied"
            meta["applied_at"] = utc_timestamp()
            meta["updated_at"] = utc_timestamp()
            self._save(meta)
            return self.snapshot(meta)

    def undo(self, preview_id: str) -> Dict[str, Any]:
        with self._lock:
            meta = self._load(preview_id)
            if meta["status"] != "applied":
                raise PreviewStateError("只有已应用的预览可以撤销")
            self._restore_backup(meta, require_applied_hash=True)
            meta["status"] = "undone"
            meta["updated_at"] = utc_timestamp()
            self._save(meta)
            return self.snapshot(meta)

    def discard(self, preview_id: str) -> Dict[str, Any]:
        with self._lock:
            meta = self._load(preview_id)
            if meta["status"] not in {"editing", "pending", "empty", "blocked"}:
                raise PreviewStateError("当前预览不能丢弃")
            stage = Path(meta["stage"])
            if stage.is_dir():
                shutil.rmtree(stage)
            meta["status"] = "discarded"
            meta["updated_at"] = utc_timestamp()
            self._save(meta)
            return self.snapshot(meta)
