#!/bin/zsh
cd -- "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "没有找到 Python 3，请先安装 Python 3.10 或更高版本。"
  read -r "?按回车键关闭…"
  exit 1
fi

python3 run_workbench.py
status=$?
if [ "$status" -ne 0 ]; then
  echo
  read -r "?启动失败。按回车键关闭…"
fi
exit "$status"
