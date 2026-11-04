# 配置笔记

## 包管理

- `pacman -Ss 关键字` — 搜索软件
- `sudo pacman -S 关键字` — 安装软件
- `sudo pacman -S yay` — 安装 AUR 助手

### yay（AUR）

- `yay -S mihomo-party-bin`
- `yay -S wechat-bin`

### 交互式安装与卸载（aur / pac / uninstall）

三个命令由 `package-tools` Stow 包管理，对应 `~/.local/bin/aur`、`pac` 和 `uninstall`，共用 `package-tools/.local/libexec/package-tools/common.bash`。

```bash
aur                 # 搜索并安装 AUR 包
pac                 # 搜索并安装官方/已配置仓库中的包
uninstall           # 从手动安装的包中选择卸载
aur 浏览器           # 可选：预填搜索关键词
pac --help
```

- 配色参考 [青.md](青.md) 的亮色：月白 `#EBF5F7`、浅青 `#BEE7E3`、碧青 `#A7DFDB`；失败/警告保留红黄状态色。
- 软件包列表从顶部开始，支持搜索、Tab 多选、Enter 确认、Esc 取消；窄终端的预览自动移到底部。
- `Alt+P` 切换预览，`Alt+J/K` 滚动，`Alt+D/U` 半页滚动；AUR 的 `Alt+B`（小写 b）预览 PKGBUILD，`Alt+Shift+B` 返回包信息。
- 列表载入和数据库核验使用青色色块动画。事务通过 PTY 保留真实终端交互，可识别的 pacman 普通/吃豆进度条替换为青色色块；不改变全局 `/etc/pacman.conf`，不影响直接运行的 pacman/yay。
- 下载使用青色，AUR 构建提示用紫色，检查用浅蓝，安装/成功用绿色，卸载/警告用琥珀色，错误用红色；同时保留阶段名称与符号。构建日志正常透传，不伪造百分比，也不额外提示“无可用百分比”。
- 执行前显示所选包数量与来源；第二步不额外输出操作说明。密码、最终事务清单、确认和 PKGBUILD 审阅均由原包管理器处理。未知或跨读取边界的输出原样透传，不隐藏错误。
- 安装成功必须同时满足：安装命令退出码为 0，且 `pacman --color never -Q` 查询成功、所选包都确实存在。显示实际安装版本，但不代替各软件的运行功能测试。
- 卸载成功必须同时满足：卸载命令退出码为 0，且完整本地数据库查询成功、所选包都已不存在。数据库查询报错不会被误判为“卸载成功”。
- 取消、权限失败、部分成功、残留包等情况分别提示；失败返回非零退出码，不再无条件打印成功。
- 不再使用 `--noconfirm`、失效的 Omarchy 脚本或后台 sudo 保活，也不把 `updatedb` 的结果当成安装结果。
- `PACKAGE_TOOLS_ANIMATION=0` 关闭加载动画；`PACKAGE_TOOLS_PROGRESS=0` 绕过 PTY 进度适配；`NO_COLOR=1` 关闭颜色。非终端输出使用静态状态提示并直接运行原包管理器，缺少 Python 3 时也自动回退。
- 只调整这三个命令各自的界面，原 Alt+I 小菜单的顺序和布局本次未修改。

离线回归测试（使用临时 mock，不会真的安装、卸载或请求 sudo 权限）：

```bash
python3 -B tests/test_package_tools.py
```

---

## 软件安装

- `sudo pacman -S jdk17-openjdk` — Java 17 版本
- `sudo pacman -S maven` — Maven 包管理工具
- `yay -S wps-office-365` — 完整的 Arch Linux 版 WPS
- `yay -S gitui` — 终端 Git 工具
- `sudo pacman -S stow` — 符号链接管理工具，用于管理 dotfiles（配置文件）或软件包
- `yay -S opencode` — 代码 Agent
- `yay -S zen-browser/helium` — 浏览器
- uv 与 Posting：

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv tool install posting
  ```
- `sudo pacman -S fcitx5-im fcitx5-chinese-addons` — 输入法核心组件与中文支持
- `sudo pacman -S qt5-base qt5-wayland` — XWayland 兼容层（允许 X11 应用在 Wayland 下运行）
- `rustdesk-server-bin`
- `rustdesk-bin`

> **XWayland** 是一个**兼容层**，允许原本为 X11 编写的应用程序在 Wayland 环境下正常运行。

---

## GNOME 设置

```bash
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
```

---

## Niri

```bash
niri msg windows
```

### 亮青活动窗口边框

配置文件：`niri/.config/niri/cfg/layout.kdl`。活动窗口的焦点边框使用亮青 `#8be9e1`，比原湖青更明亮，与 Fish / Yazi 的强调色一致；不改变原有线宽、布局、圆角或快捷键。

