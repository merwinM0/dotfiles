> 中文阅读版，仅供人工参考。程序执行入口为同目录下的 `SKILL.md`（英文版）。示例代码与命令按原文保留。

# CLI 输出设计

**适用范围：** 为 CLI 工具设计终端输出，使用 chalk 配色、Unicode 符号、多种输出详细程度（面向用户、详细、静默、JSON），以及一致的文案风格规范。涵盖配色方案选择、状态指示符设计、输出报告函数架构、仪式感／叙事式输出变体和跨终端兼容性。适用于构建新的 CLI 输出报告模块、为现有工具添加温暖的叙事式输出、统一多个命令的输出，或在提供人类可读文本的同时设计机器可读的 JSON 输出。

**技能名称：** `design-cli-output`。**许可：** MIT。**原文允许的工具：** `Read Write Edit Bash Grep Glob`。

**元数据：** 作者 Philipp Thoss；版本 `1.0`；领域 `cli`；复杂度：基础（`basic`）；语言 TypeScript；标签：`cli`、`terminal`、`ux`、`chalk`、`unicode`。

为命令行工具设计一致、支持多种详细程度的终端输出。

## 何时使用

- 为 CLI 工具构建新的输出报告模块
- 在标准事务式输出之外，添加温暖或具有叙事性的输出
- 统一多个命令的输出格式
- 在人类可读输出之外，并行设计面向机器的 JSON 输出
- 为新的终端工具选择颜色、符号和输出详细程度

## 输入

- **必需：** CLI 工具名称及主要受众（开发者、运维人员、最终用户）
- **必需：** 需要格式化输出的命令
- **可选：** 是否需要“仪式感”或叙事式输出变体
- **可选：** 品牌约束（配色方案、语气）

## 操作流程

### 第 1 步：定义配色方案

使用 chalk 创建一个包含命名条目的配色对象。

**加载 chalk 时，必须提供无颜色回退实现。** 回退实现必须能够替代配色方案实际使用的每一种调用形式，而不只是原样返回传入的字符串：

```javascript
// A factory returns a *function*; a direct style returns a string. Enumerate
// this list against the installed chalk, not from memory — chalk 6 added the
// three underline* variants, and a list that omits them is wrong for those names.
const FACTORIES = new Set(['ansi256', 'bgAnsi256', 'bgHex', 'bgRgb', 'hex',
  'rgb', 'underlineAnsi256', 'underlineHex', 'underlineRgb']);

function makeChalkStub() {
  return new Proxy((text) => text, {
    get(target, prop) {
      if (prop === 'then') return undefined;   // must not be a thenable
      if (prop === 'level') return 0;          // no color support, truthfully
      if (typeof prop === 'symbol') return Reflect.get(target, prop);
      return FACTORIES.has(prop) ? () => makeChalkStub() : makeChalkStub();
    },
  });
}

let chalk;
try { chalk = (await import('chalk')).default; }
catch { chalk = makeChalkStub(); }
```

以下四个不变量必须成立；过于简化的存根实现往往会在其中某一点出错：

1. **代理目标必须可调用**——应使用 `(text) => text`，而不是 `{}`。链式调用（`chalk.bold.cyan('x')`）要求链上的每一层既支持属性访问，也支持函数调用。
2. **工厂方法必须返回函数。** `new Proxy({}, { get: () => (s) => s })` 能满足直接样式调用，却会破坏工厂调用：此时 `chalk.hex('#FF6B35')` 返回的是字符串 `'#FF6B35'`，继续调用它就会抛出 `TypeError: ... is not a function`。配色方案在模块加载时构建，因此这个回退实现会在导入阶段就让工具崩溃——恰恰发生在本应降级为纯文本的场景中。
3. **`then` 必须为 `undefined`。** 如果存根对所有属性都返回函数，`await chalk` 就会永久等待：运行时调用 `.then`，随后等待一个永远没人调用的回调。Node 会报告 `Detected unsettled top-level await`，并以退出码 13 结束。
4. **`level` 必须是数字。** 能力判断会读取 `chalk.level >= 1`；用真值冒充能力值的存根，会在实际不支持颜色的情况下错误地启用相关分支。

