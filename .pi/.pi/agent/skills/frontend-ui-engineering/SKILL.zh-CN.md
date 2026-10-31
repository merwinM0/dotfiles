> 中文阅读版，仅供人工参考。程序执行入口为同目录下的 `SKILL.md`（英文版）。

# 前端 UI 工程

**适用范围：** 构建生产级、无障碍、响应式用户界面。用于新建或修改界面与页面、创建组件、实现布局、满足 WCAG 无障碍要求、管理状态，以及需要生产级观感而非 AI 生成感的任务。

## 概述

构建具备无障碍能力、性能良好、视觉精致的生产级用户界面。目标是让界面看起来出自顶尖公司中具有设计意识的工程师，而不是 AI 生成器。这意味着真正遵循设计系统、正确实现无障碍、认真设计交互模式，并避免泛化的“AI 审美”。

## 何时使用

- 构建新的 UI 组件或页面
- 修改现有用户界面
- 实现响应式布局
- 添加交互或状态管理
- 修复视觉或用户体验问题

## 组件架构

### 文件结构

将组件相关内容放在一起：

```text
src/components/
  TaskList/
    TaskList.tsx          # 组件实现
    TaskList.test.tsx     # 测试
    TaskList.stories.tsx  # Storybook 示例（如果使用）
    use-task-list.ts      # 自定义 Hook（状态复杂时）
    types.ts              # 组件专属类型（按需）
```

### 组件模式

**优先组合，而不是配置：**

```tsx
// 推荐：可组合
<Card>
  <CardHeader>
    <CardTitle>Tasks</CardTitle>
  </CardHeader>
  <CardBody>
    <TaskList tasks={tasks} />
  </CardBody>
</Card>

// 避免：过度配置
<Card
  title="Tasks"
  headerVariant="large"
  bodyPadding="md"
  content={<TaskList tasks={tasks} />}
/>
```

**保持组件职责集中：**

```tsx
// 推荐：只做一件事
export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className="flex items-center gap-3 p-3">
      <Checkbox checked={task.done} onChange={() => onToggle(task.id)} />
      <span className={task.done ? 'line-through text-muted' : ''}>{task.title}</span>
      <Button variant="ghost" size="sm" onClick={() => onDelete(task.id)}>
        <TrashIcon />
      </Button>
    </li>
  );
}
```

**分离数据获取与展示：**

```tsx
// 容器：处理数据
export function TaskListContainer() {
  const { tasks, isLoading, error } = useTasks();

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="Failed to load tasks" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="No tasks yet" />;

  return <TaskList tasks={tasks} />;
}

// 展示组件：处理渲染
export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul role="list" className="divide-y">
      {tasks.map(task => <TaskItem key={task.id} task={task} />)}
    </ul>
  );
}
```

## 状态管理

**选择能满足需求的最简单方案：**

```text
局部状态（useState）             → 组件专属 UI 状态
状态提升                        → 两三个兄弟组件共享的状态
Context                         → 主题、身份认证、语言区域（读多写少）
URL 状态（searchParams）         → 筛选、分页、可分享的 UI 状态
服务端状态（React Query、SWR）   → 带缓存的远程数据
全局状态库（Zustand、Redux）     → 全应用共享的复杂客户端状态
```

**避免超过 3 层的属性透传。** 如果中间组件只传递却不使用属性，应引入 Context 或调整组件树。

## 遵循设计系统

### 以参考证据驱动 UI 质量

当产品需要明确的视觉方向时，先收集证据，再选择布局：

1. 搜索可信的参考案例库，或使用产品团队提供的参考。
2. 研究两三个相关界面，记录信息层级、密度、导航、控件、响应式行为和交互状态方面的决策。
3. 实现前将这些决策整理成简短的设计约定，明确页面任务、主要操作、必要状态、响应式规则，以及应排除的模式。
4. 使用产品自己的组件、设计令牌、内容和视觉语言重建有价值的结构。不得复制其他产品的品牌、专有文案、图像或完全相同的布局。

将参考作为证据，而不是模板。无法获取参考时，记录假设，并依据产品现有设计系统检查结果。

### 避免 AI 审美

AI 生成的 UI 有可识别的套路，应全部避免：

| AI 默认做法 | 问题所在 | 生产级做法 |
|---|---|---|
| 到处使用紫色或靛蓝色 | 模型偏好视觉上“安全”的配色，使应用千篇一律 | 使用项目真实配色 |
| 过多渐变 | 增加视觉噪声，与多数设计系统冲突 | 使用纯色，或符合设计系统的细微渐变 |
| 所有元素都用大圆角（rounded-2xl） | 只强调“友好”，忽略真实设计中的圆角层级 | 使用设计系统一致的圆角规范 |
| 通用首屏宣传区 | 模板化布局脱离真实内容和用户需求 | 内容优先布局 |
| Lorem ipsum 式占位文案 | 掩盖真实内容暴露的长度、换行和溢出问题 | 使用真实感的占位内容 |
| 所有地方都用超大内边距 | 同样宽松的间距破坏视觉层级、浪费空间 | 使用一致的间距尺度 |
| 套路化卡片网格 | 忽视信息优先级和浏览模式 | 使用目标驱动的布局 |
| 大量阴影 | 层叠阴影与内容争抢注意力，并拖慢低端设备渲染 | 除非设计系统要求，否则少用或不用阴影 |

### 间距与布局

使用一致的间距尺度，不随意创造数值：

