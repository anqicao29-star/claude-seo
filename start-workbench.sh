#!/usr/bin/env sh
set -u
cd -- "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.10 or newer first." >&2
  exit 1
fi

exec python3 run_workbench.py "$@"
