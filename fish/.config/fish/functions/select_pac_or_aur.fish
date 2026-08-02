# 交互选择 pac / aur / del (Alt+i)
function select_pac_or_aur
    echo 'Select package manager:'
    set -l selection (printf 'pac\naur\ndel' | fzf --height=~6 --border --cycle --no-input --bind 'w:up,s:down')
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
