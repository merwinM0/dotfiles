> 中文阅读版，仅供人工参考。程序执行入口为同目录下的 `SKILL.md`（英文版）。代码示例保持英文原样，便于与执行版对照。

# Bun Blank Web 开发

**技能名称：** `bun-blank-web`

**适用范围：** 使用语义化 HTML、TypeScript、CSS、原生 DOM API、Bun HTML 打包器及可选的 `Bun.serve` API 路由，构建、扩展、调试、审查并交付无框架 Bun Blank Web 应用。适用于 `bun init` 的 Blank 项目、原生 TypeScript 前端、使用 Bun 工具链的 HTML/CSS 页面、无框架 SPA 或多页面应用，以及它们的开发、测试、生产构建和迁移。保留选定的技术栈；除非明确要求，不得替换为 React、JSX、Vite、Tailwind 或用于发布库的模板。

使用 HTML、TypeScript、CSS 和 Bun 实现需求。浏览器代码应独立于 Bun 运行时 API。只有应用需要服务端工作时才添加 Bun 服务器。

## 导航

英文执行版是一个自包含技能，可用于 Pi 或其他兼容 Agent Skills 的编码代理。详细指南和完整的最小起步源码均包含在内，不依赖配套文件。使用本地可用的文件与 Shell 工具，遵守项目指令，并如实报告无法执行的检查。

按任务阅读相关章节：