```css
/* 使用 0.25rem 递增尺度，或项目自己的尺度 */
/* 推荐 */ padding: 1rem;      /* 16px */
/* 推荐 */ gap: 0.75rem;       /* 12px */
/* 避免 */ padding: 13px;      /* 不符合尺度 */
/* 避免 */ margin-top: 2.3rem; /* 不符合尺度 */
```

### 排版

遵循文字层级：

```text
h1 → 页面标题（每页一个）
h2 → 章节标题
h3 → 子章节标题
body → 默认正文
small → 次要文字或辅助说明
```

不要跳过标题级别，也不要把标题样式用于非标题内容。

### 颜色

- 使用语义化颜色令牌，如 `text-primary`、`bg-surface`、`border-default`，而不是直接写十六进制颜色。
- 确保足够的对比度：普通文字 4.5:1，大号文字 3:1。
- 不要只靠颜色传达信息，还应使用图标、文字或图案。

## 无障碍（WCAG 2.1 AA）

每个组件都必须满足以下标准。

### 键盘导航

```tsx
// 每个交互元素都必须支持键盘操作
<button onClick={handleClick}>Click me</button>        // ✓ 默认可聚焦
<div onClick={handleClick}>Click me</div>               // ✗ 不可聚焦
<div role="button" tabIndex={0} onClick={handleClick}    // ✓ 但优先使用 <button>
     onKeyDown={e => {
       if (e.key === 'Enter') handleClick();
       if (e.key === ' ') e.preventDefault();
     }}
     onKeyUp={e => {
       if (e.key === ' ') handleClick();
     }}>
  Click me
</div>
```

### ARIA 标签

```tsx
// 为缺少可见文字的交互元素提供标签
<button aria-label="Close dialog"><XIcon /></button>

// 为表单输入提供标签
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// 没有可见标签时可使用 aria-label
<input aria-label="Search tasks" type="search" />
```

### 焦点管理

```tsx
// 内容变化时移动焦点
function Dialog({ isOpen, onClose }: DialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) closeRef.current?.focus();
  }, [isOpen]);

  // 对话框打开时，应将焦点限制在对话框内
  return (
    <dialog open={isOpen}>
      <button ref={closeRef} onClick={onClose}>Close</button>
      {/* 对话框内容 */}
    </dialog>
  );
}
```

### 有意义的空状态和错误状态

```tsx
// 不要显示空白页面
function TaskList({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return (
      <div role="status" className="text-center py-12">
        <TasksEmptyIcon className="mx-auto h-12 w-12 text-muted" />
        <h3 className="mt-2 text-sm font-medium">No tasks</h3>
        <p className="mt-1 text-sm text-muted">Get started by creating a new task.</p>
        <Button className="mt-4" onClick={onCreateTask}>Create Task</Button>
      </div>
    );
  }

  return <ul role="list">...</ul>;
}
```

## 响应式设计

先为移动端设计，再扩展：

```tsx
// Tailwind：移动优先的响应式布局
<div className="
  grid grid-cols-1      /* 移动端：单列 */
  sm:grid-cols-2        /* 小屏：两列 */
  lg:grid-cols-3        /* 大屏：三列 */
  gap-4
">
```

在以下宽度测试：320px、768px、1024px、1440px。

## 加载与过渡

```tsx
// 内容加载使用骨架屏，而不是旋转指示器
function TaskListSkeleton() {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="Loading tasks">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-12 bg-muted animate-pulse rounded" />
      ))}
    </div>
  );
}

// 使用乐观更新提升速度感知
function useToggleTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData(['tasks']);

      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(t => t.id === taskId ? { ...t, done: !t.done } : t)
      );

      return { previous };
    },
    onError: (_err, _taskId, context) => {
      queryClient.setQueryData(['tasks'], context?.previous);
    },
  });
}
```

## 另请参阅

详细无障碍要求和测试工具见 `../../references/accessibility-checklist.md`。

## 常见借口

| 借口 | 现实 |
|---|---|
| “无障碍只是锦上添花” | 在许多司法辖区，这是法律要求，也是工程质量标准。 |
| “以后再做响应式” | 后补响应式设计的难度是从一开始就做的 3 倍。 |
| “设计还没定，所以先不写样式” | 使用设计系统默认样式。没有样式的 UI 会给评审者留下产品损坏的第一印象。 |
| “这只是原型” | 原型会变成生产代码，应从一开始打好基础。 |
| “现在有点 AI 风格也没关系” | 这会传递低质量信号。应从一开始使用项目真实的设计系统。 |

## 警示信号

- 组件超过 200 行（应拆分）
- 内联样式或随意指定像素值
- 缺少错误、加载或空状态
- 没有键盘导航测试
- 只用颜色表示状态（红绿颜色却没有文字或图标）
- 通用“AI 风格”（紫色渐变、超大卡片、套路布局）

## 验证

完成 UI 后检查：

- [ ] 组件渲染时没有控制台错误
- [ ] 所有交互元素都可通过键盘访问（用 Tab 遍历页面）
- [ ] 屏幕阅读器能够传达页面内容和结构
- [ ] 在 320px、768px、1024px、1440px 下正常工作
- [ ] 按需处理加载、空、错误、成功和权限状态
- [ ] 遵循项目设计系统的间距、颜色和排版
- [ ] 渲染结果通过最终的 UI 专项完成质量审查
- [ ] 开发者工具或 axe-core 没有无障碍警告
