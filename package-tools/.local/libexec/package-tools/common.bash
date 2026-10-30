#!/usr/bin/env bash
# aur / pac / uninstall 共用的交互、动画和结果核验逻辑。
# 主色来自 青.md：月白、碧青、浅青、天青、灰青、玉青、青黑。

pt_notice() {
    local color=$1 symbol=$2 message=$3
    printf '%s%s%s %s\n' "$color" "$symbol" "$PT_RESET" "$message" >&2
}

pt_cleanup() {
    if [[ -n ${PT_JOB_PID:-} ]]; then
        kill "$PT_JOB_PID" 2>/dev/null || :
        wait "$PT_JOB_PID" 2>/dev/null || :
        PT_JOB_PID=
    fi
    if [[ ${PT_SPINNING:-0} == 1 ]]; then
        printf '\r\033[2K\033[?25h' >&2
        PT_SPINNING=0
    fi
    if [[ -n ${PT_WORKDIR:-} && -d $PT_WORKDIR ]]; then
        rm -rf -- "$PT_WORKDIR"
        PT_WORKDIR=
    fi
}

pt_cancel() {
    local code=$1
    trap - INT TERM HUP
    pt_cleanup
    pt_notice "$PT_WARN" '!' '操作已取消；不会显示成功提示。'
    exit "$code"
}

# 只用于只读操作：完整捕获结果，在真正完成前显示不定进度动画。
# 安装/卸载本身始终前台运行，保留密码、确认和原生下载/构建输出。
pt_capture() {
    local destination=$1 label=$2 result=0 frame=0
    shift 2
    local -a frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    "$@" >"$destination" 2>"$PT_WORKDIR/command-error" </dev/null &
    PT_JOB_PID=$!
    if [[ $PT_ANIMATE == 1 ]]; then
        PT_SPINNING=1
        printf '\033[?25l' >&2
        while kill -0 "$PT_JOB_PID" 2>/dev/null; do
            printf '\r\033[2K%s%s%s %s' "$PT_ACCENT" "${frames[frame % ${#frames[@]}]}" "$PT_RESET" "$label" >&2
            frame=$((frame + 1))
            sleep 0.12
        done
    else
        pt_notice "$PT_ACCENT" '…' "$label"
    fi
    if wait "$PT_JOB_PID"; then result=0; else result=$?; fi
    PT_JOB_PID=
    if [[ $PT_SPINNING == 1 ]]; then
        printf '\r\033[2K\033[?25h' >&2
        PT_SPINNING=0
    fi
    if [[ -s $PT_WORKDIR/command-error ]]; then
        cat -- "$PT_WORKDIR/command-error" >&2
    fi
    if (( result == 0 )); then
        pt_notice "$PT_MUTED" '✓' "$label：完成"
    else
        pt_notice "$PT_ERROR" '✗' "$label：失败（退出码 $result）"
    fi
    return "$result"
}

pt_package_name_valid() {
    [[ $1 =~ ^[a-zA-Z0-9@_][a-zA-Z0-9@._+-]*$ ]]
}

pt_help() {
    printf '用法：%s [搜索关键词]\n' "$1"
    printf '%s\n' 'Tab 多选，Enter 确认，Esc 取消；Alt+P 切换预览，Alt+J/K 滚动。'
    printf '%s\n' '列表和核验有加载动画；下载、构建和安装保留包管理器的真实进度与确认。'
    printf '%s\n' '成功必须同时满足：命令正常退出、本地包数据库达到目标状态。'
}