```kdl
layout {
    focus-ring {
        on
        active-color "#8be9e1"
    }
}
```

以上仅展示配色片段，应放入现有的 `layout` 块，不要覆盖整个配置文件。修改后校验并重载：

```bash
niri validate -c ~/.config/niri/config.kdl
niri msg action load-config-file
```

---

## SDDM（登录管理器）

```bash
yay -S sddm-astronaut-theme
```

编辑 `/etc/sddm.conf`：

```ini
[Theme]
Current=sddm-astronaut-theme

# 可选：设置背景图片（主题有自己的背景，可以不设置）
# Background=/usr/share/sddm/themes/sddm-astronaut-theme/Backgrounds/background.jpg

[Users]
# 可选：显示所有用户（默认行为）
HideUsers=false

[General]
# 可选：设置键盘布局
Numlock=on
```

---

## Fcitx5 输入法

### 环境变量（Fish）

```fish
set -gx GTK_IM_MODULE fcitx
set -gx QT_IM_MODULE fcitx
set -gx XMODIFIERS @im=fcitx
```

---

## Git 配置

```bash
# 设置用户名和邮箱
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱@example.com"

# 验证是否设置成功
git config --global --list

# 设置全局凭证存储
git config --global credential.helper store

# 任意执行一次 git push，输入用户名和 Token 后会自动保存
git push
```

---

## Fish Shell 配色（亮青）

### Niri / Fish / Yazi / ls 统一亮色色板

以原青色系为基础整体提亮，使用真彩色而非终端的 `brcyan` / `brblue`。这里的「亮色」指更明亮的文字、图标和强调色，不是把桌面或终端换成白底主题。

| 用途 | 色值 |
| --- | --- |
| 主强调色：亮青 | `#8be9e1` |
| 辅助色：浅青 | `#bbf7ef` |
| 次要信息：柔青 | `#a8d8d4` |
| 正文：亮青白 | `#f1fffc` |
| 亮色选中背景上的深青文字 | `#14353b` |
| 注释、自动建议、分隔线 | `#9fbfbd` |
| 成功、复制状态 | `#b8efcf` |
| 警告、待处理状态 | `#ffe1a8` |
| 错误、剪切状态 | `#ffb7c5` |

亮青背景搭配深青文字的对比度约为 **9.26:1**。终端原有深色/透明背景不变；深青仅用于亮色背景上的文字，错误和警告仍保留独立颜色。

### 配置与生效

配色文件：`fish/.config/fish/conf.d/qing-theme.fish`。Fish 交互式启动时自动加载，无需改动含个人路径的 `config.fish`，也无需把本地 `fish_variables` 纳入 Git。

- 命令、操作符、当前目录、Git 分支使用亮青；普通文字使用亮青白。
- 引号、次要提示和自动建议同步提亮；补全列表选中项为亮青底、深青字。
- 同时设置默认 Fish、Pure 和内置 Git 提示符颜色，不安装或切换提示符。

在**当前 Fish 终端**执行以下命令立即刷新，新终端会自动加载：

```fish
source ~/.config/fish/conf.d/qing-theme.fish
```

该文件中的全局变量优先于旧的 universal 配色。以后应编辑该文件，不要只运行旧的 `set -U ... brblue`。Fish 十六进制颜色不带 `#`，例如：

```fish
set --global fish_color_command 8be9e1 --bold
set --global fish_color_param f1fffc
set --global fish_color_selection --background=8be9e1 14353b
```

