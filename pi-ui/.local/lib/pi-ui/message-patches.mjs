export function patchMessages(runtime, frames) {
  const { components: c, tui } = runtime;
  const assistant = c.AssistantMessageComponent.prototype;
  const update = assistant.updateContent;
  assistant.updateContent = function (...args) {
    const result = update.apply(this, args);
    this.contentContainer.children = this.contentContainer.children.map(child => {
      if (child instanceof tui.Spacer) return child;
      if (child instanceof tui.MouseRegion) {
        return new frames.CornerFrame(child, { role: "syntaxKeyword", label: "思考" });
      }
      const warning = ["aborted", "length"].includes(this.lastMessage?.stopReason);
      return new frames.CornerFrame(child, {
        role: child instanceof tui.Markdown ? "borderAccent" : warning ? "warning" : "error",
        label: child instanceof tui.Markdown ? "回答" : warning ? "提示" : "错误",
      });
    });
    return result;
  };

  const user = c.UserMessageComponent.prototype;
  const rebuild = user.rebuild;
  user.rebuild = function (...args) {
    const result = rebuild.apply(this, args);
    this.children = this.children.map(child => new frames.CornerFrame(child, { role: "accent", label: "mo" }));
    return result;
  };

  for (const [name, label] of [
    ["CustomMessageComponent", "消息"], ["CustomEntryComponent", "扩展"],
    ["CompactionSummaryMessageComponent", "上下文摘要"], ["BranchSummaryMessageComponent", "分支摘要"],
    ["SkillInvocationMessageComponent", "技能"],
  ]) {
    frames.decoratePrototype(c[name].prototype, owner => ({
      role: lines => {
        if (name === "CustomEntryComponent" && tui.stripTerminalSequences(lines.join("\n")).includes("renderer failed:")) return "error";
        const level = owner.message?.details?.level;
        return level === "error" ? "error" : ["warn", "warning"].includes(level) ? "warning" : "customMessageLabel";
      },
      label, gap: ["CustomMessageComponent", "CustomEntryComponent"].includes(name),
    }));
  }
}