pt_verify() {
    local mode=$1 transaction_result=$2 name version query_result=0 invalid=0
    shift 2
    local -a correct=() incorrect=()
    local -A installed=()
    printf '\n%s[3/3] 核验结果%s\n' "$PT_ACCENT" "$PT_RESET" >&2
    # 查询整个本地数据库并确认查询成功，不能把查询错误误当成“已卸载”。
    if pt_capture "$PT_WORKDIR/installed" '读取本地包数据库' pacman --color never -Q; then
        :
    else
        query_result=$?
        pt_notice "$PT_ERROR" '✗' '无法读取包数据库，不能确认结果；请检查上方错误。'
        return "$query_result"
    fi
    while IFS=' ' read -r name version || [[ -n $name ]]; do
        [[ -n $name || -n $version ]] || continue
        if ! pt_package_name_valid "$name" || [[ -z $version || $version == *[[:space:]]* ]]; then
            invalid=1
            break
        fi
        installed["$name"]=$version
    done <"$PT_WORKDIR/installed"
    if (( invalid )); then
        pt_notice "$PT_ERROR" '✗' '包数据库输出异常，不能确认结果。'
        return 1
    fi
    for name in "$@"; do
        if [[ $mode == uninstall ]]; then
            if [[ -v installed[$name] ]]; then incorrect+=("$name"); else correct+=("$name"); fi
        else
            if [[ -v installed[$name] ]]; then correct+=("$name"); else incorrect+=("$name"); fi
        fi
    done
    if (( transaction_result == 0 && ${#incorrect[@]} == 0 )); then
        if [[ $mode == uninstall ]]; then
            pt_notice "$PT_OK" '✓' "卸载成功：已确认 ${#correct[@]} 个所选软件包不在本地数据库中。"
        else
            pt_notice "$PT_OK" '✓' "安装成功：已确认 ${#correct[@]} 个所选软件包已安装。"
        fi
        for name in "${correct[@]}"; do
            if [[ $mode == uninstall ]]; then
                printf '  %s\n' "$name" >&2
            else
                printf '  %s %s\n' "$name" "${installed[$name]}" >&2
            fi
        done
        return 0
    fi
    if (( transaction_result != 0 )); then
        pt_notice "$PT_ERROR" '✗' "包管理器未正常完成（退出码 $transaction_result），不宣布成功。"
    else
        pt_notice "$PT_ERROR" '✗' '包管理器虽已退出，但所选软件包未全部达到目标状态。'
    fi
    for name in "${correct[@]}"; do
        if [[ $mode == uninstall ]]; then
            printf '  [已不在数据库中] %s\n' "$name" >&2
        else
            printf '  [已安装] %s %s\n' "$name" "${installed[$name]}" >&2
        fi
    done
    for name in "${incorrect[@]}"; do
        if [[ $mode == uninstall ]]; then
            printf '  [仍然安装] %s %s\n' "$name" "${installed[$name]}" >&2
        else
            printf '  [尚未安装] %s\n' "$name" >&2
        fi
    done
    if (( transaction_result != 0 )); then return "$transaction_result"; fi
    return 1
}

package_tools_main() {
    local mode=$1 title preview query result=0 name dependency
    shift
    case "$mode" in
        aur) title='AUR 安装'; preview='yay -Siia -- {1}' ;;
        pac) title='仓库安装'; preview='pacman -Sii -- {1}' ;;
        uninstall) title='软件卸载'; preview='pacman -Qi -- {1}' ;;
        *) printf '%s\n' '未知的软件包操作。' >&2; return 64 ;;
    esac
    if [[ ${1:-} == --help || ${1:-} == -h ]]; then pt_help "$mode"; return 0; fi
    query="$*"
    local -a dependencies=(pacman fzf sudo mktemp sort grep cat rm sleep)
    [[ $mode != aur ]] || dependencies+=(yay)
    for dependency in "${dependencies[@]}"; do
        if ! command -v "$dependency" >/dev/null 2>&1; then
            printf '缺少命令：%s；没有执行安装或卸载。\n' "$dependency" >&2
            return 127
        fi
    done

    PT_ACCENT= PT_MUTED= PT_OK= PT_WARN= PT_ERROR= PT_RESET=
    PT_ANIMATE=0 PT_SPINNING=0 PT_JOB_PID= PT_WORKDIR=
    local -a native_color=(--color never)
    if [[ -t 2 && ${TERM:-dumb} != dumb ]]; then
        [[ ${PACKAGE_TOOLS_ANIMATION:-1} == 0 ]] || PT_ANIMATE=1
        if [[ ! -v NO_COLOR ]]; then
            PT_ACCENT=$'\033[38;2;167;223;219m'  # 碧青 #A7DFDB
            PT_MUTED=$'\033[38;2;150;199;196m'   # 灰青 #96C7C4
            PT_OK=$'\033[38;2;199;235;228m'      # 玉青 #C7EBE4
            PT_WARN=$'\033[38;2;255;225;168m'
            PT_ERROR=$'\033[38;2;255;183;197m'
            PT_RESET=$'\033[0m'
            native_color=(--color always)
        fi
    fi
    if ! PT_WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/package-tools.XXXXXX"); then
        printf '%s\n' '无法创建私有临时目录，没有执行安装或卸载。' >&2
        return 1
    fi
    trap pt_cleanup EXIT
    trap 'pt_cancel 130' INT
    trap 'pt_cancel 143' TERM
    trap 'pt_cancel 129' HUP

    printf '%s[1/3] %s · 选择软件包%s\n' "$PT_ACCENT" "$title" "$PT_RESET" >&2
    case "$mode" in
        aur)
            if pt_capture "$PT_WORKDIR/list" '载入 AUR 列表' yay -Slqa; then :; else return $?; fi ;;
        pac)
            if pt_capture "$PT_WORKDIR/list" '载入仓库列表' pacman -Slq; then :; else return $?; fi ;;
        uninstall)
            if pt_capture "$PT_WORKDIR/list" '载入手动安装列表' pacman -Qqe; then :; else return $?; fi ;;
    esac
    if ! LC_ALL=C sort -u -- "$PT_WORKDIR/list" >"$PT_WORKDIR/choices"; then
        pt_notice "$PT_ERROR" '✗' '无法整理软件包列表。'
        return 1
    fi
    if [[ ! -s $PT_WORKDIR/choices ]]; then
        pt_notice "$PT_MUTED" '○' '没有可选择的软件包。'
        return 0
    fi
    if LC_ALL=C grep -qvE '^[a-zA-Z0-9@_][a-zA-Z0-9@._+-]*$' "$PT_WORKDIR/choices"; then
        pt_notice "$PT_ERROR" '✗' '软件包列表包含异常名称，已停止操作。'
        return 1
    fi
    local -a picker=(
        --multi --layout=reverse --border=sharp --height=90%
        --with-shell='bash -c'
        --prompt='搜索 › ' --pointer='›' --marker='●'
        --border-label=" $title " --header-first
        --header='Tab 多选 · Enter 确认 · Esc 取消 · Alt+P 预览'
        --preview="$preview" --preview-label=' 软件包信息 '
        --preview-window='right:55%:wrap:<90(down:55%:wrap)'
        --bind='alt-p:toggle-preview,alt-j:preview-down,alt-k:preview-up'
        --bind='alt-d:preview-half-page-down,alt-u:preview-half-page-up'
        --query="$query"
    )
    if [[ -v NO_COLOR ]]; then
        picker+=(--no-color)
    else
        picker+=(--color='fg:#EBF5F7,bg:-1,hl:#BEE7E3,fg+:#122E3A,bg+:#BEE7E3,hl+:#122E3A,pointer:#A7DFDB,marker:#A7DFDB,info:#96C7C4,prompt:#A7DFDB,spinner:#BEE7E3,header:#D2EEE9,border:#A7DFDB,label:#A7DFDB,preview-fg:#EBF5F7,preview-bg:-1')
    fi
    if [[ $mode == aur ]]; then
        picker+=(--bind='alt-b:change-preview(yay -Gpa -- {1})')
        picker+=(--bind='alt-B:change-preview(yay -Siia -- {1})')
    fi
    if FZF_DEFAULT_OPTS= FZF_DEFAULT_OPTS_FILE=/dev/null fzf "${picker[@]}" <"$PT_WORKDIR/choices" >"$PT_WORKDIR/selection"; then
        :
    else
        result=$?
        if (( result == 1 || result == 130 )); then
            pt_notice "$PT_MUTED" '○' '已取消，没有执行安装或卸载。'
            return 0
        fi
        pt_notice "$PT_ERROR" '✗' "选包界面失败（退出码 $result）。"
        return "$result"
    fi
    local -a selected=() targets=()
    local -A seen=()
    while IFS= read -r name || [[ -n $name ]]; do
        [[ -n $name ]] || continue
        if ! pt_package_name_valid "$name" || ! grep -Fxq -- "$name" "$PT_WORKDIR/choices"; then
            pt_notice "$PT_ERROR" '✗' '选择结果包含异常名称，已停止操作。'
            return 1
        fi
        [[ ! -v seen[$name] ]] || continue
        seen["$name"]=1
        selected+=("$name")
        if [[ $mode == aur ]]; then targets+=("aur/$name"); else targets+=("$name"); fi
    done <"$PT_WORKDIR/selection"
    if (( ${#selected[@]} == 0 )); then
        pt_notice "$PT_MUTED" '○' '没有选择软件包。'
        return 0
    fi
    printf '\n%s[2/3] %s%s\n' "$PT_ACCENT" "$title" "$PT_RESET" >&2
    printf '  %s\n' "${selected[@]}" >&2
    pt_notice "$PT_MUTED" '→' '以下保留真实进度和确认提示；Ctrl+C 可取消。'
    if sudo -v; then :; else
        result=$?
        pt_notice "$PT_ERROR" '✗' '权限验证失败，没有开始操作。'
        return "$result"
    fi
    case "$mode" in
        aur)
            if yay "${native_color[@]}" -S --needed -- "${targets[@]}"; then result=0; else result=$?; fi ;;
        pac)
            if sudo pacman "${native_color[@]}" -S --needed -- "${targets[@]}"; then result=0; else result=$?; fi ;;
        uninstall)
            if sudo pacman "${native_color[@]}" -Rns -- "${targets[@]}"; then result=0; else result=$?; fi ;;
    esac
    pt_verify "$mode" "$result" "${selected[@]}"
}
