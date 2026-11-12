#!/usr/bin/env sh
set -u
cd -- "$(dirname "$0")" || exit 1

PYTHON_BIN=""
for candidate in python3 python3.13 python3.12 python3.11 python3.10 \
  /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12 \
  /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3.10 \
  /usr/local/bin/python3.13 /usr/local/bin/python3.12 \
  /usr/local/bin/python3.11 /usr/local/bin/python3.10
do
  if command -v "$candidate" >/dev/null 2>&1 && \
    "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1
  then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3.10 or newer was not found. Install it first, then start again." >&2
  exit 1
fi

exec "$PYTHON_BIN" run_workbench.py "$@"
