#!/bin/bash

# 背景图目录和软链接定义
BACKGROUNDS_DIR="$HOME/.config/omarchy/current/theme/backgrounds/"
CURRENT_BACKGROUND_LINK="$HOME/.config/omarchy/current/background"

# 0. 立即清理竞争进程 (后台运行，不阻塞脚本)
pkill -9 swaybg 2>/dev/null &

# 获取背景图片列表
mapfile -d '' -t BACKGROUNDS < <(find -L "$BACKGROUNDS_DIR" -type f -print0 | sort -z)
TOTAL=${#BACKGROUNDS[@]}

if [[ $TOTAL -eq 0 ]]; then
    notify-send "No background was found for theme" -t 2000
    exit 1
fi

# 获取当前背景路径（通过软链接）
if [[ -L "$CURRENT_BACKGROUND_LINK" ]]; then
    CURRENT_BACKGROUND=$(readlink "$CURRENT_BACKGROUND_LINK")
else
    CURRENT_BACKGROUND=""
fi

# 计算下一张图片的索引
INDEX=-1
for i in "${!BACKGROUNDS[@]}"; do
    if [[ "${BACKGROUNDS[$i]}" == "$CURRENT_BACKGROUND" ]]; then
        INDEX=$i
        break
    fi
done

if [[ $INDEX -eq -1 ]]; then
    NEW_BACKGROUND="${BACKGROUNDS[0]}"
else
    NEXT_INDEX=$(((INDEX + 1) % TOTAL))
    NEW_BACKGROUND="${BACKGROUNDS[$NEXT_INDEX]}"
fi

# 1. 立即更新软链接
ln -nsf "$NEW_BACKGROUND" "$CURRENT_BACKGROUND_LINK"

# 2. 确保 SwayNC 在后台运行 (仅在没启动时启动)
if ! pgrep -x "swaync" > /dev/null; then
    swaync & 
fi

# 3. 异步切换壁纸 (立即开始动画，不等待动画结束)
swww img "$NEW_BACKGROUND" \
    --transition-type grow \
    --transition-pos top-right \
    --transition-duration 1.0 & # 缩短至1.0秒，体感更干脆

# 4. 异步执行 Pywal 和 刷新通知中心
# 使用括号 () & 将这两个耗时操作丢进后台并行运行
(
    wal -i "$NEW_BACKGROUND" -q   # -q 静默模式减少IO消耗
    swaync-client -R              # 颜色生成后立即刷新界面
) &

exit 0