| 任务 | 参考 |
| --- | --- |
| 初始化、架构选择、依赖和 TypeScript 配置 | [项目工作流程](#项目工作流程) |
| DOM 行为、状态、表单、请求、CSS、无障碍 | [前端模式](#前端模式) |
| HTML 打包、资源、环境变量、HMR、发布输出 | [构建与部署](#构建与部署) |
| 行为测试、产物检查、故障诊断 | [测试与调试](#测试与调试) |
| API 路由、校验、服务端安全与运行维护 | [服务端与安全](#服务端与安全) |
| 根据一手文档核实变化中的 Bun 能力 | [官方资料与版本策略](#官方资料与版本策略) |

新建小型应用时，可使用[内嵌起步模板](#内嵌起步模板)作为可执行起点。该节中的文件名表示应在目标项目中创建的文件，不是本技能旁边已有的文件。将示例与现有项目协调融合，绝不能整体覆盖已有项目。

在 Pi 中，英文版原文建议将执行文档存为已配置技能目录下的 `bun-blank-web/SKILL.md`，需要显式加载时调用 `/skill:bun-blank-web`。本地当前目录名为 `bun-blank-coding`，英文元数据中的技能名仍为 `bun-blank-web`。

## 1. 修改前先检查

1. 阅读适用的项目指令和用户验收标准。
2. 检查包脚本、当前锁文件、`tsconfig*.json`、`bunfig.toml`、HTML 入口、源码导入、测试和部署设置。
3. 运行 `bun --version` 及相关帮助命令，记录实际验证的精确版本。标志或 API 不一致时查询官方文档。
4. 区分浏览器代码、服务端代码、工具代码和共享纯逻辑。
5. 保留现有架构、命名、格式、路由、CSS 和测试约定。
6. 保护无关修改。不要删除锁文件、替换项目指令、升级 Bun，或放宽类型安全来掩盖错误。
7. 常规实现选择自行判断；只有信息缺失会改变用户可见结果或阻碍进度时才提问。

把需求转化为可观察的验收标准：用户操作、校验、加载/空/错误状态、导航及相关屏幕尺寸。

## 2. 选择执行模型

| 模型 | 适用情况 | 开发 | 生产 |
| --- | --- | --- | --- |
| 静态前端 | 浏览器代码或现有 API 足以满足需求 | 通过 Bun 运行 HTML 入口 | HTML、JS、CSS、资源 |
| 多页面应用 | 内容适合独立文档和 URL | 运行多个 HTML 入口 | 每个入口对应一个构建文档 |
| 浏览器 SPA | 导航需要保留客户端状态 | 单个 HTML 入口和显式路由 | 打包产物及托管端重写规则 |
| Bun 全栈 | 密钥、特权操作、持久化或 API 必须留在服务端 | 将 HTML 导入 `Bun.serve` | Bun 目标服务器及生成的资源 |

新的 Blank Web 项目默认采用静态前端。不要只为开发服务而创建后端。生产托管路由应独立于开发服务器的 SPA 回退行为验证。

将 **Blank** 视为脚手架，而不是框架或浏览器运行时。在 `bun init` 中选择 Blank，并检查生成文件。只有确认该版本默认设置合适后才使用 `bun init -y`。

## 3. 严格划分执行边界

- HTML 负责文档语义，CSS 负责呈现，TS 模块负责浏览器行为。
- 通过 HTML 入口打包浏览器 TypeScript。直接打开原始 HTML，并不会让浏览器支持 `.ts`、裸包导入或 Bun API。
- DOM API 和浏览器存储只能用于浏览器模块或明确配置的 DOM 测试。
- `Bun.file`、`Bun.write`、`Bun.serve`、`bun:sqlite`、文件系统访问及私有环境变量只能用于服务端或工具代码。
- 共享模块应保持纯净，不包含环境特定副作用。仅类型导入使用 `import type`。
- 不让服务端配置和数据库客户端进入浏览器依赖图。
- 不添加 Node 全局变量或 polyfill 来掩盖误导入服务端代码的问题。

## 4. 建立可复现基线

新应用创建内嵌模板中的文件或等价文件：

```text
index.html
src/main.ts
src/styles.css
src/lib/                  # 按需添加纯逻辑
scripts/build.ts
scripts/preview.ts
tests/
package.json
bun.lock                  # 通过 bun install 生成
tsconfig.json
tsconfig.browser.json
tsconfig.tools.json
bunfig.toml
```

只创建必要层次。依赖、脚本、测试和打包统一使用 Bun。优先 `bun run <script>`，避免与内置命令重名。运行时依赖尽量少；TypeScript 和 Bun 类型声明放在开发依赖。

在运行时配置和 `packageManager` 中固定已验证的 Bun 版本。提交生成的锁文件；锁文件存在后，自动化使用 `bun install --frozen-lockfile`。起步模板的版本固定值是经测试基线，更新需主动审查。

浏览器和工具代码使用独立类型配置。不能因为构建脚本需要 Bun/Node 全局变量，就让浏览器代码也获得它们。启用严格检查、`noEmit`、bundler 模块解析及显式文件范围。区分类型检查目标和真实浏览器兼容性。

运行配置好的检查器：仅执行或打包 TS 不能证明类型安全。优先使用模板中的本地 `tsc` 命令。只有已安装 Bun 支持原生 `bun check`，且其对这些配置的行为已验证时才使用。

## 5. 一次完成一个用户流程

1. 编写语义化 HTML，并提供有意义的初始内容。
2. 添加响应式 CSS、可复用令牌和可见焦点指示。
3. 定义显式状态及纯领域转换。
4. 原生 DOM 事件只绑定一次；运行时收窄元素类型。
5. 不可信内容使用 `textContent` 或 DOM 构建方式渲染。
6. 处理适用的加载、成功、空、错误和禁用状态。
7. 卸载或热替换时清理监听器、观察器、请求、定时器和订阅。
8. 按需验证键盘操作、窄屏、无效输入、重复操作和请求失败。

优先局部 DOM 更新，避免替换大片文档。保留焦点、选区、滚动位置和正在进行的交互。非简单行为应以状态为唯一事实来源。

不要为小页面自建虚拟 DOM、通用组件框架、事件总线、依赖注入容器或全局状态库。只有小型库能比平台 API 更好地解决具体需求时才引入。

## 6. 保持 HTML 和 CSS 质量

- 按语义使用原生按钮、链接、表单、标签、地标、列表和表格。
- 设置文档语言、有意义的标题、字符集和 viewport 元信息。
- 在可行时，让脚本失败后的核心内容和导航仍可用。
- 使用稳定类名或 `data-*` 钩子选择控件，不依赖位置或显示文字。
- 重复的间距、颜色、排版和圆角使用自定义属性；优先 flex/grid，而不是位置微调。
- 支持内容增长、文字缩放、减少动态效果、可见焦点和目标浏览器集合。
- 除非用户要求或项目已有，不引入 CSS 框架、预处理器和插件。
- 不要把 CSS 降级转换等同于对所有 CSS 或浏览器 API 的通用支持。

## 7. 有意识地配置 Bun

浏览器构建以 HTML 为入口。通过 `<script type="module" src="./src/main.ts"></script>` 引入 TS 模块；样式建立单一明确的归属路径，例如 `<link rel="stylesheet" href="./src/styles.css">`。

分离开发、生产构建和构建产物预览。预览 `dist/`，而不是源码开发服务器。资源应通过构建可见的 HTML、CSS 或导入引用。不要假定名为 `public/` 的目录会自动复制。检查生成的 URL 和文件，包括多页面及子路径部署。

显式配置环境变量：

- 所有下发给浏览器的值都视为公开信息。
- 默认不内联环境变量；确有需要时，只使用严格限定的公开白名单或前缀。
- 开发和构建分别配置；`bunfig.toml` 开发设置不会自动配置 `Bun.build` 调用。
- 使用受支持的字面量替换方式，不假定具有 Vite 的 `import.meta.env` 行为。
- 构建或启动服务前校验必要公开值，绝不内联全部环境变量。
- 服务端密钥保持运行时可配置，不能进入包或日志。

HMR 只是开发便利。直接调用 `import.meta.hot` API，接受更新时提供清理逻辑。无法保证安全重新挂载时允许整页刷新。

## 8. 有意引入后端功能

添加路由前阅读[服务端与安全](#服务端与安全)。复杂度增长时分离请求处理、领域规则和持久化。运行时校验不可信输入，限制请求大小及昂贵操作。

区分格式错误、校验失败、身份认证、授权、资源不存在、不支持的方法及内部错误。未知 `/api/*` 路径应返回 API 错误，而不是前端 HTML。

可行时使用同源 API 路径。根据实际信任模型配置认证、Cookie、CSRF 和 CORS。客户端检查不能作为授权。服务器使用 Bun 目标构建，生产环境显式禁用开发行为。

## 9. 验证并报告证据

运行项目要求的检查。内嵌模板使用：

```sh
bun install
bun run typecheck
bun run test
bun run build
bun run preview
```

按行为和风险选择测试。领域规则使用 `bun:test`；需要时为 DOM 行为配置 DOM 环境；布局、焦点、导航及关键集成使用真实浏览器验证。避免只复述简单实现细节的测试。

检查生成的 HTML、JS、CSS、资源 URL、缺失文件和意外泄露的密钥。服务端行为改变时测试有意义的 API 错误及构建后的服务器。使用可用且获授权的浏览器工具检查 UI；否则说明哪些视觉检查未验证。

不要通过 `any`、无依据的断言、忽略诊断或禁用严格性来压制失败。不要只为测试页面就添加前端框架。

最终说明实现行为、相关文件、通过的检查及重要限制，明确无法执行的检查。未实际发生的浏览器验证、部署、安全审查或兼容性测试，绝不能声称完成。

## 完成标准

- 交付要求的流程及适用错误状态。
- 保持执行边界及有意选择的依赖。
- 通过相关类型、测试和生产构建检查。
- 构建行为改变时检查生成产物。
- 保持无障碍、响应式行为和项目约定。
- 不留下未解释的错误、仍运行的验证进程、密钥或无关改动。

## 项目工作流程

### 调研与初始化

阅读现有指令和脚本。定向搜索实际 HTML 入口、导入模块、锁文件、环境示例、测试和部署设置。修改包级配置前识别 monorepo。

运行 `bun --version`、`bun --help` 和 `bun build --help`。尽量使用固定版本，不将升级当作常规修复。验证部署环境是否支持 Bun 本身，而不只是 JavaScript。

空项目运行 `bun init` 并选择 **Blank**。检查生成文件：生成的 TS 入口不会自动成为浏览器应用，需要有意识地添加 HTML 入口和浏览器源码。不要只为获取示例配置就在已有项目中初始化。

也可在新目录中创建内嵌模板文件，并运行 `bun install` 生成锁文件。除非有意修改依赖，否则保留锁文件。模板不包含 React、JSX、CSS 框架、运行时依赖或必需后端。

### 架构与归属

| 代码 | 常见入口 | 允许的依赖 |
| --- | --- | --- |
| 浏览器 | HTML 到 `src/main.ts` | Web/DOM API 及浏览器兼容包 |
| 服务端 | `server/index.ts` | Bun API 及仅服务端包 |
| 工具 | `scripts/*.ts` | Bun 及构建/文件系统工具 |
| 共享 | 导入的纯模块 | 不依赖运行时的逻辑和数据类型 |

第一版保持精简：一个 HTML 文档、CSS 入口、TS 入口和必要纯模块。职责明显分离后再按功能拆分：

```text
src/features/search/model.ts
src/features/search/view.ts
src/features/search/api.ts
src/lib/dom.ts
src/styles/tokens.css
server/index.ts
server/routes/search.ts
server/services/search.ts
shared/contracts.ts
```

只创建必要文件。纯状态转换不做网络 IO，领域逻辑不操作 DOM。共享契约时不导入服务端实现。避免循环依赖及共享模块副作用。

独立页面显式定义 HTML 入口，并使用普通导航链接。基于 History API 的 SPA 应一起实现初始路由解析、前进/后退、焦点管理、文档标题更新和生产重写。不要假定 `Bun.serve` 按文件名发现路由或进行模板渲染。

### 依赖与版本

统一使用 Bun：

```sh
bun add package-name
bun add -d typescript @types/bun
bun remove package-name
bun install --frozen-lockfile
```

优先平台原生能力。评估新增包的浏览器支持、维护情况、体积、许可证和安装钩子。工具和测试放入开发依赖。自动化优先已安装并固定版本的工具，避免反复运行未固定的 `bunx ...@latest`。

提交当前锁文件，避免多个竞争锁文件。已有 `bun.lockb` 应保留，直到进行有意且受支持的迁移。当前 Bun 通常生成 `bun.lock`。

调查依赖安装钩子失败的原因；只信任脚本确有必要且经过审查的具体包，不要把广泛启用安装钩子作为通用修复。

让 `packageManager`、可选 `.bun-version`、本地配置及 CI 对齐实际验证的精确 Bun 版本。模板固定版本是可复现基线，不是永久推荐。升级包并重新生成锁文件时需主动审查。

### TypeScript 配置

在 `tsconfig.json` 中保留共享严格设置：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Preserve",
    "moduleResolution": "Bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  }
}
```

这些是项目选择，不是 Bun 强制要求。`skipLibCheck` 跳过依赖声明内部检查，不能成为忽略应用错误的理由。

各环境独立配置：

| 配置 | 库 | 全局类型 | 文件范围 |
| --- | --- | --- | --- |
| 浏览器 | ES2022、DOM、DOM.Iterable | `[]` | 浏览器和共享源码 |
| 工具/测试 | ES2022 | `["bun"]` | 构建脚本、纯模块、单元测试 |
| 服务端（按需） | ES2022 | `["bun"]` | 服务端和共享源码 |

通过包脚本运行 `tsc --noEmit -p tsconfig.browser.json` 及对应工具/服务端命令。原生 `bun check` 只有在确认已安装版本支持且配置行为正确后才可选用。执行或转译并不等于类型检查。

尽量不让浏览器全局对象进入纯服务端代码。Bun 类型也暴露平台声明，因此即使检查器接受，也要审查导入。浏览器代码仅声明所需的最小 HMR 类型接口，不要引入全部 Bun 全局变量。

优先相对导入。只有检查器、打包器、运行时和测试均支持时才添加别名。仅设置 TypeScript `paths` 不会教会部署后的浏览器解析别名。区分 TypeScript `target` 与实际打包器/浏览器兼容要求。

### 命令与验收

| 脚本 | 约定 |
| --- | --- |
| `dev` | 通过 Bun 开发打包器提供源码 HTML |
| `typecheck` | 不输出文件，检查所有相关环境 |
| `test` | 验证行为和失败情况 |
| `build` | 写出生产产物，构建出错时失败退出 |
| `preview` | 提供已构建的静态文件 |
| `start` | 有实际生产服务器时运行它 |

不要把源码服务称为 `preview`，也不要给纯静态应用添加虚假的服务器启动命令。构建和文件系统操作使用可移植 Bun 脚本，而不是必须依赖 Bash 的 Shell 脚本；用户可能使用 fish 或 Windows。

先写可观察验收标准，再做基础设施。搜索页应明确空输入、每次提交一个请求、等待状态、过期请求防护、错误、重试和键盘行为。先完成流程，再考虑路由器、全局状态库或组件注册机制。

## 前端模式

### HTML 与渐进式行为

HTML 承载稳定结构和有意义的初始内容。包含 doctype、字符集、viewport、文档语言及描述性标题。标题层级合理，设置一个主要 `main` 地标，列表使用列表元素，表格数据使用带表头和标题的表格。

非提交操作使用 `<button type="button">`，提交使用 `<button type="submit">`，导航使用链接。不能用可点击 `div` 模拟。输入框应有可见标签；帮助/错误文本按需通过 `aria-describedby` 关联，无效字段使用 `aria-invalid`。

重复复杂内容可使用真正的 HTML 模板，克隆 `<template>` 内容后以安全 DOM 操作填充。模板 ID 保持唯一，避免多个 TS 模块重复 HTML 字符串。

可行时让 JS 失败后普通链接和可读内容仍可用。仅 JS 功能应说明缺失能力，而不是留下永久禁用且毫无解释的界面。

### DOM 边界与生命周期

在视图边界校验必需元素。泛型选择器类型或 `as HTMLButtonElement` 不会在运行时检查实际标记：

```ts
function requireButton(root: ParentNode, selector: string): HTMLButtonElement {
  const element = root.querySelector(selector);
  if (!(element instanceof HTMLButtonElement)) {
    throw new Error(`Expected a button: ${selector}`);
  }
  return element;
}
```

使用模块脚本，使其在 HTML 解析后运行。每个视图只挂载一次；各挂载函数负责自己的副作用并返回清理函数：

```ts
export function mountCounter(root: ParentNode): () => void {
  const button = requireButton(root, '[data-action="increment"]');
  const events = new AbortController();
  let count = 0;
  button.addEventListener('click', () => {
    count += 1;
    button.textContent = `Count: ${count}`;
  }, { signal: events.signal });
  return () => events.abort();
}
```

除监听器外，还应清理 interval/timeout、`requestAnimationFrame`、观察器、订阅、未完成请求和外部引用。使用 `AbortController` 创建事件监听器可简化卸载。事件委托使用 `instanceof Element`、`closest` 及根边界检查。

只有能安全重新挂载时才直接使用 HMR 调用：

```ts
const dispose = mountCounter(document);
if (import.meta.hot) {
  import.meta.hot.accept();
  import.meta.hot.dispose(dispose);
}
```

此例接受更新后会重置局部状态。需要保留状态时，应显式设计并依据 Bun 当前 HMR 契约验证。不能只因存在 HMR 就承诺状态保留。

### 状态与渲染

有实际规则时使用显式类型和纯转换。可辨识联合有助于避免不可能的异步状态：

```ts
type ResultsState<T> =
  | { status: 'idle' }
  | { status: 'loading'; query: string }
  | { status: 'success'; items: T[] }
  | { status: 'error'; message: string };
```

持久化状态和领域状态不应含 DOM 引用。总数和筛选列表应派生计算，不维护多个相互竞争的副本。功能局部对象足够时，不使用全局可变状态。

只渲染变化部分，使用 `textContent`、`createElement`、`append`、`replaceChildren` 和属性。用户可控字符串绝不插入 `innerHTML`。可信常量/模板与不可信值不同，但仍优先更简单的安全 API。

不要每次按键都重建正在使用的表单。保留焦点和选区。列表在身份重要时使用稳定 ID 和定向更新。批量构建可用 `DocumentFragment`；只有测量证明确有规模问题后才虚拟化。

确需接收富 HTML 时，选择持续维护的净化器并制定显式策略。URL 校验单独处理：安全设置 `href` 并不意味着 `javascript:` 导航安全。解析 URL 并仅允许所需协议和来源。

### 表单与校验

通过 `FormData` 或有明确类型的控件读取值。写自定义校验前先使用 `required`、`min`、`max`、`minlength`、`maxlength` 和适当输入类型。考虑未选中的复选框、禁用字段、重名字段、文件输入及空字符串。

谨慎处理数字解析：拒绝非有限值，约束领域范围；不要依赖 `parseInt` 校验整个数字字符串。避免使用真值判断误拒合法零值。

显示可操作的字段错误，修正后清理过期错误，并将消息关联到字段。提交后聚焦第一个无效字段或错误摘要。不要通过 live region 播报每次按键。

通过表单 submit 事件统一处理 Enter 提交和按钮点击。防止重复写入，失败时保留输入并提供恢复路径。通过 `finally` 或状态转换重新启用控件。异步变更需区分取消与失败，不要声称取消浏览器请求就回滚了服务端写入。

输入跨越信任边界时，服务端必须重复校验。浏览器校验改善界面，但不是授权或数据完整性保障。

### 请求与存储

请求逻辑放入小型功能 API 模块。检查 `response.ok`；服务端返回 4xx/5xx 并不会让 `fetch` 自动拒绝。根据端点需求处理空响应体、意外内容类型、错误 JSON、网络失败和取消。

远程 JSON 按 `unknown` 解析，再校验结构。`as User[]` 等类型断言不校验数据。小契约使用针对性的类型守卫；复杂度足够时再引入 schema 包。

实时搜索应防止过期结果覆盖。取消前一个读取请求，并在应用结果前检查单调递增请求 ID；仅取消不足以证明所有异步步骤停止。只有能减少无用工作而不损害反馈时才对快速输入防抖。

同源服务器优先相对 `/api/...` URL。不要通过宽松 CORS 修复错误 API 地址。跨源时明确凭据策略。只对适当操作使用超时和有界重试；无幂等设计时，绝不自动重试非幂等写入。

查询字符串使用 `URLSearchParams`，路径片段有意识地编码，不通过不安全拼接组装 URL。

只持久化真正需要的数据。记录版本、校验解码 JSON、从损坏/旧数据恢复并捕获存储失败。绝不在 localStorage 持久化密钥。存储视为不可信输入，只清理应用自己的键。结构化数据量或异步访问确有需要时使用 IndexedDB，不为单个偏好设置引入它。

### CSS 与无障碍

小型样式表按令牌、基础规则、布局、组件和工具组织。拆分确实改善维护性时才使用 CSS 导入。没有明确原因时，不要同时从 HTML 和 TS 导入同一份样式。

使用逻辑属性、流式宽度、`max-inline-size`、`minmax`、grid、flex 和 `gap`。必要时通过 `min-inline-size: 0` 让子元素收缩。长字符串可换行；不断增长的文字内容不要使用固定高度。

类名清晰、选择器低特异性。`!important` 仅用于有文档说明的工具类或不可避免的覆盖。组件选择器限定作用域，避免全局影响。重复值使用 CSS 自定义属性；媒体查询由布局需要驱动，而不是设备名称。

焦点可见、对比度足够、支持键盘操作。优先原生语义而非 ARIA。`aria-live="polite"` 谨慎用于异步状态更新，不要把每个装饰值都设为 live region。

自定义对话框或菜单需实现焦点进入/恢复、键盘关闭、适当语义及外部交互。目标浏览器支持时优先原生 `<dialog>`，不要实现残缺的模态遮罩。

信息图像提供有用 alt 文本，装饰图像使用空 alt。不要只靠颜色传递信息。尊重 `prefers-reduced-motion`，不能让理解状态依赖动画。添加深色主题时，两种主题都检查表单控件、对比度、图标和保存/系统偏好行为。

验证窄宽布局、文字缩放、较长翻译标签、校验消息、空数据集和大数据集。单一宽度截图不足以证明响应式。

### 性能与兼容性

增加缓存、worker、懒加载或虚拟化前先测量。避免循环中混杂反复布局读取和写入。必要时将昂贵视觉工作合并到帧中。移除热点路径中不必要的全局监听器和同步存储访问。

指定图像尺寸以减少布局偏移，使用响应式图片和适当加载行为。优先系统字体，或有明确加载策略的自托管资源，不默认添加外部字体。

设定浏览器支持目标。Bun 的 `target: "browser"` 选择执行环境，不是通用兼容性保证。检查不支持的语法/API，仅为真实需求添加 polyfill。可行时在目标真实浏览器上测试平台特有行为。

## 构建与部署

### HTML 开发与生产

浏览器以 HTML 为入口，使用相对路径引用源码 TS 模块和样式。开发可直接运行 `bun ./index.html`；使用仓库 `dev` 脚本。端口/控制台等 CLI 标志应依据已安装版本核实。

非简单配置使用构建脚本。内嵌模板的 `Bun.build` 显式配置浏览器目标、HTML 入口、输出目录、压缩、无 source map 和禁用环境内联。检查结果，失败时非零退出。

不能因为脚本执行到最后就把失败的 API 构建当作成功。根据已安装 Bun API 检查 `success`/日志并捕获抛出的错误。除非有意配置且验证过集成检查器，否则单独运行类型检查。

构建输出隔离。只清理从项目/脚本位置解析的已知输出目录。没有包含关系检查时，绝不递归删除用户提供路径。不要将源码 `.env`、测试、服务端模块或私有配置复制到静态输出。

确认支持后，简单 CLI 构建可用：

```sh
bun build ./index.html --target=browser --outdir=dist --minify
```

多页面显式传入每个 HTML 入口，并检查生成文档和共享资源引用。不要杜撰自动页面发现。可选的独立单文件 HTML 输出属于另行处理的版本相关功能，不是默认发布格式。

### 资源与 URL

优先构建图可见的引用：

- HTML 属性，如图像源和样式链接。
- 相对 CSS `url(...)` 和样式导入。
- 受支持的静态模块导入或其他经验证的资源引用。

Bun 可能重写处理后的资源路径，应检查输出而不是预测哈希文件名。动态字符串不一定能被发现。不要假定各版本对所有 `new URL(..., import.meta.url)` 模式或扩展名处理一致。

`public/` 没有通用的自动复制约定。robots.txt、Web manifest、下载文件或运行时选择资源需要稳定路径时，应明确复制/服务规则并测试。保持正确 MIME 类型，避免多个事实来源。

子路径托管要测试真实基础路径。相对路径、根相对链接、CSS URL、SPA 导航和深层刷新行为不同。按需配置文档说明的构建/public-path 和托管行为，不能假定部署在 `/`。直接访问嵌套页后再刷新验证。

静态预览应服务生成文件，对缺失资源返回真实 404，避免暴露源码。SPA 文档回退必须显式且仅用于导航路由，不能对缺失 JS/CSS 或 API 路径返回 HTML。

### 环境配置

默认不替换浏览器环境变量。需要公开配置时使用严格前缀，如 `PUBLIC_*`，或显式构建期 `define` 映射。进入 JS/HTML 的所有值，不论名字是什么，都公开可读。

Bun 文档中的开发配置可使用：

```toml
[serve.static]
env = "PUBLIC_*"
```

相应生产 `Bun.build` 必须单独设置 `env` 策略。开发配置不决定 API 构建策略。浏览器包避免 `env: "inline"`。

字面量 `process.env.PUBLIC_API_URL` 仅在配置了受支持替换方式后使用。不要假定 `import.meta.env`、解构、计算属性访问或别名与 Vite 一样。未设置/未替换引用可能让缺少 `process` 的浏览器崩溃。

需要更强控制时，在构建脚本中校验公开值，仅通过 `define` 注入它的 JSON 字符串字面量，并有意识地提供等价开发配置。模板完全不引用公开环境变量，无需 `.env` 即可运行。

诊断缺失值前阅读当前 Bun 环境文件加载规则。显式环境有意识地使用 `--env-file`，`.env.example` 不含凭据，实际密钥加入忽略。区分构建期公开配置与运行时服务端配置；修改服务端环境不会重写已经构建的静态包。

绝不全局定义 `process.env` 以序列化整个环境。服务端凭据也不能烘焙进服务端包；除非明确编译某个非敏感常量，否则运行时读取。

### HMR 与进程重启

区分浏览器模块替换、Bun 进程热重载和进程 watch/重启，它们的状态及清理影响不同。依据已安装版本验证，不承诺所有编辑都保留状态。

浏览器 HMR 直接调用 `import.meta.hot.accept()` 和 `import.meta.hot.dispose(...)`，不要为 HMR 对象或方法设别名。清理旧模块副作用。需要保留状态时显式设计和测试。

不能安全重新挂载的视图使用整页刷新。反复编辑后检查重复监听器、过期定时器、多重请求和观察器泄漏。开发成功不证明生产输出已排除 HMR 代码；管线改变时检查构建。

### 全栈构建

全栈发布与静态模板分离：

```sh
bun build ./server/index.ts --target=bun --production --root=. --outdir=dist-server
```

依据已安装版本验证命令。服务端 HTML 导入可转为预构建前端 manifest。在此布局及显式 root 下，预期服务器位于 `dist-server/server/index.js`，浏览器资源位于 `dist-server/`。检查实际输出，不假定入口总在输出根目录。

在已验证基线上，从输出目录启动，让 HTML manifest 的相对资源路径正确解析：

```sh
cd dist-server
env NODE_ENV=production bun ./server/index.js
```

进程管理器配置等价工作目录。打包器升级或输出命名改变后重测。显式配置运行时生产模式，不假定构建标志替代运行时部署配置。

根据输出布局保留服务器旁所有必要资源。有意识地检查外置运行时依赖、动态加载文件、迁移、数据库路径和公开文件。单个服务端 JS 文件不自动等于整个部署。

容器使用实际验证的精确 Bun 镜像/版本，构建阶段用锁文件安装，有意处理运行时依赖，只有需要时提供可写数据目录。不复制本地凭据或其他操作系统的 `node_modules`。按宿主配置监听地址和端口。静态网站生产环境不需要 Bun 进程。

### 发布验证

最终改动后运行一次相关检查，再检查产物：

1. 按锁定依赖集安装。
2. 运行适用类型检查和有意义测试。
3. 构建生产输出并检查日志。
4. 预览输出或运行构建后的服务器。
5. 请求 HTML、JS、CSS 和代表性资源，验证状态码与内容类型。
6. 按部署模型验证深链接/404/API 行为。
7. 检查意外密钥、源码、私有 map 或仅开发资源。
8. 浏览器工具可用时检查控制台/网络和关键交互。

有意识地配置缓存：HTML 应允许发现更新；不可变缓存适合已确认带内容哈希的资源。压缩、TLS、响应头、可观测性和托管重写规则按需放在部署层。只生成本地构建不能声称已部署。

## 测试与调试

### 验证策略

添加工具前检查现有检查机制。按变更规模验证：文案/样式修改通常需要构建和视觉检查；复杂校验、状态转换、持久化、API 和并发需要行为测试。不要写只复述常量或选择器的测试。

模板从项目根运行 `bun run typecheck`、`bun run test` 和 `bun run build`，预览构建的 `dist/` 产物。后续干净复现使用 frozen-lockfile 安装。

将以下视为独立证据：

| 检查 | 能证明 | 不能证明 |
| --- | --- | --- |
| 类型检查器 | 静态类型一致性 | 运行时数据有效性或浏览器渲染 |
| `bun:test` | 在 Bun 中执行到的逻辑 | 真实浏览器布局/焦点 |
| DOM 模拟器 | 模拟环境中的受测 DOM 行为 | 完整浏览器布局/API 兼容性 |
| 构建 | 为配置入口生成包 | 托管正确性或运行时交互 |
| HTTP 冒烟检查 | 状态、内容、资源可访问性 | 完整 UI 行为 |
| 浏览器交互 | 受测浏览器中观察到的流程 | 所有浏览器/设备支持 |

### 单元与集成测试

使用 `import { test, expect } from "bun:test"`。领域逻辑应能独立导入，不启动服务器或操作 DOM。按需测试边界、无效输入、状态转换、损坏持久化值及顺序/竞态行为。

输入保持确定；时间重要时固定时钟。在明确边界 mock 外部服务；每个用例后重置 mock 和状态。避免依赖测试顺序、不可控网络、真实凭据或共享可变文件。

服务端路由优先服务器工厂，让测试以端口 `0` 启动，记录分配的 URL，并在清理阶段停止。按需测试状态码、相关响应头、响应结构、不支持方法、格式错误和授权。持久化测试使用临时隔离目录，有意识地测试迁移。

不要为了适配错误行为而跳过失败测试、放宽断言或修改 fixture。判断错误在预期契约还是实现。

### DOM 与真实浏览器检查

Bun 运行时不是完整浏览器 DOM。确有需要时才安装兼容 DOM 环境。官方文档方案包括在测试导入前加载 `@happy-dom/global-registrator`：

```ts
// tests/setup-dom.ts
import { GlobalRegistrator } from '@happy-dom/global-registrator';
GlobalRegistrator.register();
```

```toml
[test]
preload = ["./tests/setup-dom.ts"]
```

合并进现有配置，不覆盖无关设置。检查这些测试的配置应包含 DOM 库。全局 DOM preload 若可能掩盖边界错误，不用于纯服务端测试；必要时拆分测试命令/套件。

测试可观察行为：挂载、激活控件、检查结果、卸载、重新挂载，并确保一次操作只引起一次更新。每个用例后清理 DOM 和资源。模拟器不验证布局、真实焦点行为、CSS 或所有浏览器 API。

关键端到端流程复用项目已有真实浏览器运行器，如已安装的 Playwright。执行与 `bun:test` 发现分离，例如 E2E 文件放独立目录，限制单元测试根目录。不能因为 Bun 启动其 CLI 就声称 Playwright 在 Bun 测试运行器内部运行。

真实浏览器检查清单：

- 指针和键盘验证初始状态及主要操作。
- 检查焦点顺序、可见焦点、标签、无效状态和恢复。
- 检查窄/宽布局及长内容。
- 触发空、加载、失败及重复请求状态。
- 检查控制台错误、失败网络请求和缺失资源。
- 存在路由时验证导航、前进/后退、直接深链接和刷新。
- 生命周期代码改变时，验证重新挂载或多次开发更新后的清理。

### 生产冒烟检查

使用构建输出预览，请求 `/`、生成的 JS/CSS 及一个缺失路径。验证 HTML 包含构建引用，资源返回正确媒体类型。缺失 JS/CSS URL 返回 200 HTML 属于失败。

静态应用确认必要请求不依赖源码 `.ts`、本地文件系统路径或仅开发模块。服务端应用运行生成的 Bun 服务器，测试 HTML 和 API 成功/失败，确认生产模式及必要运行时环境。

检查代表性资源路径，不硬编码猜测哈希。配置测试可使用已知非敏感哨兵值检查意外嵌入，绝不把真实凭据打印到日志。

如实说明浏览器检查情况。没有浏览器时，应报告类型/测试/构建/HTTP 检查通过，而视觉交互仍未验证。

### 故障诊断

| 现象 | 优先调查 | 修复方向 |
| --- | --- | --- |
| 浏览器拒绝 TS 或裸导入 | 直接打开原始 HTML、错误服务器、绕过打包器 | 通过 Bun HTML 入口或构建输出提供服务 |
| 浏览器出现 `Bun is not defined` | 服务端代码进入浏览器依赖图 | 将运行时逻辑移到 API/工具边界后 |
| 测试/服务端出现 `document is not defined` | 导入浏览器代码或缺少 DOM 环境 | 拆分模块或显式配置 DOM 测试 |
| 浏览器出现 `process is not defined` | 未替换环境引用或仅 Node 依赖 | 配置显式公开替换或移除服务端依赖 |
| 构建通过但类型失败 | 把转译当作检查 | 运行并修复实际检查器，不放宽设置 |
| 开发正常但生产资源 404 | 动态资源字符串、缺失复制步骤、基础路径 | 检查输出图和托管 URL |
| 构建后服务器报告打包文件缺失 | 工作目录、manifest 路径、产物复制不全 | 保留全部生成资源，从验证过的输出目录启动 |
| 深链接刷新 404 | 生产重写缺失 | 只为导航配置文档回退 |
| API JSON 解析器收到 `<` | 前端回退将 API 错误变为 HTML | 修复路由匹配和 API 404 |
| 更新后重复事件 | 缺少 HMR/卸载清理 | 重新挂载前中止/移除旧副作用 |
| 旧响应覆盖新结果 | 异步竞态 | 增加取消和请求身份检查 |
| UI 丢失光标/焦点 | 整个表单重新渲染 | 定向更新有焦点的 DOM 节点 |
| CSS 缺失/重复 | 错误相对链接、混合归属、构建遗漏 | 使用单一明确 CSS 入口路径 |
| 依赖脚本后安装失败 | 不可信生命周期钩子、版本不匹配 | 检查具体依赖，只信任必要钩子 |
| 本地正常、Linux 失败 | 文件名/导入大小写、系统原生依赖 | 修正精确大小写，按目标平台安装 |
| 打包标志未知 | 文档与运行时版本不符 | 阅读已安装版本帮助，采用受支持等价项 |

将失败缩小为最小相关依赖图。加依赖前验证当前目录、入口、版本、配置来源和环境。没有证据表明缓存或锁文件是原因时，不清缓存或删锁文件。

### 报告

报告实际运行的命令及结果。说明已验证 Bun 版本，区分源码服务和产物预览。如实说明重要未检查项，不夸大确定性。停止验证服务器，最终补丁移除临时生成测试产物。

## 服务端与安全

### 后端决策

需求包含私有凭据、共享持久化数据、授权、特权调用或服务端控制渲染时才添加服务器。不要只因 Bun 能提供 HTTP 就引入。浏览器入口与服务端入口分离。

小型服务使用显式路由。复杂度增加时组织处理器/服务/持久化。即使只是方便复用助手函数，也不能在浏览器导入服务端模块；应抽出纯共享助手。

### 最小全栈边界

以下可选示例应按项目调整，不默认加入静态应用：

```ts
// server/index.ts; the HTML lives in the project root.
import page from '../index.html';

const production = process.env.NODE_ENV === 'production';
const rawPort = process.env.PORT ?? '3000';
const port = /^\d+$/.test(rawPort) ? Number(rawPort) : NaN;
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('PORT must be an integer from 1 to 65535');
}

const server = Bun.serve({
  port,
  hostname: process.env.HOST ?? '127.0.0.1',
  development: production ? false : { hmr: true, console: true },
  routes: {
    '/': page,
    '/api/health': {
      GET() {
        return Response.json({ ok: true });
      },
    },
  },
  fetch(request) {
    const isApi = new URL(request.url).pathname.startsWith('/api/');
    return isApi
      ? Response.json({ error: 'Not found' }, { status: 404 })
      : new Response('Not found', { status: 404 });
  },
});
console.log(`Listening on ${server.url}`);
```

本地开发使用回环地址；容器或部署按宿主配置监听地址。服务端类型检查配置应包含 server 目录。临时脚本状态使用运行时安全的局部名称，不覆盖常见环境变量。

按构建与部署章节使用 `--target=bun`、显式项目根目录和输出目录启动流程。保留全部资源树，测试生产工作目录。示例有意不含认证、持久化、SPA 回退或写 API；只有实际需求存在才实现。验证不支持方法行为；契约要求时返回 405 和 `Allow` 头。

未知 `/api/*` 保持 JSON 错误。添加兜底 HTML 路由时排除 API 和资源失败。健康端点不能泄露密钥、连接字符串、内部细节或详细数据库错误。

### 校验与 API 契约

请求头、URL/查询/路径参数、JSON 体、multipart 表单、Cookie、存储及数据库值都视为不可信。解析为 `unknown`，使用前验证结构、长度、类型、数值范围、允许值和归属。

区分语法错误（400）、未认证（401）、禁止操作（403）、资源缺失（404）、不支持方法（405）、冲突（409）、体积超限（413）、不支持媒体类型（415）、领域校验错误（按既有契约使用 400/422）和意外错误（500）。

服务器和代理均设请求体限制。不能只信任 `Content-Length`，流式/分块输入也需有界。限制上传、查询复杂度、分页、昂贵操作及相关超时。适当时拒绝意外内容类型。

错误响应应稳定有用，不暴露堆栈或凭据。服务端记录有上下文且脱敏的诊断，运维确有需要时生成请求 ID。

共享 TS 类型改善开发工具体验，但网络边界仍需运行时校验。`fetch` 或 `Response.json` 上匹配的泛型不是 schema 校验器。

### 身份认证与数据访问

需要时才引入认证，并定义信任模型。服务端认证调用者，对每个受保护资源/操作授权。隐藏按钮或检查浏览器状态中的用户 ID 不够。

Cookie 会话配置 `HttpOnly`、适当 `Secure` 和 `SameSite`、作用域、过期、轮换和失效。不在浏览器存储保存特权凭据。Cookie 认证的变更操作采用成熟设计处理 CSRF；仅 SameSite 不是通用替代。

尽量同源请求。必须跨源时，有意识地允许目标来源/方法/请求头。CORS 不是认证；通配来源加凭据不是可接受修复。

使用参数化 SQL 或绑定参数的标签 API，不能将用户数据拼接进 SQL。校验 ID、强制记录归属，多次写入涉及一致性时用事务。按实际持久化需要创建迁移和备份/恢复机制。内存 map 是临时状态，不是持久化存储。

`.env` 和密钥不能进入版本控制、浏览器代码、产物和日志。启动时校验必需服务端变量，失败时不打印值。

### 文件、请求与运行维护

静态文件使用白名单映射，或在已知根目录内解析并可靠处理包含关系和符号链接。不能直接把任意 URL 路径拼到项目根目录。隐藏文件、源码、环境文件、私钥和数据文件不可访问。返回正确 MIME 类型，缺失资源真实返回 404。

用户指定的出站请求应定义允许协议/目标；有实际 SSRF 风险时执行网络策略。限制重定向、响应大小和超时。不能携带服务端凭据代理浏览器提供的任意 URL。

子进程优先参数数组 API，而不是 Shell 插值。原始用户字符串不能传给命令 Shell。避免暴露通用文件系统或命令端点。

生产环境显式将 development 设为 false。通过固定 Bun 版本支持的 API 优雅关闭：停止接收流量、有界等待在途工作、关闭存储和资源。持久化数据放在可丢弃构建目录之外。

在相关服务器/代理层配置 TLS、压缩、缓存、请求限制、安全头和日志。CSP 依据实际脚本/样式/HMR 需要，开发策略可不同于生产。在部署环境检查依赖 HTTPS 的 API。这些是实际服务的实现要求，不是引入无用后端的理由。

## 官方资料与版本策略

变化中的行为以官方文档和已安装 CLI 帮助为准。引入陌生标志、API 或部署假设前查询相关来源。英文原文注明以下链接核查于 2026-10-31；本次翻译未重新联网核查。内嵌模板的精确验证基线见对应章节。

| 主题 | 一手资料 | 核实内容 |
| --- | --- | --- |
| Blank 脚手架 | https://bun.com/docs/runtime/templating/init | 模板选择、生成文件、默认设置 |
| HTML 入口 | https://bun.com/docs/bundler/html-static | 开发命令、HTML 处理、多页面行为 |
| 打包 API | https://bun.com/docs/bundler | 目标、构建结果、输出选项、define |
| 全栈 HTML 导入 | https://bun.com/docs/bundler/fullstack | HTML manifest、生产/运行时区别 |
| HTTP 路由 | https://bun.com/docs/runtime/http/server | 路由选项、回退、运行时限制 |
| HMR | https://bun.com/docs/bundler/hot-reloading | 直接调用语法、清理、支持的方法 |
| CSS 处理 | https://bun.com/docs/bundler/css | 资源引用、降级转换、模块行为 |
| TypeScript | https://bun.com/docs/runtime/typescript | 声明和推荐编译选项 |
| 原生检查 | https://bun.com/docs/runtime/check | 已安装版本支持、检查范围 |
| 测试运行器 | https://bun.com/docs/test | 发现、钩子、CLI 选项 |
| DOM 测试 | https://bun.com/docs/test/dom | 可选模拟器预加载和测试环境 |
| 依赖安装 | https://bun.com/docs/pm/cli/install | 冻结安装、依赖、生命周期信任 |
| 锁文件 | https://bun.com/docs/pm/lockfile | 当前格式和有意迁移 |
| 环境加载 | https://bun.com/docs/runtime/environment-variables | 环境文件和运行时访问 |
| 索引访问检查 | https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html | 潜在 undefined 值 |

本技能中的架构、约定、示例和审查标准是工程指导，不代表 Bun 强制要求。不要大段复制文档。

文档能力若在项目 Bun 版本中不存在，应使用受支持替代或提出有意升级及其影响。不要静默升级现有项目。除非任务包括变更，否则保留已验证检查器及包版本。

优先当前规范的 `bun.com` 文档。旧 `bun.sh` 链接可能重定向。依赖新链接前先验证。运行时行为不能仅以第三方文章为依据。

## 内嵌起步模板

仅在确认目标目录为空，或文件不会覆盖用户工作后，才在新项目目录创建以下文件。将计数器示例调整为用户所需应用。项目依赖与代理自身运行时保持独立。

英文原文说明：源码示例已使用 Bun 1.4.4、TypeScript 7.0.2 和 `@types/bun` 1.4.4 验证。本次仅翻译，未重新执行这些示例。这是可复现基线，不要求升级已有项目。调整命令前检查已安装版本。

通过 `bun install` 生成 `bun.lock`，不要手写锁文件。应用项目提交生成的锁文件。示例没有运行时依赖，也不要求环境变量。

创建文件后运行：

```sh
bun install
bun run typecheck
bun run test
bun run build
bun run preview
```

源码开发使用 `bun run dev`；提供已构建输出使用 `bun run preview`。预览服务器仅监听回环地址，用于本地验证，不是生产托管建议。

### `package.json`

```json
{
  "name": "bun-blank-web-starter",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "packageManager": "bun@1.4.4",
  "scripts": {
    "dev": "bun ./index.html",
    "typecheck:browser": "tsc --noEmit -p tsconfig.browser.json",
    "typecheck:tools": "tsc --noEmit -p tsconfig.tools.json",
    "typecheck": "bun run typecheck:browser && bun run typecheck:tools",
    "test": "bun test ./tests",
    "build": "bun run ./scripts/build.ts",
    "preview": "bun run ./scripts/preview.ts"
  },
  "devDependencies": {
    "@types/bun": "1.4.4",
    "typescript": "7.0.2"
  }
}
```

### `.bun-version`

```text
1.4.4
```

### `.gitignore`

```text
node_modules/
dist/
coverage/
.env
.env.*
!.env.example
*.log
```

### `bunfig.toml`

```toml
[serve.static]
env = "disable"
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Preserve",
    "moduleResolution": "Bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "files": []
}
```

### `tsconfig.browser.json`

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "types": []
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts"]
}
```

### `tsconfig.tools.json`

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "lib": ["ES2022"],
    "types": ["bun"]
  },
  "include": ["scripts/**/*.ts", "tests/**/*.ts", "src/lib/**/*.ts"]
}
```

### `index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="A framework-free HTML, TypeScript, and CSS starter powered by Bun.">
    <title>Bun Blank Starter</title>
    <link rel="stylesheet" href="./src/styles.css">
    <script type="module" src="./src/main.ts"></script>
  </head>
  <body>
    <main class="card">
      <p class="eyebrow">HTML · TypeScript · CSS</p>
      <h1>Bun Blank Starter</h1>
      <p>A small, accessible counter with explicit state and input validation.</p>
      <p class="total">Completed tasks: <output data-count aria-live="polite">0</output></p>
      <form data-counter>
        <label for="step">Tasks to add</label>
        <input id="step" name="step" type="number" value="1" min="1" max="100" step="1" required aria-describedby="step-help counter-error">
        <p id="step-help" class="help">Enter a whole number from 1 to 100.</p>
        <p id="counter-error" class="error" data-error role="alert" hidden></p>
        <div class="actions">
          <button type="submit">Add tasks</button>
          <button type="button" data-reset class="secondary">Reset</button>
        </div>
      </form>
      <noscript><p>This counter requires JavaScript. The page content remains available.</p></noscript>
    </main>
  </body>
</html>
```

### `src/env.d.ts`

```ts
// Keep browser typings independent of Bun's server/runtime globals.
// Declare only the verified HMR surface used by this starter.
interface ImportMeta {
  readonly hot?: {
    accept(): void;
    dispose(callback: () => void): void;
  };
}
```

### `src/lib/counter.ts`

```ts
export function parseStep(raw: string): number {
  const value = raw.trim();
  if (!/^\d+$/.test(value)) {
    throw new Error("Enter a whole number from 1 to 100.");
  }
  const step = Number(value);
  if (!Number.isSafeInteger(step) || step < 1 || step > 100) {
    throw new Error("Enter a whole number from 1 to 100.");
  }
  return step;
}

export function addTasks(count: number, step: number): number {
  if (!Number.isSafeInteger(count) || count < 0) {
    throw new Error("The current task count is invalid.");
  }
  if (!Number.isSafeInteger(step) || step < 1 || step > 100) {
    throw new Error("Enter a whole number from 1 to 100.");
  }
  const next = count + step;
  if (!Number.isSafeInteger(next)) {
    throw new Error("The task count is too large. Reset to continue.");
  }
  return next;
}
```

### `src/main.ts`

```ts
import { addTasks, parseStep } from "./lib/counter.ts";

function mountCounter(root: ParentNode): () => void {
  const form = root.querySelector("[data-counter]");
  const output = root.querySelector("[data-count]");
  const step = root.querySelector("#step");
  const reset = root.querySelector("[data-reset]");
  const error = root.querySelector("[data-error]");
  if (!(form instanceof HTMLFormElement) ||
      !(output instanceof HTMLOutputElement) ||
      !(step instanceof HTMLInputElement) ||
      !(reset instanceof HTMLButtonElement) ||
      !(error instanceof HTMLParagraphElement)) {
    throw new Error("The counter markup is incomplete.");
  }

  const events = new AbortController();
  let count = 0;
  const clearError = (): void => {
    error.textContent = "";
    error.hidden = true;
    step.removeAttribute("aria-invalid");
  };
  const render = (): void => {
    output.value = String(count);
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearError();
    try {
      count = addTasks(count, parseStep(step.value));
      render();
    } catch (cause: unknown) {
      error.textContent = cause instanceof Error ? cause.message : "Please try again.";
      error.hidden = false;
      step.setAttribute("aria-invalid", "true");
      step.focus();
    }
  }, { signal: events.signal });

  step.addEventListener("input", clearError, { signal: events.signal });
  reset.addEventListener("click", () => {
    count = 0;
    form.reset();
    clearError();
    render();
  }, { signal: events.signal });

  clearError();
  render();
  return () => events.abort();
}

const dispose = mountCounter(document);
if (import.meta.hot) {
  import.meta.hot.accept();
  import.meta.hot.dispose(dispose);
}
```

### `src/styles.css`

```css
:root {
  color-scheme: light;
  font-family: system-ui, sans-serif;
  color: #172033;
  background: #f2f4f8;
  --accent: #2344b8;
  --radius: 0.75rem;
}
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; padding: clamp(1rem, 5vw, 4rem); line-height: 1.6; }
.card {
  max-inline-size: 36rem;
  margin-inline: auto;
  padding: clamp(1.25rem, 4vw, 2.5rem);
  border: 1px solid #d6dce7;
  border-radius: var(--radius);
  background: #fff;
  overflow-wrap: anywhere;
}
h1 { line-height: 1.2; font-size: clamp(1.8rem, 6vw, 2.4rem); }
.eyebrow { color: #43516b; font-weight: 600; }
.total { font-size: 1.25rem; font-weight: 700; }
label { display: block; font-weight: 600; }
input, button { font: inherit; border-radius: 0.4rem; }
input {
  display: block;
  inline-size: 100%;
  margin-block-start: 0.4rem;
  padding: 0.7rem;
  border: 1px solid #788398;
  color: inherit;
  background: #fff;
}
.help { color: #43516b; font-size: 0.9rem; }
.error { color: #a61728; font-weight: 600; }
.actions { display: flex; flex-wrap: wrap; gap: 0.75rem; }
button {
  min-block-size: 2.75rem;
  padding: 0.65rem 1rem;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
  cursor: pointer;
}
button.secondary { color: var(--accent); background: #fff; }
:focus-visible { outline: 3px solid #c2440a; outline-offset: 3px; }
[hidden] { display: none !important; }
```

### `scripts/build.ts`

```ts
import { rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const projectRoot = fileURLToPath(new URL("../", import.meta.url));
const output = fileURLToPath(new URL("../dist/", import.meta.url));

// Delete only this fixed, project-owned output directory.
await rm(output, { recursive: true, force: true });
const result = await Bun.build({
  entrypoints: [fileURLToPath(new URL("../index.html", import.meta.url))],
  root: projectRoot,
  outdir: output,
  target: "browser",
  minify: true,
  sourcemap: "none",
  env: "disable",
});
for (const log of result.logs) console.error(log);
if (!result.success) process.exit(1);
console.log(`Built ${result.outputs.length} files into dist/`);
```

### `scripts/preview.ts`

```ts
import { fileURLToPath } from "node:url";

// Local preview only: serve an exact map of build outputs, never source paths.
const outputRoot = fileURLToPath(new URL("../dist/", import.meta.url));
const files = new Map<string, ReturnType<typeof Bun.file>>();
for await (const relative of new Bun.Glob("**/*").scan({
  cwd: outputRoot,
  onlyFiles: true,
  dot: false,
  followSymlinks: false,
})) {
  files.set(`/${relative.replaceAll("\\", "/")}`, Bun.file(`${outputRoot}/${relative}`));
}
if (!files.has("/index.html")) throw new Error("Build the application before previewing it.");

const rawPort = process.env.PORT ?? "4173";
const port = /^\d+$/.test(rawPort) ? Number(rawPort) : NaN;
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("PORT must be an integer from 1 to 65535.");
}
const server = Bun.serve({
  hostname: "127.0.0.1",
  port,
  development: false,
  fetch(request) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }
    let pathname: string;
    try {
      pathname = decodeURIComponent(new URL(request.url).pathname);
    } catch {
      return new Response("Bad request", { status: 400 });
    }
    if (pathname.includes("\\") || pathname.includes("\0")) {
      return new Response("Bad request", { status: 400 });
    }
    const file = files.get(pathname === "/" ? "/index.html" : pathname);
    if (!file) return new Response("Not found", { status: 404 });
    return new Response(request.method === "HEAD" ? null : file, {
      headers: { "Content-Type": file.type, "Cache-Control": "no-store" },
    });
  },
});
console.log(`Built-output preview: ${server.url}`);
```

### `tests/counter.test.ts`

```ts
import { describe, expect, test } from "bun:test";
import { addTasks, parseStep } from "../src/lib/counter.ts";

describe("task input and count boundaries", () => {
  test("accepts the range boundaries and surrounding whitespace", () => {
    expect(parseStep("1")).toBe(1);
    expect(parseStep("100")).toBe(100);
    expect(parseStep(" 25 ")).toBe(25);
  });
  test.each(["", " ", "0", "101", "-1", "1.5", "1e2", "12tasks", "Infinity", "99999999999999999999"])(
    "rejects invalid task step %j", (raw) => {
      expect(() => parseStep(raw)).toThrow();
    },
  );
  test("preserves zero and permits the final safe count", () => {
    expect(addTasks(0, 1)).toBe(1);
    expect(addTasks(Number.MAX_SAFE_INTEGER - 1, 1)).toBe(Number.MAX_SAFE_INTEGER);
  });
  test("rejects overflow and invalid caller state", () => {
    expect(() => addTasks(Number.MAX_SAFE_INTEGER, 1)).toThrow();
    expect(() => addTasks(-1, 1)).toThrow();
    expect(() => addTasks(0, 0)).toThrow();
    expect(() => addTasks(0, NaN)).toThrow();
  });
});
```

## Pi 加载参考

使用包含 `SKILL.md` 的目录，获得可移植加载方式。调用 `/skill:bun-blank-web` 显式请求此技能。遵循所用 Pi 版本配置的技能位置；支持时，编辑已加载技能后执行 `/reload`。

主要格式和加载文档：<https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md>。

跨机器迁移时保持英文执行技能自包含。上文所有本地文件名均表示需要创建的应用文件，不是技能包必需依赖。