### ls / eza 输出配色

当前 `ls` 是 `eza -l --sort=extension --group-directories-first` 的别名，不能只修改 Fish 语法高亮来改变文件列表颜色。

同一个配色文件导出 `LS_COLORS` 和 `EZA_COLORS`：

- 目录、可执行文件和图标使用亮青，普通文件使用浅青。
- 权限、大小、用户/组、日期等长列表字段也采用青色系。
- 使用 `EZA_COLORS` 的 `reset` 清除内置扩展名配色，防止部分文件仍呈蓝紫色。
- 断链、危险状态和 Git 冲突保留浅红色；需要注意的权限/状态保留暖黄色。
- `LS_COLORS` 同时可供 GNU `ls --color=auto` 使用。

重新 source 配色文件后直接运行 `ls` 即可，不改变现有排序和别名。

---

## Yazi 配色（亮青）

配置文件：`yazi/.config/yazi/theme.toml`，使用 **Yazi 26.9.1** 的配置格式。

- 保留透明背景，正文、目录、面板边框、次要文字和各状态指示器整体提亮。
- 当前文件、活动标签和正常模式使用亮青底、深青字；选择模式使用浅青。
- 语言/工具图标在保留大致色相的同时提亮，避免旧的暗色图标不清晰。
- 光标行放在 `[indicator]`，模式指示器放在 `[mode]`，不使用旧的 `mgr.hovered`。

退出并重新打开 Yazi 即可生效，无需重启桌面。文件操作快捷键不变。

### 终端图片查看器：timg

电脑已安装 **timg 1.6.3**，但系统版本依赖旧 FFmpeg 的 `libavformat.so.62` 等库，与当前 FFmpeg 不兼容，无法启动。

本次复用了本机已有的 AUR 缓存源码，核对了 PKGBUILD 中的 SHA-256，并从上游 timg 1.6.3 源码构建**仅图片版本**，关闭 FFmpeg/视频解码依赖。没有额外下载其他 AUR 查看器，也没有替换、降级或乱建系统库软链接。

- 图片专用二进制：`~/.local/libexec/timg-images`。
- 便捷命令：`~/.local/bin/timg`，链接到上述二进制。
- 系统的 `/usr/bin/timg` 保留不动；本地版本不负责视频，视频仍使用原来的 Celluloid。
- 支持终端图形协议自动检测，包括 Foot 的 Sixel；不支持图形协议时可回退为 Unicode 彩色块。

检查本地版本：

```bash
~/.local/bin/timg --version
~/.local/bin/timg -I --frames=1 -- "图片.jpg"
```

Yazi 配置位于 `yazi/.config/yazi/yazi.toml`。`scripts/view-image.sh` 是兼容入口，实际由同目录的 `view-image.py` 负责终端输入与恢复，使用系统已有的 Python 3 标准库：

- PNG、JPEG、WebP、GIF、BMP、TIFF、SVG、AVIF、ICO、QOI 等图片按 MIME/扩展名匹配 timg。
- 选中图片按 **Enter** 或 **o** 查看，再按一次 **Enter** 直接返回 Yazi；正常看图时没有文字提示。
- opener 使用 `%s1`，一次只打开当前/首张图片，不再逐张轮播多选列表。
- 直接读取实际终端，兼容 CR/LF、Kitty/CSI-u 和 xterm 的 Enter 编码，忽略 Enter 松键事件。
- 看图使用独立备用屏幕，返回时清除图像并恢复终端状态，避免 Sixel/图片残留遮挡 Yazi。
- 不执行 `ya emit quit`，不关闭 Yazi。动图显示首帧，右侧预览仍由 Yazi 内置预览器负责。
- 文件名作为独立参数传递，并使用 `--` 分隔选项，兼容空格、中文和以短横线开头的文件名。

本次修改前的私有备份位于 `~/.local/state/dotfiles-theme-backups/`，不在 dotfiles 仓库内。

---

## Yazi：PDF / Word 终端阅读与预览

