# 开发约定

## 目录

- 各配置包按家目录布局组织，例如 `fish/.config/fish/`、`foot/.config/foot/`。
- `tmux/.tmux.conf`：按窗格切换的 Alt 绑定；`tmkeys.fish` 是对应 Fish 入口。
- `package-tools/`：软件包选择、安装和卸载脚本。
- `pi-ui/`：本地 Pi 启动器与显示补丁。
- `tests/`：离线回归测试。
- `Config.md`：现有配置说明；保留已有内容，按功能补充。

## 修改规则

- 先检查实际配置、符号链接、相关文档和 Git 状态，再修改。
- 保留用户已有改动，仅提交当前任务涉及的文件。
- 不提交个人凭证、历史记录、缓存或 `.gitignore` 中的本地配置。
- Fish 函数按函数名放入 `functions/`，不为新增功能改写含个人路径的 `config.fish`。
- Shell 参数保持独立传递，避免 `eval`；失败返回非零状态，不伪报成功。
- tmux 验证使用临时独立 socket，不在测试中关闭或发送按键到日常服务器。
- 启用 Stow 包前先执行 `stow --simulate`，不直接使用 `--adopt`。
- README 中英文同步维护；功能说明使用简短文字和表格。

## 验证

在仓库根目录按修改范围执行：

```sh
python3 -B tests/test_tmkeys.py -v
python3 -B tests/test_package_tools.py
python3 -B tests/test_yazi_documents.py -v
node --test tests/test_pi_ui.mjs
```

Python 测试优先使用标准库，运行时加 `-B`，不向仓库写入字节码缓存。新增功能应提供对应的离线回归测试。
