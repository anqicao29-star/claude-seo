"""Central configuration for the local workbench."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional


SUPPORTED_SANDBOXES = ("read-only", "workspace-write")


@dataclass(frozen=True)
class WorkbenchConfig:
    home: Path
    project_dir: Path
    ui_dir: Path
    skills_dir: Path
    agents_dir: Path
    drift_db: Path
    codex_bin: str
    codex_model: str
    max_sandbox: str
    max_concurrent_tasks: int
    task_timeout_seconds: int
    max_request_bytes: int = 256 * 1024
    max_message_chars: int = 100_000


def _bounded_int(
    values: Mapping[str, str],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(values.get(name, str(default)))
    except (TypeError, ValueError):
        return default
    return max(minimum, min(value, maximum))


def load_config(
    server_file: Path,
    environ: Optional[Mapping[str, str]] = None,
) -> WorkbenchConfig:
    """Load configuration once at process start and fail closed on permissions."""
    values = os.environ if environ is None else environ
    ui_dir = server_file.resolve().parent
    project_dir = ui_dir.parent
    home = Path.home()
    max_sandbox = values.get("CLAUDE_SEO_MAX_SANDBOX", "read-only")
    if max_sandbox not in SUPPORTED_SANDBOXES:
        max_sandbox = "read-only"

    return WorkbenchConfig(
        home=home,
        project_dir=project_dir,
        ui_dir=ui_dir,
        skills_dir=home / ".claude" / "skills",
        agents_dir=home / ".claude" / "agents",
        drift_db=home / ".cache" / "claude-seo" / "drift" / "baselines.db",
        codex_bin=values.get("CLAUDE_SEO_CODEX_BIN") or shutil.which("codex") or "codex",
        codex_model=values.get("CLAUDE_SEO_CODEX_MODEL", "gpt-5.4"),
        max_sandbox=max_sandbox,
        max_concurrent_tasks=_bounded_int(
            values,
            "CLAUDE_SEO_MAX_CONCURRENT_TASKS",
            2,
            1,
            4,
        ),
        task_timeout_seconds=_bounded_int(
            values,
            "CLAUDE_SEO_TASK_TIMEOUT_SECONDS",
            900,
            30,
            3600,
        ),
    )
