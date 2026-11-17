[中文](README.md) | [English](README.en.md)

# 个人终端与桌面配置

面向这台 Linux 工作环境的配置集合，按 GNU Stow 包组织。包含 Fish、tmux、foot、Helix、Niri、Yazi、Zellij，以及包管理脚本和本地 Pi 显示补丁。

## 使用

先检查目标位置已有的文件，再模拟链接需要的包：

```sh
cd ~/dotfiles
stow --simulate --target="$HOME" fish foot
stow --target="$HOME" fish foot
```

只链接需要的包，不使用 `--adopt` 覆盖已有配置。个人路径、Fish universal 变量和运行状态不纳入版本控制，具体规则见 `.gitignore`。

## tmux 按键切换

使用 `stow --target="$HOME" tmux` 链接配置。默认由 tmux 处理自定义 Alt 快捷键；在 Fish 中执行 `tmkeys fish` 交给当前程序，执行 `tmkeys tmux` 恢复，`tmkeys status` 查看当前窗格模式。

## 文档

- [配置与使用笔记](Config.md)
- [Fish 函数说明](fish/.config/fish/functions/函数说明.md)
- [开发约定](AGENTS.md)
- [路线图](READMAP.md)
- [Pi 显示补丁](pi-ui/README.md)
