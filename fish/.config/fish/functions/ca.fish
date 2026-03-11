# ~/.config/fish/functions/ca.fish
function ca -d "Cargo with beautiful colored output"
    # 颜色定义
    set -l RED (set_color red)
    set -l GREEN (set_color green)
    set -l YELLOW (set_color yellow)
    set -l BLUE (set_color blue)
    set -l MAGENTA (set_color magenta)
    set -l CYAN (set_color cyan)
    set -l BOLD (set_color --bold)
    set -l NORMAL (set_color normal)

    # 边框样式
    set -l BORDER_TOP "╔══════════════════════════════════════════════════════════╗"
    set -l BORDER_MID "╠══════════════════════════════════════════════════════════╣"
    set -l BORDER_BOTTOM "╚══════════════════════════════════════════════════════════╝"

    # 如果没有参数，显示帮助
    if test (count $argv) -eq 0
        echo $BLUE"╔══════════════════════════════════════════════════════════╗"$NORMAL
        echo $BLUE"║                     ca - Cargo美化命令                     ║"$NORMAL
        echo $BLUE"╠══════════════════════════════════════════════════════════╣"$NORMAL
        echo $BLUE"║ 用法: ca <cargo命令> [参数]                               ║"$NORMAL
        echo $BLUE"║                                                          ║"$NORMAL
        echo $BLUE"║ 示例:                                                    ║"$NORMAL
        echo $BLUE"║   ca run         # 运行项目                              ║"$NORMAL
        echo $BLUE"║   ca build       # 构建项目                              ║"$NORMAL
        echo $BLUE"║   ca test        # 运行测试                              ║"$NORMAL
        echo $BLUE"║   ca check       # 检查代码                              ║"$NORMAL
        echo $BLUE"╚══════════════════════════════════════════════════════════╝"$NORMAL
        return
    end

    # 运行原始 cargo 命令并处理输出
    command cargo $argv 2>&1 | while read -l line

        # 错误处理 - 带完整边框
        if string match -qr "error(\[.*\])?:|Error:" $line
            echo $RED$BORDER_TOP$NORMAL
            echo $RED"║ ❌ ERROR: $line"$NORMAL
            echo $RED$BORDER_BOTTOM$NORMAL

            # 严重错误（如编译失败）
        else if string match -q "*could not compile*" $line
            echo $RED$BORDER_TOP$NORMAL
            echo $RED"║ 🔥 COMPILE ERROR: $line"$NORMAL
            echo $RED$BORDER_BOTTOM$NORMAL

            # 警告处理 - 带完整边框
        else if string match -qr "warning(\[.*\])?:|Warning:" $line
            echo $YELLOW$BORDER_TOP$NORMAL
            echo $YELLOW"║ ⚠️  WARNING: $line"$NORMAL
            echo $YELLOW$BORDER_BOTTOM$NORMAL

            # 注意/提示信息
        else if string match -qr "note:|Note:" $line
            echo $BLUE"║ ℹ️  $line"$NORMAL

            # 编译信息
        else if string match -q "*Compiling*" $line
            echo $BLUE"🔨 $line"$NORMAL

            # 完成信息
        else if string match -q "*Finished*" $line
            # 检测是release还是debug
            if string match -q "*release*" $line
                echo $GREEN"🚀 $line"$NORMAL
            else
                echo $GREEN"✨ $line"$NORMAL
            end

            # 运行信息
        else if string match -q "*Running*" $line
            echo $MAGENTA"▶️  $line"$NORMAL

            # 测试结果
        else if string match -q "*test result:*" $line
            if string match -q "*FAILED*" $line
                echo $RED"❌ $line"$NORMAL
            else if string match -q "*ok*" $line
                echo $GREEN"✅ $line"$NORMAL
            else
                echo $CYAN"🧪 $line"$NORMAL
            end

            # 测试单个测试
        else if string match -q "*test ... ok" $line
            echo $GREEN"  ✅ $line"$NORMAL
        else if string match -q "*test ... FAILED" $line
            echo $RED"  ❌ $line"$NORMAL

            # 文档信息
        else if string match -q "*Documenting*" $line
            echo $BLUE"📖 $line"$NORMAL

            # 检查信息
        else if string match -q "*Checking*" $line
            echo $CYAN"🔍 $line"$NORMAL

            # 下载信息
        else if string match -q "*Downloading*" $line
            echo $CYAN"📥 $line"$NORMAL

            # 更新信息
        else if string match -q "*Updating*" $line
            echo $YELLOW"🔄 $line"$NORMAL

            # 修复信息
        else if string match -q "*Fixed*" $line
            echo $GREEN"🔧 $line"$NORMAL

            # 代码位置 (--> src/main.rs:10:5)
        else if string match -qr "--> .*:\d+:\d+" $line
            echo $CYAN"📍 $line"$NORMAL

            # 代码行 (带 | 符号)
        else if string match -q "*| *" $line
            # 检查是否是错误/警告的代码行
            if string match -q "*^ *" $line
                echo $RED"  $line"$NORMAL
            else
                echo $NORMAL"  $line"$NORMAL
            end

            # 数字信息 (如 "Compiling 15 files")
        else if string match -qr "^[0-9]+" $line
            echo $CYAN"📊 $line"$NORMAL

            # 空白行
        else if test -z "$line"
            echo ""

            # 其他行
        else
            # 尝试检测这是否是错误上下文的一部分
            if string match -q "*^ *" $line
                echo $RED"  $line"$NORMAL
            else
                echo $line
            end
        end
    end

    # 返回 cargo 的退出状态
    return $pipestatus[1]
end
