# 交互选择 aur / pac / del (Alt+i)，从顶部开始选择
function select_pac_or_aur
    echo 'Select package manager:'
    set -l selection (printf 'aur\npac\ndel\n' | fzf --height=~6 --border --layout=reverse --no-sort --cycle --no-input --bind 'w:up,s:down')
    if test -n "$selection"
        switch $selection
            case pac aur
                commandline -r "$selection "
            case del
                commandline -r "uninstall "
        end
        commandline -f execute
    end
end