无论导入成功后得到真实 chalk，还是导入失败后得到回退对象，都应使用最终得到的对象构建配色方案。

**标准配色**（事务式输出）：

```javascript
// Status colors
const ok = chalk.green;       // success
const fail = chalk.red;       // errors
const warn = chalk.yellow;    // warnings
const info = chalk.cyan;      // identifiers, names
const dim = chalk.dim;        // secondary info, paths
const bold = chalk.bold;      // headers
```

**暖色配色**（仪式感／叙事式输出）：

```javascript
const C = {
  flame: chalk.hex('#FF6B35'),   // active elements, fire
  amber: chalk.hex('#FFB347'),   // arriving items, warm highlights
  spark: chalk.hex('#FFF4E0'),   // individual items (sparks/skills)
  ember: chalk.hex('#8B4513'),   // cold/dormant states
  warm:  chalk.hex('#D4A574'),   // neutral warm text
  dim:   chalk.dim,              // background, secondary
  fail:  chalk.red,              // errors stay red (honest)
};
```

配色设计规则：
- 始终提供无颜色回退实现，并按照配色方案实际使用的调用形式进行检查——上面的暖色配色几乎全部使用工厂方法
- 自定义配色使用十六进制颜色（`chalk.hex('#FF6B35')`）
- 无论配色主题如何，失败／错误颜色始终保持为红色
- 按语义角色而不是视觉外观命名配色条目
- 在模块之间共享一个存根，不要在每个导入位置重新实现，否则同一个缺陷需要在每份副本中分别发现和修复

**预期结果：** 得到一个包含命名条目的配色对象，以及一个已经实际执行验证、而非仅仅编写完成的回退实现。

**失败时：** 直接测试回退路径，不要等构建配色方案时才发现它已经损坏。在可以访问存根的作用域内执行：

```javascript
console.assert(chalk.dim('x') === 'x');            // direct style
console.assert(chalk.hex('#fff')('x') === 'x');    // factory — the usual defect
console.assert(chalk.bold.cyan('x') === 'x');      // chain
console.assert(chalk.level === 0);                 // capability gate stays shut
await chalk;                                       // must not hang
```

