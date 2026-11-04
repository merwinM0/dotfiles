export function toolRole(component) {
  if (component.result?.isError) return "error";
  if (["edit", "write"].includes(component.toolName)) return "success";
  if (["read", "find", "grep", "ls"].includes(component.toolName)) return "syntaxType";
  if (["bash", "powershell"].includes(component.toolName)) return "bashMode";
  return "accent";
}

export function patchTools(runtime, frames) {
  const { ToolExecutionComponent, BashExecutionComponent, DynamicBorder } = runtime.components;
  frames.decoratePrototype(ToolExecutionComponent.prototype, owner => ({
    gap: true,
    role: () => toolRole(owner),
    label: () => `${owner.toolName} · ${owner.isPartial ? "执行中" : owner.result?.isError ? "失败" : "完成"}`,
  }));

  const bash = BashExecutionComponent.prototype;
  const update = bash.updateDisplay;
  bash.updateDisplay = function (...args) {
    const result = update.apply(this, args);
    // The host owns the common frame; do not leave the previous full-width rules inside it.
    this.children = this.children.filter(child => !(child instanceof DynamicBorder));
    return result;
  };
  frames.decoratePrototype(bash, owner => ({
    gap: true,
    role: () => owner.status === "error" ? "error" : owner.status === "cancelled" ? "warning" : "bashMode",
    label: () => `命令 · ${{ running: "执行中", complete: "完成", cancelled: "已取消", error: "失败" }[owner.status] ?? owner.status}`,
  }));
}
