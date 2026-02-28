#!/bin/sh

# 笔记本内屏名称
BUILDIN_DISPLAY_NAME="eDP-1"

# 内屏恢复时的配置
DEFAULT_BUILDIN_ENABLE="$BUILDIN_DISPLAY_NAME, 2560x1600, auto, 1.6"

# 获取当前连接的显示器数量
NUM_OF_MONITORS=$(hyprctl monitors all | grep -c 'Monitor')

if [ "$NUM_OF_MONITORS" -gt 1 ]; then
    # HDMI 已连接：禁用内屏，只显示 HDMI 显示器
    hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, disable"
else
    # HDMI 已断开：恢复内屏
    hyprctl keyword monitor "$DEFAULT_BUILDIN_ENABLE"
fi
