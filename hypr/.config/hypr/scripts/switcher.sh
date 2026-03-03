# #!/bin/sh

# # 笔记本内屏名称
# BUILDIN_DISPLAY_NAME="eDP-1"

# # 检查内屏是否包含 "disabled" 字样
# # hyprctl monitors 输出中，被禁用的屏幕会显示在列表里并标记 disabled
# if hyprctl monitors all | grep -A 5 "$BUILDIN_DISPLAY_NAME" | grep -q "disabled"; then
#     # 当前是关闭状态 -> 执行恢复（开启）
#     # 注意：逗号后面必须有空格
#     hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, 2560x1600, auto, 1.6"
# else
#     # 当前是开启状态 -> 执行关闭（只留 HDMI）
#     hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, disable"
# fi


#!/bin/bash
BUILDIN_DISPLAY_NAME="eDP-1"

# 检查HDMI是否连接
HDMI_CONNECTED=$(hyprctl monitors all | grep -c "HDMI")

# 如果没有HDMI，直接确保内屏开启
if [ "$HDMI_CONNECTED" -eq 0 ]; then
    hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, 2560x1600@120, auto, 1.6"
    exit 0
fi

# 有HDMI的情况下，按原逻辑切换
if hyprctl monitors all | grep "$BUILDIN_DISPLAY_NAME" -A 20 | grep -q "disabled: true"; then
    hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, 2560x1600@120, auto, 1.6"
else
    hyprctl keyword monitor "$BUILDIN_DISPLAY_NAME, disable"
fi
