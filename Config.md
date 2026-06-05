



# 包管理

- `pacman -Ss 关键字` — 搜索软件
- `sudo pacman -S 关键字` — 安装软件
- `sudo pacman -S yay` — 安装 AUR 助手

## yay (AUR)

- `yay -S mihomo-party-bin`
- `yay -S wechat-bin`

---

# 软件安装

- `sudo pacman -S jdk17-openjdk` —java17版本
- `sudo pacman -S maven`—maven包管理工具
- `yay -S wps-office-365`—完整的archlinux的wps
- `yay -S gitui`—终端git
- `sudo pacman -S stow`—符号链接管理工具，用于管理 dotfiles（配置文件）或软件包
- `yay -S opencode`—代码agent
- `yay -S zen-browser/helium`—浏览器
- `curl -LsSf https://astral.sh/uv/install.sh | sh`
  `uv tool install posting`
- `sudo pacman -S fcitx5-im fcitx5-chinese-addons` — 输入法核心组件与中文支持
- `sudo pacman -S qt5-base qt5-wayland` — XWayland 兼容层（允许 X11 应用在 Wayland 下运行）
-  rustdesk-server-bin
-  rustdesk-bin

> **XWayland** 是一个**兼容层**，允许原本为 X11 编写的应用程序在 Wayland 环境下正常运行。

---

# GNOME 设置

```bash
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
```

---

# Niri

```bash
niri msg windows
```

---

# SDDM（登录管理器）

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

# Fcitx5 输入法

## 环境变量 (fish)

```fish
set -gx GTK_IM_MODULE fcitx
set -gx QT_IM_MODULE fcitx
set -gx XMODIFIERS @im=fcitx
```

---

# Git 配置

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

# Fish Shell 配色

## 基本颜色（亮色系）

- `set -U fish_color_command brwhite`        # 命令为亮白色
- `set -U fish_color_param brcyan`           # 参数为亮青色
- `set -U fish_color_error brred`            # 错误为亮红色
- `set -U fish_color_quote bryellow`         # 引号内容为亮黄色
- `set -U fish_color_redirection brwhite`    # 重定向符号为亮白色
- `set -U fish_color_end brgreen`            # 结束符（如 done, end）为亮绿色
- `set -U fish_color_operator brcyan`        # 操作符为亮青色
- `set -U fish_color_escape brblue`          # 转义符为亮蓝色

## Prompt 颜色（覆盖 Pure 主题）

- `set -U pure_color_primary brblue`         # 当前目录为亮蓝色
- `set -U pure_color_success brgreen`        # 成功提示为亮绿色
- `set -U pure_color_warning bryellow`       # 警告为亮黄色
- `set -U pure_color_danger brred`           # 危险/错误为亮红色
- `set -U pure_color_info brcyan`            # 信息为亮青色
- `set -U pure_color_mute brblack`           # 次要信息为亮黑色（灰色）
- `set -U pure_color_normal brwhite`         # 正常文字为亮白色
- `set -U pure_color_light white`            # 亮色为纯白

## Git 相关颜色

- `set -U pure_color_git_branch bryellow`    # Git 分支为亮黄色
- `set -U pure_color_git_dirty brred`        # Git 脏状态为亮红色

## 自动补全颜色

- `set -U fish_color_autosuggestion d0d0d0`

## stow使用

1.创建包结构

```bash
cd ~/dotfiles
mkdir nvim git zsh

# 在包内按家目录结构放文件
nvim/.config/nvim/init.lua
git/.gitconfig
zsh/.zshrc
```

2.常用命令

```bash
# 创建符号链接（安装）
stow nvim                    # 只链接 nvim 包
stow nvim git zsh           # 链接多个包
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

## rustdesk远程控屏

下载rustdesk-bin和rustdesk-server-bin

####  启动服务

```bash
# 查看包安装了哪些文件
pacman -Ql rustdesk-server-bin

#先查看服务文件内容（确认配置）
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

#### 配置 hbbs 的 IP 参数

修改服务文件（推荐）

```bash
# 编辑 hbbs 服务
sudo -E EDITOR=helix systemctl edit --full rustdesk-server-hbbs

#找到 ExecStart= 这一行，原本可能是：
ExecStart=/opt/rustdesk-server/hbbs

#改成（ip addr show 查看实际的ip并替换）：
#服务文件默认可能没有 -r 参数，需要手动添加你的局域网 IP。
ExecStart=/opt/rustdesk-server/hbbs -r 192.168.1.123:21117
#21117 是 RustDesk 服务器中继服务（hbbr）的默认端口。

```

重新加载并重启

```bash
sudo systemctl daemon-reload
sudo systemctl restart rustdesk-server-hbbs
sudo systemctl restart rustdesk-server-hbbr
```

获取 Key

```bash
# Key 文件在 /opt/rustdesk-server/data/ 目录下
sudo cat /opt/rustdesk-server/data/id_ed25519.pub
```

## 蓝牙配置

### 1. 检查蓝牙硬件是否存在

```bash
lsusb | grep -i bluetooth
```

### 2. 检查蓝牙服务状态

```bash
systemctl status bluetooth
```

### 3.检查蓝牙控制器状态

```
bluetoothctl show
```

状态是 **`Powered: no`** 和 **`PowerState: off-blocked`**的话这说明蓝牙被软封锁（soft blocked）了，执行以下命令启用：

```
rfkill unblock bluetooth

```

