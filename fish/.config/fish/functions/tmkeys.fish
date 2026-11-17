function tmkeys --description '切换当前 tmux 窗格的 Alt 快捷键'
    if test (count $argv) -gt 1
        printf '用法：tmkeys [tmux|fish|toggle|status]\n' >&2
        return 2
    end

    set -l action status
    if set -q argv[1]
        set action "$argv[1]"
    end
    switch "$action"
        case -h --help help
            printf '%s\n' \
                'tmkeys tmux    Alt 快捷键交给 tmux（默认）' \
                'tmkeys fish    Alt 快捷键交给当前程序' \
                'tmkeys toggle  切换模式' \
                'tmkeys status  查看当前窗格模式'
            return 0
        case tmux fish toggle status
        case '*'
            printf '未知模式：%s。可用：tmux、fish、toggle、status。\n' "$action" >&2
            return 2
    end

    if not set -q TMUX; or test -z "$TMUX"; or not set -q TMUX_PANE; or test -z "$TMUX_PANE"
        printf '当前不在 tmux 中，无需切换。\n' >&2
        return 1
    end
    if not command -q tmux
        printf '找不到 tmux 命令。\n' >&2
        return 127
    end

    set -l current (command tmux display-message -p -t "$TMUX_PANE" '#{@altkeys_mode}')
    or return $status
    if not contains -- "$current" tmux fish
        printf '请先加载配置：tmux source-file ~/.tmux.conf\n' >&2
        return 1
    end

    if test "$action" = status
        printf '%s\n' "$current"
        return 0
    end
    if test "$action" = toggle
        if test "$current" = tmux
            set action fish
        else
            set action tmux
        end
    end

    command tmux set-option -p -t "$TMUX_PANE" @altkeys_mode "$action"
    or return $status
    printf '%s\n' "$action"
end
