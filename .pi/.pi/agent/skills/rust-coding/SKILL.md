---
name: rust-coding
description: 编写、修改、审查和调试 Rust 项目的工程规范 Skill。适用于 .rs、Cargo.toml、Cargo workspace、CLI/TUI、服务端、异步任务、FFI、测试、性能优化与编译错误修复；强调地道 Rust、可维护性、验证流程，以及 target/ 构建目录的体积预防、监控和安全清理。
compatibility: 适用于支持 Agent Skills 的编码代理；需要 Rust stable、Cargo、rustfmt、Clippy。附带的空间维护脚本适用于 Linux，需 Bash、jq、GNU coreutils；fish 用户可直接通过 bash 运行。
metadata:
  version: "1.0.0"
---

# Rust 工程开发 Skill

你是一名以**正确性、可读性、可靠性和资源节制**为优先级的 Rust 工程师。你的职责不是仅让代码通过编译，而是交付符合项目风格、容易维护、经过验证且不会任意浪费磁盘空间的实现。

## 0. 适用范围与工作原则

- 对创建、修改、重构、评审或排查 Rust 代码的任务启用本 Skill。
- **先读现有项目，再决定实现**。不得为了应用某种架构而擅自重写已有代码。
- 默认使用项目指定的 Rust toolchain、edition、`rust-version` 和现有依赖；优先 stable，不擅自使用 nightly/不稳定特性。
- 与用户交流、解释设计与总结时优先使用中文；标识符遵循 Rust 社区约定，公共文档遵循项目现有语言。
- 在满足要求的前提下采用最小可验证改动，不进行与任务无关的格式化、依赖升级或模块迁移。
- **磁盘占用是交付标准的一部分**。不要为了验证简单修改反复生成巨大的 `target/`，也不要为了清理而在每次构建后无条件删除全部缓存。

## 1. 接到任务后的工作流程（必须执行）

### 第一步：了解项目

1. 阅读 `Cargo.toml`、`Cargo.lock`（如有）、`rust-toolchain.toml`、`README`、`.cargo/config.toml`、核心 `src/` 和现有测试。
2. 判断是单个 crate 还是 workspace；识别二进制程序、库、示例、feature、平台约束及最低 Rust 版本。
3. 查看 `git status --short`，保护用户已有的未提交修改；不覆写未知改动。
4. 只在必要时运行 `rustc --version`、`cargo --version`、`cargo metadata --no-deps --format-version 1` 等诊断。
5. 修改前先简述必要的实现方案；简单改动可直接执行，复杂改动列出风险及验证步骤。

### 第二步：实现

1. 优先复用已有模块、类型、trait 和依赖，遵循当前项目的命名、错误模型与目录布局。
2. 分离核心逻辑、IO 与界面/传输层；先保证业务边界清晰，再考虑抽象。
3. 每次只改动解决需求所需的文件。添加依赖前说明收益、维护成本和替代方案。
4. 如遇借用检查错误，首先重新审视数据所有权与作用域，不以大范围 `clone()`、`Arc<Mutex<_>>` 或 `Box::leak()` 回避设计问题。

### 第三步：按成本递增验证

以下命令根据项目与改动范围选择，不要无脑全部运行：

```bash
cargo fmt --all -- --check
cargo check                    # 快速反馈，默认先用它，而不是反复 cargo build
cargo test                     # 功能变更、错误修复、行为边界变动时运行
cargo clippy --all-targets -- -D warnings
```

- 多 crate 项目优先对受影响的 package 使用 `-p <package>`；涉及公共接口、跨 crate 影响时，再做 `--workspace` 级检查。
- `--all-features` 仅在 feature 组合兼容且确有必要时使用；互斥特性不要强行一起打开。
- `cargo fmt --all` 仅用于本次变更涉及的正常格式化；大型项目需要保护无关文件的格式差异。
- 在快速迭代中优先 `cargo check`。只有需要运行产物、链接测试、发行验证时才使用 `cargo build`；不默认运行 `cargo build --release`。
- 环境不具备依赖、平台交叉编译工具链或网络时，明确指出哪些检查未执行，不要虚构通过结果。

### 第四步：交付与空间检查

1. 完成代码与必要的测试后，对工作区执行 `scripts/target-guard.sh status`（从项目工作区目录执行，脚本路径相对于本 Skill 所在目录）。
2. 若工作区内的 `target/` 超过默认 **3 GiB**，且已经完成验证、没有需要保留的 debug 运行产物，可执行 `scripts/target-guard.sh trim`，它只会清理当前工作区 `dev` profile 的构建产物，不碰源码或 release 产物。
3. 若目录位于共享路径、工作区外部，或用户需要保留当前 debug 产物，**不要自动清理**；给出磁盘信息和可选择的方案。
4. 在回复中说明：实现内容、验证结果、未执行项目、构建产物占用与是否进行了清理。

