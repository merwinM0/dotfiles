# 亮青主题：主色 8be9e1，整体比原湖青配色更明亮。
# 仅设置配色；不修改 PATH、终端背景、提示符结构或快捷键。
status is-interactive; or return

# 语法高亮：亮青命令/操作符、近白正文、浅青引号和次要信息。
set --global fish_color_normal f1fffc
set --global fish_color_command 8be9e1 --bold
set --global fish_color_keyword bbf7ef
set --global fish_color_param f1fffc
set --global fish_color_quote bbf7ef
set --global fish_color_redirection 8be9e1
set --global fish_color_end 8be9e1
set --global fish_color_operator 8be9e1
set --global fish_color_escape a8d8d4
set --global fish_color_comment 9fbfbd --italics
set --global fish_color_autosuggestion 9fbfbd
set --global fish_color_error ffb7c5
set --global fish_color_match 8be9e1 --bold
set --global fish_color_valid_path --underline
set --global fish_color_history_current --bold
set --global fish_color_cancel --reverse

# 默认 Fish 提示符与搜索/选中状态。
set --global fish_color_cwd 8be9e1
set --global fish_color_cwd_root ffe1a8
set --global fish_color_user bbf7ef
set --global fish_color_host a8d8d4
set --global fish_color_host_remote ffe1a8
set --global fish_color_status ffb7c5
set --global fish_color_selection --background=8be9e1 14353b
set --global fish_color_search_match --background=29494f f1fffc

# 自动补全列表：亮青背景配深青文字，保持清晰对比。
set --global fish_pager_color_progress --background=8be9e1 14353b
set --global fish_pager_color_prefix 8be9e1 --bold
set --global fish_pager_color_completion f1fffc
set --global fish_pager_color_description a8d8d4
set --global fish_pager_color_selected_background --background=8be9e1
set --global fish_pager_color_selected_prefix 14353b --bold
set --global fish_pager_color_selected_completion 14353b
set --global fish_pager_color_selected_description 14353b

# 如果使用 Pure 提示符，也沿用同一亮色色板；不切换提示符。
set --global pure_color_primary 8be9e1
set --global pure_color_info bbf7ef
set --global pure_color_mute 9fbfbd
set --global pure_color_normal f1fffc
set --global pure_color_light f1fffc
set --global pure_color_dark 14353b
set --global pure_color_success b8efcf
set --global pure_color_warning ffe1a8
set --global pure_color_danger ffb7c5
set --global pure_color_git_branch 8be9e1
set --global pure_color_git_dirty ffe1a8

# Fish 内置 Git 提示符保留状态含义，不改变显示内容。
set --global __fish_git_prompt_color_branch 8be9e1
set --global __fish_git_prompt_color_dirtystate ffe1a8
set --global __fish_git_prompt_color_stagedstate b8efcf
set --global __fish_git_prompt_color_invalidstate ffb7c5

# ls 实际使用 eza：不仅修改 Fish 命令行，也给子进程导出真彩色。
# LS_COLORS 同时适用于 GNU ls --color=auto；普通文件和目录统一亮青系。
set --global --export LS_COLORS (string join : \
    'rs=0' \
    'fi=38;2;187;247;239' 'di=1;38;2;139;233;225' \
    'ln=38;2;168;216;212' 'ex=1;38;2;139;233;225' \
    'pi=38;2;187;247;239' 'so=38;2;168;216;212' \
    'bd=38;2;255;225;168' 'cd=38;2;255;225;168' \
    'or=1;38;2;255;183;197' 'mi=1;38;2;255;183;197' \
    'su=1;38;2;255;225;168' 'sg=1;38;2;255;225;168' \
    'st=38;2;139;233;225' 'ow=38;2;139;233;225' 'tw=38;2;139;233;225')

# reset 清除 eza 自带的扩展名颜色，防止图片/源码等继续使用旧的蓝紫色。
set --global --export EZA_COLORS (string join : reset $LS_COLORS \
    'ur=38;2;187;247;239' 'uw=38;2;168;216;212' 'ux=1;38;2;139;233;225' \
    'ue=38;2;139;233;225' 'gr=38;2;187;247;239' 'gw=38;2;168;216;212' \
    'gx=38;2;139;233;225' 'tr=38;2;187;247;239' 'tw=38;2;168;216;212' \
    'tx=38;2;139;233;225' 'su=38;2;255;225;168' 'sf=38;2;255;225;168' \
    'sn=38;2;187;247;239' 'sb=38;2;168;216;212' \
    'uu=38;2;187;247;239' 'un=38;2;168;216;212' 'uR=38;2;255;225;168' \
    'gu=38;2;168;216;212' 'gn=38;2;168;216;212' 'gR=38;2;255;225;168' \
    'da=38;2;168;216;212' 'xx=38;2;159;191;189' 'hd=1;38;2;139;233;225' \
    'lc=38;2;168;216;212' 'lm=38;2;168;216;212' 'lp=38;2;168;216;212' \
    'xa=38;2;168;216;212' 'in=38;2;168;216;212' 'bl=38;2;168;216;212' \
    'df=38;2;168;216;212' 'ds=38;2;168;216;212' 'sp=38;2;187;247;239' \
    'im=38;2;187;247;239' 'vi=38;2;187;247;239' 'mu=38;2;187;247;239' \
    'lo=38;2;187;247;239' 'cr=38;2;187;247;239' 'do=38;2;187;247;239' \
    'co=38;2;187;247;239' 'tm=38;2;168;216;212' 'cm=38;2;187;247;239' \
    'bu=38;2;187;247;239' 'sc=38;2;187;247;239' 'ic=38;2;139;233;225' \
    'ga=38;2;184;239;207' 'gm=38;2;255;225;168' 'gd=38;2;255;183;197' \
    'gv=38;2;139;233;225' 'gt=38;2;255;225;168' 'gi=38;2;159;191;189' \
    'gc=1;38;2;255;183;197' 'bO=1;38;2;255;183;197')
