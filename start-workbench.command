#!/bin/zsh
cd -- "$(dirname "$0")" || exit 1

/bin/sh ./start-workbench.sh "$@"
status=$?
if [ "$status" -ne 0 ]; then
  echo
  read -r "?启动失败。按回车键关闭…"
fi
exit "$status"