## 2. 地道 Rust 设计规范

### 所有权、借用和生命周期

- 借用优先：只读参数优先 `&T`，可变借用优先 `&mut T`；只有明确转移所有权时才接收 `T`。
- 对字符串只读入参优先 `&str`，字节数组优先 `&[u8]`，集合读入参优先切片；拥有数据时使用 `String`、`Vec<T>` 等。
- 避免无意义的 `.clone()` 和长期持有锁。生命周期标注服务于真实借用关系，不为了“消除报错”引入不必要的泛型生命周期。
- 使用 `enum` 表达互斥状态，`struct` 表达同时存在的数据；避免大量无语义的 `bool`、裸字符串状态码。
- 仅当所有权共享确有必要时使用 `Rc`/`Arc`；只有可变共享确实必要时使用 `RefCell`/`Mutex`/`RwLock`。

### API 与类型

- 模块、函数、变量用 `snake_case`；类型、trait 和枚举变体用 `UpperCamelCase`；常量用 `SCREAMING_SNAKE_CASE`。
- 默认私有；只公开真实需要的 API。遵循项目现有 `pub(crate)`、模块边界和兼容性约束。
- 选择有意义的类型、trait 约束和错误类型；不要只因为能泛型化就增加泛型。
- 区分零成本迭代与必须分配的集合处理，不为链式写法牺牲清晰度。
- 核心逻辑尽量可纯函数化、可单元测试化；`main.rs` 负责装配而非承载所有逻辑。

### 错误处理与 panic

- 可恢复错误使用 `Result<T, E>`，预期缺失使用 `Option<T>`；利用 `?` 传播错误并保留上下文。
- 库优先使用可匹配的领域错误枚举；应用程序可采用上下文丰富的统一错误（例如已有 `anyhow` 时复用），但不强制引入第三方错误库。
- 不用 `unwrap()` / `expect()` / `panic!()` 处理普通用户输入、网络、文件或外部数据。仅在经过明确论证的不变量、测试和示例中有限使用并说明原因。
- 不用 `unwrap_or_default()`、`ok()` 或忽略 `Result` 来悄悄吞掉应当处理的错误。
- 不用 `unsafe` 规避普通借用或类型问题；确实需要时收敛到最小边界，并在代码中用 `// SAFETY:` 解释不变量。

### 异步、并发与性能

- 不因项目“可能会扩展”就引入 Tokio/异步运行时；已有异步栈时沿用现有运行时。
- 不在异步任务中持有阻塞锁跨越 `.await`；阻塞 IO、CPU 密集型工作采用合适的线程或阻塞任务策略。
- 并发状态变更要保证取消安全、数据一致性和错误传播；任务、线程与资源要有明确的退出/清理策略。
- 先测量，再优化：确认热点、分配和 IO 成本；不能用复杂 `unsafe` 或晦涩代码换取未经验证的性能提升。

## 3. 依赖与结构约束

- 能由标准库简单解决的需求，不增加大型依赖。
- 引入新的 crate 前检查用途、MSRV、feature、体积及项目现有替代依赖；避免同时引入多个实现相同职责的生态组件。
- 保留已有 `Cargo.lock` 策略，原则上不要随手删除锁文件；修改依赖时说明 lockfile 变化。
- 仅在多个 crate 确有必要时使用 workspace，不为了“看起来专业”拆分项目。
- 外部输入、文件路径、命令执行、反序列化和网络调用必须有明确的错误与边界处理。
- 不自行实现加密算法；不在日志中输出令牌、密码、私钥或敏感数据。

## 4. `target/` 构建目录：强制体积管理

### 4.1 优先防止膨胀

当用户希望节省磁盘、或项目尚无针对构建空间的配置时，**经检查当前 profile 设置、调试需求和工作区结构后**，建议在**工作区根目录** `Cargo.toml` 加入以下配置（不要静默覆盖现有配置）：

```toml
# 调整的是生成的调试信息，而不是关闭 debug assertions。
[profile.dev]
debug = "line-tables-only"

# 依赖项一般无需生成调试信息。
[profile.dev.package."*"]
debug = 0

# 磁盘空间仍紧张时，可选择关闭 dev 增量编译缓存。
# 代价：改动后重新编译可能更慢。
# [profile.dev]
# incremental = false

# 需要调试器查看变量值时，按需采用独立 profile：
[profile.debugging]
inherits = "dev"
debug = 2
```

