#!/bin/sh

# 替换成你自己的内置显示器名称
BUILDIN_DISPLAY_NAME="eDP-1" 

# 替换成你内置显示器恢复时的配置（分辨率, 位置, 缩放）
# 示例：1920x1080分辨率, 0x0位置, 1.0缩放
DEFAULT_BUILDIN_ENABLE="$BUILDIN_DISPLAY_NAME, 2560x1600, auto,1.6"

# 获取当前连接的显示器数量
# 注意：这个grep|wc -l的方法在不同Hyprland版本可能需要微调，但通常有效
NUM_OF_MONITORS=$(hyprctl monitors all | grep -c 'Monitor')

if [ "$NUM_OF_MONITORS" -gt 1 ]; then
    # 超过一个显示器连接时（外接显示器已连接）
    # 禁用内置显示器
    hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, disable"
else
    # 只有一个显示器连接时（外接显示器已断开）
    # 重新启用内置显示器
    hyprctl keyword monitor "$DEFAULT_BUILDIN_ENABLE"
fi
