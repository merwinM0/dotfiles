export function patchNotices(runtime, frames) {
  const { InteractiveMode } = runtime;
  const { ThemedText, DynamicBorder } = runtime.components;
  const { Text, Markdown, Container } = runtime.tui;
  const states = new WeakMap();

  function ensure(host) {
    const chat = host.chatContainer;
    if (!chat || states.has(chat)) return chat && states.get(chat);
    const state = { style: { role: "muted", label: "信息" }, grouped: false };
    const add = chat.addChild;
    chat.addChild = function (child) {
      if (!state.grouped && (child instanceof Text || child instanceof Markdown || child instanceof ThemedText)) {
        frames.decorate(child, { ...state.style });
      }
      return add.call(this, child);
    };
    states.set(chat, state);
    return state;
  }

  const init = InteractiveMode.prototype.init;
  InteractiveMode.prototype.init = function (...args) {
    ensure(this);
    return init.apply(this, args);
  };

  const methods = [
    ["showError", "error", "错误"], ["showWarning", "warning", "警告"],
    ["showStatus", "muted", "状态"], ["showManagedToolStatus", "muted", "工具状态"],
    ["addCacheWarmingUsage", "dim", "缓存"], ["addCacheMissNotice", "warning", "缓存提示"],
    ["addCompactionCostNotice", "warning", "上下文用量"],
    ["showNewVersionNotification", "warning", "版本更新", true],
    ["showPackageUpdateNotification", "warning", "扩展更新", true],
  ];
  for (const [name, role, label, group = false] of methods) {
    const original = InteractiveMode.prototype[name];
    InteractiveMode.prototype[name] = function (...args) {
      const state = ensure(this);
      if (!state) return original.apply(this, args);
      const previous = { style: state.style, grouped: state.grouped };
      const start = this.chatContainer.children.length;
      state.style = { role: name === "showManagedToolStatus" && args[0]?.type === "warning" ? "warning" : role, label };
      state.grouped = group;
      try {
        const result = original.apply(this, args);
        if (group) {
          const children = this.chatContainer.children;
          const added = children.splice(start);
          const content = new Container();
          for (const child of added) if (!(child instanceof DynamicBorder)) content.addChild(child);
          children.push(new frames.CornerFrame(content, { role, label, gap: true }));
        }
        return result;
      } finally {
        state.style = previous.style;
        state.grouped = previous.grouped;
      }
    };
  }
}