配置位于 `yazi/.config/yazi/`，适配 Yazi 26.9.1。PDF 使用内置 `pdftoppm` 页面预览；Word 使用 `piper` 加 `pandoc` / `antiword` 文字预览，不依赖 LibreOffice，也不声称保留 Word 的原始分页和图片。

| 格式 | Enter / o 打开 | 右侧预览 | O / Shift+Enter 备用方式 |
| --- | --- | --- | --- |
| PDF | `tdf` 终端页面阅读 | Yazi 内置页面预览 | 文字阅读（`pdftotext + less`）、Zathura 图形窗口 |
| DOCX | `doxx` 终端阅读 | `pandoc` 提取文字 | `pandoc + less` 文字阅读 |
| 老式 DOC | `antiword + less` 文字阅读 | `antiword` 提取文字 | 同默认方式 |

- `Alt+↑` / `Alt+↓` 向上、向下滚动预览；PDF 的单位是页。原有文件导航和图片查看方式不变。
- 终端阅读器使用 `block = true`，退出后返回 Yazi；Zathura 使用 `orphan = true`，独立窗口不阻塞文件管理器。
- 每次只打开当前/首个选中文件；文件参数由 Yazi 的 `%s1` 转义，不额外套引号。MIME 使用 `mime` 匹配，扩展名使用 `url` 兜底；不把 XLSX/PPTX 交给 doxx。
- `scripts/document-text.py` 共用于文字预览和分页阅读，使用 Python 标准库；传入绝对路径，兼容空格、中文和短横线开头的文件名。
- 文字转换成功后才启动 less；临时文件自动移除，不记录 less 历史。扫描 PDF 没有可提取文字时，使用 tdf 看页面，若需文字搜索则先 OCR。
- DOCX 预览是文字视图；复杂表格、图片、公式和版面以原文档为准，不能当作 Word 的完整替代。

### 依赖安装与插件恢复

通过 yay 安装 AUR 的 `tdf-git` 和作者维护的 `doxx-bin`，后者直接校验并打包上游二进制，避免不必要的完整编译。`antiword` 只有官方仓库包，仍可由 yay 安装。两个阅读器提供的命令仍叫 `tdf` / `doxx`。

```bash
yay -S --needed tdf-git doxx-bin antiword
# 新电脑还需要：Python、less、poppler（pdftoppm / pdftotext）、pandoc。
# 本机已有 pandoc-bin；不要为了恢复配置再额外安装冲突的 pandoc 包。

# Stow 链接配置后，按 package.toml 恢复锁定版本的 piper：
ya pkg install

pacman -Q tdf-git doxx-bin antiword
```

`doxx-bin` 当前为 0.1.4：TUI 图片仍是占位显示，不能当作 Word 的完整页面渲染器。

`package.toml` 纳入 Git，插件下载目录 `plugins/` 保留本地并忽略；不提交下载缓存和构建产物。

无需安装/卸载软件的离线回归测试：

```bash
python3 -B tests/test_yazi_documents.py -v
```

测试包含 MIME/扩展名路由、终端阻塞模式、插件锁定、文件名转义、转换失败处理，以及本机 pandoc / Poppler 的真实 DOCX 文字提取与 PDF 渲染。

本机已确认安装 `tdf-git 20260815.r155.de00504-1`（tdf 0.5.0）、`doxx-bin 0.1.4-1` 和 `antiword 0.37-12`。全部 41 项回归测试通过；另在真实 Foot 窗口中自动验证了 PDF / DOCX / DOC 从 Yazi 按 Enter 打开、退出阅读器并返回 Yazi，包含中文、空格、单引号和短横线开头的文件名。终端集成验证使用生成的 PDF / DOCX 和 antiword 上游公开 DOC 样例，不读取个人文档。

退出并重新打开 Yazi 生效。

---

## Pi：透明背景与彩色四角框

实现说明见 [pi-ui/README.md](pi-ui/README.md)。`pi-ui` 是独立 Stow 包：本地启动器优先于原版 `pi`，加载版本受控的 JavaScript 显示补丁，再使用安装包自带的未压缩入口；不重新编译、不修改 Pi 安装文件。

