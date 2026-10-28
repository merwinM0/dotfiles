#!/bin/sh
# 保留 opener 入口；由 Python 直接处理终端按键和清屏恢复。
case $0 in
    */*) script_dir=${0%/*} ;;
    *) script_dir=. ;;
esac
exec python3 "$script_dir/view-image.py" "$@"