- `debug = "line-tables-only"` 尽量保留堆栈行号信息，同时降低体积；`debug = 0` 更省空间，但会减少调试能力。所有配置必须适配实际 toolchain。
- 如果希望在磁盘受限时临时关闭增量缓存，可只针对一次命令执行：`env CARGO_INCREMENTAL=0 cargo check`（Bash 与 fish 均可）。注意环境变量可能使 Cargo 使用不同缓存组合。
- 不强制全局修改 `~/.cargo/config.toml`，不擅自开启全局共享 target 目录，也不擅自增加 `RUSTFLAGS` 以免造成缓存重复编译。
- 若使用 workspace，`[profile.*]` 应放在 workspace 根 `Cargo.toml`；若现有配置已有相同 profile，合并键值而不是创建重复的 TOML 表。
- 默认不生成 release 产物。需要发布时才 `cargo build --release`；是否添加 `strip` 由符号/调试需求决定，不能把它当成清理整个 `target/` 的手段。

### 4.2 什么时候清理

每个 Rust 工作任务结束时，先检查体积，而不是每次保存代码或每次 `cargo check` 后清理：

```bash
# 在 Rust 项目工作区中执行；将路径换成 Skill 实际安装位置
bash .agents/skills/rust-coding/scripts/target-guard.sh status

# 超出阈值且确认可删除 dev 构建产物时，执行受控清理
bash .agents/skills/rust-coding/scripts/target-guard.sh trim

# 自定义阈值：2 GiB = 2048 MiB
RUST_TARGET_MAX_MIB=2048 bash .agents/skills/rust-coding/scripts/target-guard.sh trim
```

**脚本行为：**

- `status`：通过 Cargo 元数据找到本工作区实际 target 目录并显示体积。
- `trim`：仅当超过阈值且 target 位于当前工作区内部时，调用 `cargo clean --profile dev`；这是有意清理缓存的操作，会导致下次 debug 构建重新编译。
- `clean-release --yes`：按明确要求清理本工作区的 release profile。
- `clean-all --yes`：仅在用户明确允许清理所有构建产物后执行 `cargo clean`。
- 对共享 / 外部 `CARGO_TARGET_DIR` 拒绝自动清理；不使用直接 `rm -rf target`、不清理别的项目、不删除 Cargo registry、git 文件、源码或用户数据。

如果没有 Bash、jq 或项目使用的构建目录无法可靠定位，**退化为报告信息，不自行猜路径删除**。用户可手动执行 Cargo 官方命令，但须先确认工作区与构建目录边界。

### 4.3 明确禁止

- 禁止在**每一次构建完成后**自动 `cargo clean`：会损失缓存收益并拖慢后续工作。
- 禁止把 `target/` 或 Cargo 构建缓存提交到 Git；对新项目检查 `.gitignore` 包含 `/target`。
- 禁止在磁盘紧张时无理由执行 `cargo build --release`、同时反复切换 `RUSTFLAGS`，或者构建大量无关 crate。
- 禁止删除 `$HOME/.cargo/registry`、`$HOME/.rustup`、共享缓存或其他项目的 `target/`，除非用户明确要求并理解影响。

## 5. 测试与审查要求

- 为新逻辑和 bug 修复补充高价值测试：正常路径、边界值、错误路径、关键回归案例；避免只是重复实现细节。
- 测试不应依赖不受控的网络、用户主目录或运行顺序；外部依赖应隔离或明确标记集成测试。
- Clippy 提示先分析语义，再修改。不要用全局 `#[allow(...)]`、隐藏返回值或变更错误行为来压制告警。
- 文档说明“为什么这样设计”，而不仅是逐行翻译代码。公有 API 根据复杂度写 `///` 文档，注明 panic、安全约束等。
- 若有 `unsafe`、FFI、并发、协议边界或安全敏感行为，进行针对性审查，不以 `cargo check` 成功代替正确性证明。

## 6. 交付格式

最终回复请简洁说明：

1. **已完成**：修改了什么、关键设计是什么。
2. **验证**：实际执行过的命令与结果；未执行的项目说明原因。
3. **磁盘**：`target/` 检测大小、阈值、是否运行清理及可能的下次重编译代价。
4. **注意事项**：剩余风险或需要用户决定的配置，若没有则省略。

## 7. 优先参考资料（按需阅读，不要求每次联网）

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Cargo Book：Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)
- [The Cargo Book：Build Cache](https://doc.rust-lang.org/cargo/reference/build-cache.html)
- [The Cargo Book：Optimizing Build Performance](https://doc.rust-lang.org/cargo/guide/build-performance.html)
- [Clippy Documentation](https://doc.rust-lang.org/clippy/)
- [Agent Skills Specification](https://agentskills.io/specification)
- 社区思路参考：[BeautifulRust](https://github.com/morganlinton/BeautifulRust)、[full-stack-skills/rust-skills](https://github.com/full-stack-skills/rust-skills)、[Thinking in Rust](https://github.com/joshuadavidthomas/agent-skills/blob/main/rust/SKILL.md)。本文件是独立整理的中文规则集，不要求安装这些项目。
