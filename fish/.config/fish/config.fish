# source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

### --- 1. 基础环境检查 ---
if not status is-interactive
    exit
end

### --- 3. 别名 (Aliases) ---
alias mm='zellij'
alias c='clear'
alias ca='cargo'
alias gol='go build -ldflags="-s -w" .'
alias p='posting'
alias ll='zellij a a'
# alias l='ls -a'
# alias l='eza -1  --color=always --icons --group-directories-first'
alias ls='eza -l --sort=extension --group-directories-first'
alias kimg='kitty +kitten icat'

# fish_add_path /usr/local/bin
# fish_add_path "$HOME/.cargo/bin"

# Helix 智能启动
function helix_smart
    if test -d .venv
        # Fish 激活虚拟环境通常使用 bin/activate.fish
        if test -f .venv/bin/activate.fish
            source .venv/bin/activate.fish
        end
    end
    helix .
end

# Yazi 协同跳转 (官方推荐的 Fish 版写法)
function y
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if set cwd (command cat -- "$tmp"); and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        builtin cd -- "$cwd"
    end
    rm -f -- "$tmp"
end

# Go Windows 交叉编译
function gow
    set -l args $argv
    env CGO_ENABLED=1 \
        GOOS=windows GOARCH=amd64 \
        CC=x86_64-w64-mingw32-gcc \
        CXX=x86_64-w64-mingw32-g++ \
        go build \
        -ldflags '-s -w -extldflags "-static -static-libgcc -static-libstdc++"' \
        $args
end

### --- 6. 快捷键绑定 (Key Bindings) ---
# Fish 的绑定需要放在 fish_user_key_bindings 函数中或直接写在 config 里
# \ez 是 Alt+z, \em 是 Alt+m, \ex 是 Alt+x

# function fish_user_key_bindings
bind \ez 'helix_smart; commandline -f repaint'
bind \em 'gitui; commandline -f repaint'
bind \ex 'y; commandline -f repaint'
bind \ep pi
# end

set -g fish_greeting

# uv
# fish_add_path "/home/mo/.local/share/../bin"

# Fcitx5 环境变量
set -gx GTK_IM_MODULE fcitx
set -gx QT_IM_MODULE fcitx
set -gx XMODIFIERS @im=fcitx

set -gx PATH ~/.local/bin $PATH

# bun
set --export BUN_INSTALL "$HOME/.bun"
set --export PATH $BUN_INSTALL/bin $PATH

# Pi
fish_add_path "/home/mo/.local/share/pi-node/node-v22.22.3-linux-x64/bin"
