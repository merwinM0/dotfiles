# If not running interactively, don't do anything (leave this at the top of this file)
[[ $- != *i* ]] && return

# All the default Omarchy aliases and functions
# (don't mess with these directly, just overwrite them here!)
source ~/.local/share/omarchy/default/bash/rc

# Add your own exports, aliases, and functions here.
#
# Make an alias for invoking commands you use constantly
#
alias mm='zellij'
alias c='clear' 
alias ca='cargo'
alias gol='go build -ldflags="-s -w" .'
alias p='posting'
alias ll='zellij a a'

bind -x '"\ez": helix_smart'
bind -x '"\em": "gitui"'



helix_smart() {
    if [ -d .venv ]; then
        source .venv/bin/activate
    fi
    helix .
}


[[ $- == *i* ]] && bind -x '"\ex": '\''y'\'''
y() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
    yazi "$@" --cwd-file="$tmp"
    IFS= read -r -d '' cwd < "$tmp"
    if [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        builtin cd -- "$cwd"
        printf '\e[1A\e[K'
    fi
    rm -f -- "$tmp"
}
. "$HOME/.cargo/env"

gow() {
    local args="$@"
    
    env CGO_ENABLED=1 \
        GOOS=windows GOARCH=amd64 \
        CC=x86_64-w64-mingw32-gcc \
        CXX=x86_64-w64-mingw32-g++ \
        go build \
        -ldflags '-s -w -extldflags "-static -static-libgcc -static-libstdc++"' \
        $args
}


export PATH="$PATH:/usr/local/bin"
    
