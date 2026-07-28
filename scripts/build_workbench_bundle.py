#!/usr/bin/env python3
"""Build a credential-free local workbench zip from tracked project files."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist" / "claude-seo-workbench-local.zip"
ARCHIVE_ROOT = "claude-seo-workbench"
EXCLUDED_PREFIXES = (
    ".github/",
    "docs/worklogs/",
    "tests/",
)
EXCLUDED_FILES = {
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
}


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = Path(raw_path.decode("utf-8"))
        text = relative.as_posix()
        if text in EXCLUDED_FILES or text.startswith(EXCLUDED_PREFIXES):
            continue
        path = ROOT / relative
        if path.is_file():
            yield relative, path


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, path in tracked_files():
            archive.write(path, f"{ARCHIVE_ROOT}/{relative.as_posix()}")
    print(OUTPUT)
    print(f"{OUTPUT.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