- 主题：`.pi/.pi/agent/themes/myTheme.json`。消息、工具、选择和搜索背景恢复终端默认色，保留 Foot 的透明配色。
- 补丁：`pi-ui/.local/lib/pi-ui/`。对话区统一四角框，亮青为主，命令蓝、思考/摘要紫、读取浅蓝、编辑浅绿、警告黄、错误红。
- 用户/回答/思考/工具/命令/摘要/技能及通知均覆盖；输入框、页脚和设置菜单不套消息角框。
- 不修改模型思考强度，也不强制隐藏思考；原来的折叠、展开和鼠标操作保留。
- 已验证 Pi 1.4.0 / 1.5.0，未知版本自动回退原版；升级后角框消失时先核对版本，再适配并重启 Pi，不删除版本保护。打印、JSON、RPC、重定向与包管理命令也走原版入口。

```bash
cd ~/dotfiles
mkdir -p ~/.local/lib
stow --target="$HOME" pi-ui
pi -c                                  # 退出旧 Pi 后，重新启动并继续最近会话
PI_UI_DISABLE=1 pi                     # 临时绕过显示补丁
PI_UI_DISABLE=1 pi --use-theme dark    # 同时临时使用内置主题
node --test tests/test_pi_ui.mjs
```

原主题备份在 `~/.local/state/pi-ui-backups/`。卸载启动器：`stow --delete --target="$HOME" pi-ui`；主题是否恢复应另行比较备份，不覆盖后续改动。

---

## Stow 使用

### 当前新增的管理项

```bash
cd ~/dotfiles
stow --simulate --target="$HOME" package-tools noctalia
stow --target="$HOME" package-tools noctalia
```

- `package-tools/.local/bin/{aur,pac,uninstall}` 链接到 `~/.local/bin/`；共用逻辑位于 `~/.local/libexec/package-tools/`。
- `noctalia/.config/noctalia/` 链接到 `~/.config/noctalia/`。此机器的完整目录仍保留，但 Git 只记录检查过的 `colors.json` 和 `colorschemes/`。
- Noctalia 的个人 `settings.json`、插件状态/下载内容及其他未审查配置保持忽略；当前 v5 的 GUI 设置在 `~/.local/state/noctalia/settings.toml`，此次未迁移或提交。
- 若目标位置已有真实文件，先备份并核对，再迁入对应 Stow 包；不要直接用 `--adopt` 覆盖仓库中不同的配置。
- 本次原始包管理脚本备份位于 `~/.local/state/package-tools-backups/`，不在 Git 仓库内。

### 1. 创建包结构

```bash
cd ~/dotfiles
mkdir nvim git zsh

# 在包内按家目录结构放文件
nvim/.config/nvim/init.lua
git/.gitconfig
zsh/.zshrc
```

### 2. 常用命令

```bash
# 创建符号链接（安装）
stow nvim                    # 只链接 nvim 包
stow nvim git zsh            # 链接多个包
stow .                      # 链接当前目录下所有包（谨慎使用）

# 模拟运行（查看将做什么，不实际执行）
stow --simulate nvim
stow -n nvim                # 简写

# 删除符号链接
stow --delete nvim
stow -D nvim                # 简写

# 重新链接（先删除再创建）
stow --restow nvim
stow -R nvim                # 简写

# 详细输出
stow --verbose nvim
stow -v nvim                # 简写，可以 -vv 更详细
```

---

## RustDesk 远程控屏

下载 `rustdesk-bin` 和 `rustdesk-server-bin`。

### 启动服务

```bash
# 查看包安装了哪些文件
pacman -Ql rustdesk-server-bin

# 先查看服务文件内容（确认配置）
cat /usr/lib/systemd/system/rustdesk-server-hbbs.service
cat /usr/lib/systemd/system/rustdesk-server-hbbr.service

# 启动
sudo systemctl start rustdesk-server-hbbs
sudo systemctl start rustdesk-server-hbbr

# 设置开机自启
sudo systemctl enable rustdesk-server-hbbs
sudo systemctl enable rustdesk-server-hbbr

# 查看状态
sudo systemctl status rustdesk-server-hbbs
sudo systemctl status rustdesk-server-hbbr
```

