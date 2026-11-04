import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { pathToFileURL } from "node:url";
import { inspectRoot, SUPPORTED_VERSIONS, supportsVersion } from "./installation.mjs";
import { createFrameSystem } from "./corner-frame.mjs";
import { patchMessages } from "./message-patches.mjs";
import { patchTools } from "./tool-patches.mjs";
import { patchNotices } from "./notice-patches.mjs";

const applied = new Map();
const modules = {
  AssistantMessageComponent: "assistant-message", UserMessageComponent: "user-message",
  ToolExecutionComponent: "tool-execution", BashExecutionComponent: "bash-execution",
  CustomMessageComponent: "custom-message", CustomEntryComponent: "custom-entry",
  CompactionSummaryMessageComponent: "compaction-summary-message",
  BranchSummaryMessageComponent: "branch-summary-message", SkillInvocationMessageComponent: "skill-invocation-message",
  ThemedText: "themed-text", DynamicBorder: "dynamic-border",
};
const importFile = file => import(pathToFileURL(file).href);

export async function applyPatch(root) {
  const installation = inspectRoot(root);
  if (!supportsVersion(installation.version)) {
    throw new Error(`角框补丁已验证 Pi ${SUPPORTED_VERSIONS.join(" / ")}，当前为 ${installation.version}；未验证版本使用原版界面。`);
  }
  if (applied.has(installation.root)) return applied.get(installation.root);
  const require = createRequire(join(installation.root, "package.json"));
  const tuiEntry = require.resolve("@earendil-works/pi-tui");
  const uiRoot = join(installation.root, "dist/modes/interactive");
  const [tui, mouse, images, themeModule, interactive] = await Promise.all([
    importFile(tuiEntry), importFile(join(dirname(tuiEntry), "tui.js")),
    importFile(join(dirname(tuiEntry), "terminal-image.js")),
    importFile(join(uiRoot, "theme/theme.js")), importFile(join(uiRoot, "interactive-mode.js")),
  ]);
  const components = Object.fromEntries(await Promise.all(Object.entries(modules).map(async ([name, file]) => {
    const exports = await importFile(join(uiRoot, "components", `${file}.js`));
    if (typeof exports[name] !== "function") throw new Error(`Pi 组件接口改变：${name}`);
    return [name, exports[name]];
  })));
  const expected = [
    [components.AssistantMessageComponent, "updateContent"], [components.UserMessageComponent, "rebuild"],
    [components.ToolExecutionComponent, "render"], [components.ToolExecutionComponent, "handleMouse"],
    [components.BashExecutionComponent, "updateDisplay"], [interactive.InteractiveMode, "init"],
    [tui.TuiAltScreen, "beforeTerminalStart"], [themeModule.Theme, "bg"],
    ...["showError", "showWarning", "showStatus", "showManagedToolStatus", "addCacheWarmingUsage",
      "addCacheMissNotice", "addCompactionCostNotice", "showNewVersionNotification", "showPackageUpdateNotification"]
      .map(name => [interactive.InteractiveMode, name]),
  ];
  for (const [component, method] of expected) {
    if (typeof component.prototype[method] !== "function") throw new Error(`Pi 组件接口改变：${method}`);
  }
  const runtime = { ...installation, tui, components, themeModule, InteractiveMode: interactive.InteractiveMode };
  const frames = createFrameSystem({ tui, dispatchMouseEvent: mouse.dispatchMouseEvent, isImageLine: images.isImageLine, theme: themeModule.theme });
  // Keep panels transparent even if the user switches to another palette in /settings.
  const background = themeModule.Theme.prototype.bg;
  themeModule.Theme.prototype.bg = function (token, text) {
    if (["userMessageBg", "customMessageBg", "toolPendingBg", "toolSuccessBg", "toolErrorBg"].includes(token)) {
      return `\x1b[49m${text}\x1b[49m`;
    }
    if (token === "selectedBg") return this.bold(this.fg("accent", text));
    if (token === "searchMatchBg") return this.underline(this.fg("warning", text));
    return background.call(this, token, text);
  };
  const terminalStart = tui.TuiAltScreen.prototype.beforeTerminalStart;
  tui.TuiAltScreen.prototype.beforeTerminalStart = function (...args) {
    this.searchMatchStyle = text => themeModule.theme.underline(themeModule.theme.fg("warning", text));
    this.searchCurrentMatchStyle = text => themeModule.theme.bold(themeModule.theme.underline(themeModule.theme.fg("accent", text)));
    return terminalStart.apply(this, args);
  };
  patchMessages(runtime, frames);
  patchTools(runtime, frames);
  patchNotices(runtime, frames);
  runtime.frames = frames;
  applied.set(installation.root, runtime);
  return runtime;
}