`NO_COLOR=1` 无法覆盖这种情况。它测试的是一个正常工作的 chalk 主动选择不输出转义序列的路径；回退实现测试的则是 chalk 导入失败的路径。两条路径不共享任何代码。带注释的生产用存根、缺陷复现，以及上述检查的可运行版本，见[扩展示例](references/EXAMPLES.md#step-1-the-no-color-chalk-fallback)。

### 第 2 步：选择状态指示符

选择用于传达状态的 Unicode 符号或 ASCII 字符：

**ASCII（兼容性最高）：**

```text
+  已创建／已安装（绿色）
-  已移除／已删除（红色）
=  已跳过／未变化（弱化显示）
!  错误／警告（红色）
```

**Unicode（表现更丰富，需要 UTF-8 终端）：**

```text
✦  条目／技能／修习（火星色 spark）
◉  活跃／燃烧状态
◎  冷却／余烬状态
○  冷却完毕／休眠状态
◌  可用／未安装
✗  失败条目
✓  成功（谨慎使用，并非所有终端都能良好渲染）
```

选择标准：
- 在 CI 或管道环境中运行的工具使用 ASCII
- 面向交互式终端用户的工具使用 Unicode
- 通过 `--ascii` 标志或检测 `NO_COLOR`，提供两种选择
- 在以下环境测试符号：macOS Terminal、Windows Terminal、VS Code 终端、SSH 会话

**预期结果：** 得到一组无需仅依赖颜色，就能让用户一眼看懂状态的符号。

**失败时：** 如果测试中某个符号显示为 `?` 或方框，就替换为对应的 ASCII 字符。`+/-/=/!` 这组符号适用于所有环境。

### 第 3 步：设计输出详细程度

每个命令都应支持四种输出级别：

| 级别 | 标志 | 受众 | 内容 |
| --- | --- | --- | --- |
| **默认** | 无 | 终端前的用户 | 有格式、有颜色、信息清晰 |
| **详细** | `--verbose` 或 `--ceremonial` | 需要详细信息的用户 | 逐项明细、到来过程的叙事序列 |
| **静默** | `--quiet` | 脚本、CI | 尽量少的输出行、状态图标、无装饰 |
| **JSON** | `--json` | 机器端消费者 | 结构化、可解析、完整 |

实现模式：

```javascript
function output(data, options) {
  if (options.json) {
    console.log(JSON.stringify(data, null, 2));
    return;
  }
  if (options.quiet) {
    for (const item of data.items) {
      const icon = item.ok ? '+' : '!';
      console.log(`${icon} ${item.id}`);
    }
    return;
  }
  // Default (or verbose) human output
  printFormatted(data, { verbose: options.verbose });
}
```

JSON 输出规则：
- 始终输出有效 JSON，不混入面向用户的文本
- 包含人类可读输出展示的全部数据，以及对机器处理有用的额外字段
- 在不同命令之间保持键名一致
- 成功时退出码为 0，出错时为 1，与输出模式无关

**预期结果：** 四种清晰的输出级别，在不同命令之间保持一致行为。

**失败时：** 如果详细模式过于嘈杂，就将其设为明确选择后才启用的模式（`--ceremonial`），而不是把它当作逐级增加详细程度的一档。

### 第 4 步：建立文案风格规范

定义所有输出函数共同遵循的语气和风格，防止不同命令之间不一致。

文案风格规范示例（来自 campfire 输出报告模块）：

1. **现在时、主动语态：** 使用“mystic 到来”（mystic arrives），而不是“mystic 已被安装”（mystic has been installed）
2. **不使用感叹号：** 平静而自信，工具不需要大喊大叫
3. **用隐喻替代术语：** 使用“修习”（practices），而不是“依赖”（dependencies），仅限仪式感模式
4. **如实描述失败，不渲染灾难感：** 使用“一颗火星遗失了”（A spark was lost），而不是“错误：安装失败，退出码为 1”（ERROR: installation failed with exit code 1）
5. **收尾句反映状态：** 每次操作都以状态摘要结束
6. **不使用 emoji：** Unicode 符号无需依赖装饰，也能形成视觉分量
7. **每个词都承载信息：** 如果某个词不能增进理解，就删掉它

标准输出（非仪式感模式）的文案规范：
- 简洁、客观地逐行呈现信息
- 状态图标 + 条目 ID + 上下文
- 使用包含计数的摘要行
- 错误消息给出纠正问题的建议

**预期结果：** 形成 3–7 条书面文案规范，要求输出函数共同遵守。

**失败时：** 如果规则显得武断，就实际检验：针对每条规则，分别写出遵守与不遵守时的输出。如果去掉某条规则后输出质量没有变化，就不需要这条规则。

### 第 5 步：实现输出报告函数

将输出组织到一个报告模块中，并让每个函数职责集中：

```javascript
// reporter.js — standard output
export function printResults(results) { ... }
export function printItemTable(items) { ... }
export function printDetections(detections) { ... }
export function printAudit(auditResults) { ... }
export function printDryRun() { ... }
export function warn(msg) { ... }
export function error(msg) { ... }
export { chalk };
```

每个函数都遵循相同结构：
1. 妥善处理空输入和 null 输入
2. 计算布局（列宽、填充间距）
3. 使用配色方案输出
4. 在底部输出摘要行

为仪式感输出创建单独的模块：

```javascript
// campfire-reporter.js — warm narrative output
export function printArrival({ teamId, agents, results, ceremonial }) { ... }
export function printScatter({ teamId, agents, results }) { ... }
export function printTend(fires) { ... }
export function printCampfireList({ teams, state, reg }) { ... }
export function printFireSummary({ team, fireData, reg }) { ... }
export function printJson(data) { ... }
```

**预期结果：** 输出报告函数可以独立使用，每个函数自行处理格式，不依赖调用方的状态。

**失败时：** 如果函数超过约 50 行，就提取辅助函数。单个输出报告函数应当易于独立审查。

### 第 6 步：跨环境测试输出

验证输出在不同环境下都能正确呈现：

```bash
# With colors (interactive terminal)
node cli/index.js list --domains

# Without colors (piped)
node cli/index.js list --domains | cat

# With NO_COLOR environment variable
NO_COLOR=1 node cli/index.js list --domains

# JSON mode (parseable)
node cli/index.js campfire --json | jq .

# In CI (typically no TTY)
CI=true node cli/index.js audit

# The no-color fallback. A failed import cannot be provoked with an env var, so
# assert on the stub itself in the suite rather than reaching it through the CLI.
# Pass a glob, not a directory: `node --test <dir>` stopped expanding at Node 22.
node --test 'cli/test/*.test.js'
```

检查以下事项：
- 颜色在交互模式下正确显示
- 管道／重定向输出中没有泄漏 ANSI 转义码
- JSON 有效，可通过管道传给 `jq .` 验证
- Unicode 符号在目标终端中正确渲染
- 内容宽度不同时，列仍保持对齐
- 无颜色回退实现能够处理配色方案使用的每一种调用形式；这一点应在测试套件中断言，而不是只手工演示一次

**预期结果：** 在上述六种环境中，输出都正确。

**失败时：** 如果泄漏 ANSI 转义码，确保 chalk 遵循 `NO_COLOR`。如果 Unicode 显示异常，提供 ASCII 回退模式。注意，测试套件全部通过，并不能证明颜色是否正常：测试运行器通过管道接收 stdout，这会让 `chalk.level` 为 0，因此有色和无色输出在字节层面完全相同；即使颜色功能彻底损坏，断言也仍可能通过。要证明颜色功能正常，需要使用 `FORCE_COLOR=3`，并对转义序列进行断言。

## 验证清单

- [ ] 配色方案包含无颜色回退实现，且已实际运行验证：直接样式调用、工厂调用、链式调用、`level === 0` 和 `await` 均已检查
- [ ] 状态指示符在有色和无色模式下都能正常工作
- [ ] 四种输出级别都能产生有用的输出
- [ ] JSON 输出有效，且能够被 `jq` 解析
- [ ] 文案风格规范已有文档，并得到一致遵循
- [ ] 输出报告函数能妥善处理空输入和 null 输入
- [ ] 已在终端、管道、NO_COLOR、CI 环境中测试输出

## 常见陷阱

- **无颜色回退只处理直接样式调用：** `new Proxy({}, { get: () => (s) => s })` 看起来很完整，确实也能覆盖 `chalk.dim` 和 `chalk.red`，但每个工厂方法都会返回字符串，而调用方随后会立即尝试调用这个字符串。由于配色方案在模块加载时构建，`TypeError` 会出现在导入阶段——回退实现偏偏在它唯一需要发挥作用的场景中，以最严重的方式失败。第 1 步列出了存根必须满足的四个不变量。
- **将面向用户的文本与 JSON 混在一起：** 在 `--json` 模式下，只输出有效 JSON。仅仅多出一行文本，例如“DRY RUN”，就会破坏 JSON 解析器。如果命令必须同时展示两者，应明确分离，或在 JSON 模式下禁止输出人类可读文本。
- **硬编码列宽：** 内容长度会变化。使用 `Math.max(...items.map(i => i.id.length))` 动态计算填充间距。
- **颜色没有配套的信息表达：** 如果颜色是区分成功与失败的唯一方式，色觉障碍用户和管道输出都会丢失信息。始终搭配文字指示符（`+`、`OK`、`ERR`）。
- **在错误的场景中使用仪式感输出：** 温暖的叙事式输出适合交互式终端会话；在 CI、脚本或 `--quiet` 模式下，它只会增加噪声。必须通过显式标志才启用仪式感输出。
- **忘记摘要行：** 用户往往先扫视最后一行。每次操作都应以单行摘要结束，包含成功／失败／跳过的数量。

## 相关技能

- `scaffold-cli-command`——使用这套输出机制的命令
- `test-cli-application`——测试输出是否符合预期
- `build-cli-plugin`——插件通过这套输出系统报告结果