### 配置 hbbs 的 IP 参数

修改服务文件（推荐）

```bash
# 编辑 hbbs 服务
sudo -E EDITOR=helix systemctl edit --full rustdesk-server-hbbs

# 找到 ExecStart= 这一行，原本可能是：
ExecStart=/opt/rustdesk-server/hbbs

# 改成（ip addr show 查看实际的 IP 并替换）：
# 服务文件默认可能没有 -r 参数，需要手动添加你的局域网 IP。
ExecStart=/opt/rustdesk-server/hbbs -r 192.168.1.123:21117
# 21117 是 RustDesk 服务器中继服务（hbbr）的默认端口。
```

### 重新加载并重启

```bash
sudo systemctl daemon-reload
sudo systemctl restart rustdesk-server-hbbs
sudo systemctl restart rustdesk-server-hbbr
```

### 获取 Key

```bash
# Key 文件在 /opt/rustdesk-server/data/ 目录下
sudo cat /opt/rustdesk-server/data/id_ed25519.pub
```

---

## 蓝牙配置

### 1. 检查蓝牙硬件是否存在

```bash
lsusb | grep -i bluetooth
```

### 2. 检查蓝牙服务状态

```bash
systemctl status bluetooth
```

### 3. 检查蓝牙控制器状态

```bash
bluetoothctl show
```

状态是 **`Powered: no`** 和 **`PowerState: off-blocked`** 的话，说明蓝牙被软封锁（soft blocked）了，执行以下命令启用：

```bash
rfkill unblock bluetooth
```

---

## Arch Linux《博德之门 3》MOD 安装指南

本指南使用 `protontricks` 在游戏的 Proton 容器（Prefix）中运行 Windows 版 **BG3 Mod Manager (BG3MM)**，这是目前在 Linux 下管理《博德之门3》MOD 最稳定、兼容性最好的方案。

### 第一步：系统环境准备

在 Arch Linux 终端中安装必要组件 `protontricks`（用于让 Windows 程序识别 Steam 游戏瓶）：

```bash
sudo pacman -S protontricks
```

### 第二步：下载核心软件与依赖

你需要前往以下网站下载管理工具及必备环境：

#### 1. 下载 BG3 Mod Manager

- **官方下载地址**：[GitHub - LaughingLeader/BG3ModManager](https://github.com/LaughingLeader/BG3ModManager)
- **操作**：下载最新版本的 `.zip` 压缩包，并解压到你习惯的目录（例如 `~/Games/BG3MM/`）。

#### 2. 下载 .NET Desktop Runtime 8.0（关键环境）

BG3MM 是 Windows 桌面程序，需要微软的桌面运行时支持。**请勿使用 winetricks 脚本安装，直接下载微软官方独立安装包：**

- **官方下载直链**：[Microsoft .NET Desktop Runtime 8.0.x (x64)](https://www.google.com/search?q=https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/runtime-desktop-8.0.12-windows-x64-installer)

### 第三步：安装环境与启动管理器

#### 1. 安装 .NET 桌面环境

打开终端，切换到你下载微软 `.exe` 安装包的目录，将其安装进《博德之门3》的 Steam 容器中（游戏 AppID 为 `1086940`）：

```bash
protontricks-launch --appid 1086940 windowsdesktop-runtime-8.0.12-win-x64.exe
```

*在弹出的标准 Windows 安装界面中，一路点击 **Install** 直至完成。*

#### 2. 启动 BG3 Mod Manager

使用以下命令启动管理器（请将路径替换为你实际解压的路径）：

```bash
protontricks-launch --appid 1086940 /path/to/BG3ModManager.exe
```

> 💡 **游戏路径确认**：打开软件后，点击 `Settings` -> `Preferences`，确保路径正确（通常会自动识别）：
>
> - **Data Path**: `Z:\home\你的用户名\.local\share\Steam\steamapps\common\Baldur's Gate 3\Data\`
> - **Executable Path**: `Z:\home\你的用户名\.local\share\Steam\steamapps\common\Baldur's Gate 3\bin\bg3.exe`


---

## Zathura

待补充。
