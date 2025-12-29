#!/bin/bash

DIR="/home/mo/.config/hypr/imgs/states"
SYMLINK="/home/mo/.config/hypr/current_status.png"

# 进入目录，确保路径正确
cd "$DIR" || exit

# --- 核心修复：只匹配真实存在的文件 ---
# 使用 nullglob 确保如果没有匹配项，数组就是空的，而不是带有 "*" 的字符串
shopt -s nullglob
FILES=( *.png *.jpg *.jpeg *.webp *.gif )
shopt -u nullglob

# 如果文件夹是空的，直接退出
if [ ${#FILES[@]} -eq 0 ]; then
    echo "错误：目录中没有任何图片文件！"
    exit 1
fi

# 获取当前指向的文件名
CURRENT=$(basename "$(readlink "$SYMLINK" 2>/dev/null)")

# 寻找下一张图
NEXT_PIC=""
for i in "${!FILES[@]}"; do
    if [ "${FILES[$i]}" == "$CURRENT" ]; then
        NEXT_INDEX=$(( (i + 1) % ${#FILES[@]} ))
        NEXT_PIC="${FILES[$NEXT_INDEX]}"
        break
    fi
done

# 如果是第一次运行或者当前图被删了，选第一张
if [ -z "$NEXT_PIC" ]; then
    NEXT_PIC="${FILES[0]}"
fi

# 创建链接并强制刷新时间戳
ln -sf "$DIR/$NEXT_PIC" "$SYMLINK"
touch -h "$SYMLINK" 

echo "成功切换至: $NEXT_PIC"
