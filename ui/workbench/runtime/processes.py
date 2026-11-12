"""Cross-platform helpers for stopping a runtime and all of its children."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from typing import Dict, Iterable, List, Set


def _process_table() -> Dict[int, List[int]]:
    """Return parent -> children mappings on POSIX systems."""
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid="],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if result.returncode != 0:
        return {}

    children: Dict[int, List[int]] = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        try:
            pid, parent_pid = (int(value) for value in fields)
        except ValueError:
            continue
        children.setdefault(parent_pid, []).append(pid)
    return children


def _descendants(root_pid: int) -> List[int]:
    table = _process_table()
    result: List[int] = []
    stack = list(table.get(root_pid, []))
    while stack:
        pid = stack.pop()
        result.append(pid)
        stack.extend(table.get(pid, []))
    return result


def _is_running(pid: int) -> bool:
    try:
        result = subprocess.run(
            ["ps", "-o", "stat=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=1,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    status = result.stdout.strip()
    return result.returncode == 0 and bool(status) and not status.startswith("Z")


def _signal_groups(pids: Iterable[int], sig: int) -> None:
    own_group = os.getpgrp()
    groups: Set[int] = set()
    for pid in pids:
        try:
            group = os.getpgid(pid)
        except (OSError, ProcessLookupError):
            continue
        if group != own_group:
            groups.add(group)
    for group in groups:
        try:
            os.killpg(group, sig)
        except (OSError, ProcessLookupError):
            pass


def _signal_processes(pids: Iterable[int], sig: int) -> None:
    for pid in pids:
        try:
            os.kill(pid, sig)
        except (OSError, ProcessLookupError):
            pass


def terminate_process_tree(process: subprocess.Popen, grace_seconds: float = 1.0) -> None:
    """Stop a runtime plus descendants that created their own process groups."""
    pid = getattr(process, "pid", None)
    if not isinstance(pid, int) or pid <= 0:
        if process.poll() is None:
            process.terminate()
        return
    if process.poll() is not None:
        return

    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            process.terminate()
        return

    # Capture descendants before stopping the runtime. Once the parent exits,
    # grandchildren can be re-parented and are no longer discoverable from it.
    descendants = _descendants(pid)
    targets = [*reversed(descendants), pid]
    _signal_groups(targets, signal.SIGTERM)
    _signal_processes(targets, signal.SIGTERM)

    deadline = time.monotonic() + max(0.0, grace_seconds)
    while time.monotonic() < deadline:
        if not any(_is_running(target) for target in targets):
            return
        time.sleep(0.05)

    survivors = [target for target in targets if _is_running(target)]
    if survivors:
        _signal_groups(survivors, signal.SIGKILL)
        _signal_processes(survivors, signal.SIGKILL)
