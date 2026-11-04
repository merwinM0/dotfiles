import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { test } from "node:test";
import { transparentSgr } from "../pi-ui/.local/lib/pi-ui/ansi.mjs";
import { findInstallation, inspectRoot, supportsVersion, SUPPORTED_VERSIONS, wantsInteractivePatch } from "../pi-ui/.local/lib/pi-ui/installation.mjs";
import { applyPatch } from "../pi-ui/.local/lib/pi-ui/frame-patch.mjs";

const installation = findInstallation();
const runtime = await applyPatch(installation.root);
runtime.themeModule.initTheme("myTheme", false);
const { tui, components: c, frames, themeModule } = runtime;
const { createShellRenderers } = await import(pathToFileURL(join(installation.root, "dist/core/tools/renderers/bash.js")));
const plain = lines => tui.stripTerminalSequences(lines.join("\n"));
const requestRender = () => {};
const ui = { requestRender };
const message = content => ({ role: "assistant", content, stopReason: "stop", timestamp: 0 });
const event = overrides => ({ type: "click", button: "left", x: 4, y: 2, width: 60, height: 10,
  screenX: 104, screenY: 102, shift: false, alt: false, ctrl: false, ...overrides });
const countFrames = lines => (plain(lines).match(/┏/g) ?? []).length;

function bounds(lines, width) {
  for (const line of lines) assert.ok(tui.visibleWidth(line) <= width, `${tui.visibleWidth(line)} > ${width}`);
}
function noBackground(lines) {
  for (const line of lines) assert.equal(transparentSgr(line), line, "An opaque/reversed SGR survived framing");
}
function tool(name = "bash", definition) {
  return new c.ToolExecutionComponent(name, "test-call", { command: "printf 中文" }, {}, definition, ui, "/tmp");
}

test("frames have continuous horizontal borders and user messages are labeled mo", () => {
  for (const width of [8, 12, 40, 80]) {
    const frame = new frames.CornerFrame(new tui.Text("body", 0, 0), { label: "mo" });
    const lines = frame.render(width).map(line => tui.stripTerminalSequences(line));
    assert.equal(lines[0], width === 8 ? `┏${"━".repeat(6)}┓` : `┏━ mo ${"━".repeat(width - 7)}┓`);
    assert.equal(lines.at(-1), `┗${"━".repeat(width - 2)}┛`);
    bounds(lines, width);
    for (const line of lines.slice(1, -1)) {
      assert.match(line, /^┃.*┃$/);
      assert.equal(tui.visibleWidth(line), width);
    }
  }
  assert.equal(themeModule.theme.fg("borderAccent", "gold"), "\x1b[38;2;232;197;104mgold\x1b[39m");
  const user = new c.UserMessageComponent("user fixture");
  assert.match(plain(user.render(60)), /┏━ mo ━+┓/);
});

test("only explicitly reviewed Pi versions pass the compatibility guard", () => {
  assert.deepEqual(SUPPORTED_VERSIONS, ["1.4.0", "1.5.0"]);
  assert.equal(supportsVersion(installation.version), true);
  for (const version of SUPPORTED_VERSIONS) assert.equal(supportsVersion(version), true);
  for (const version of ["1.5.1", "1.6.0", "2.0.0", "1.5.0-beta.1", "", undefined]) {
    assert.equal(supportsVersion(version), false);
  }
});

test("Pi 1.5 Markdown metadata and reused streaming components survive framing", { skip: installation.version === "1.4.0" }, () => {
  const contexts = [];
  const transformer = (markdown, context) => { contexts.push(context); return markdown; };
  const timestamp = "2026-11-04T00:00:00.000Z";
  const user = new c.UserMessageComponent("metadata fixture", undefined, 1, [transformer], "user-fixture", timestamp);
  user.render(60);
  assert.ok(contexts.some(context => context.messageType === "user" && context.messageId === "user-fixture" && context.timestamp === timestamp));
  const assistant = new c.AssistantMessageComponent(message([{ type: "text", text: "first fixture" }]), false, undefined,
    "Thinking...", 1, [transformer], "assistant-fixture", timestamp);
  assistant.render(60);
  const markdown = assistant.markdownSlots[0].markdown;
  assistant.updateContent(message([{ type: "text", text: "streamed fixture" }]), true);
  assert.match(plain(assistant.render(60)), /streamed fixture/);
  assert.equal(assistant.markdownSlots[0].markdown, markdown);
  assert.ok(contexts.some(context => context.messageType === "assistant" && context.messageId === "assistant-fixture"
    && context.timestamp === timestamp && context.isStreaming));
  assert.equal(countFrames(assistant.render(60)), 1);
  assistant.setOutputPad(0);
  assert.equal(countFrames(assistant.render(60)), 1);
});

test("Pi 1.5 hidden thinking with an empty label leaves no frame or spacing", { skip: installation.version === "1.4.0" }, () => {
  const assistant = new c.AssistantMessageComponent(message([{ type: "thinking", thinking: "hidden fixture" }]), true, undefined, "");
  assert.deepEqual(assistant.render(60), []);
  assistant.setHideThinkingBlock(false);
  assert.equal(countFrames(assistant.render(60)), 1);
  assert.match(plain(assistant.render(60)), /hidden fixture/);
});

test("Pi 1.5 deferred argument rendering applies the final delta once per frame", { skip: installation.version === "1.4.0" }, () => {
  const calls = [];
  const component = tool("bash", { renderCall(args) { calls.push(args.command); return new tui.Text(args.command, 0, 0); } });
  component.render(60);
  const before = calls.length;
  component.updateArgs({ command: "printf intermediate" });
  component.updateArgs({ command: "printf final" });
  assert.equal(calls.length, before);
  const lines = component.render(60);
  assert.equal(calls.length, before + 1);
  assert.equal(calls.at(-1), "printf final");
  assert.match(plain(lines), /printf final/);
  assert.equal(countFrames(lines), 1);
  assert.equal(component.argsPending, false);
});

test("Pi 1.5 tool and custom-message keybinding helpers are retained", { skip: installation.version === "1.4.0" }, () => {
  const component = tool();
  const context = component.getRenderContext();
  assert.equal(typeof context.keyHint, "function");
  assert.equal(typeof context.keyText, "function");
  let received;
  const custom = new c.CustomMessageComponent({ customType: "fixture", content: "fixture" }, (_message, options) => {
    received = options;
    return new tui.Text("custom keybinding fixture", 0, 0);
  });
  assert.equal(countFrames(custom.render(60)), 1);
  assert.equal(typeof received.keyHint, "function");
  assert.equal(typeof received.keyText, "function");
});

test("paint removal preserves truecolor foreground channels and hyperlinks", () => {
  const fg = "\x1b[38;2;40;100;107m";
  const link = "\x1b]8;;https://example.org\x1b\\中文\x1b]8;;\x1b\\";
  assert.equal(transparentSgr(`${fg}\x1b[48;2;10;20;30m${link}\x1b[49m`), `${fg}\x1b[49m${link}\x1b[49m`);
  assert.equal(transparentSgr("\x1b[38;5;40;48;5;120mtext"), "\x1b[38;5;40;49mtext");
  assert.equal(transparentSgr("\x1b[48:2::12:13:14;38:2::40:100:107mX"), "\x1b[49;38:2::40:100:107mX");
  assert.equal(transparentSgr("\x1b[1;7;41mX"), "\x1b[1;1;4;49mX");
});

test("launcher leaves redirected, print, JSON, RPC and maintenance commands alone", () => {
  const terminal = { stdin: true, stdout: true };
  assert.equal(wantsInteractivePatch([], terminal), true);
  assert.equal(wantsInteractivePatch(["--mode", "text"], terminal), true);
  for (const args of [["--print"], ["-p"], ["--mode", "json"], ["--mode=rpc"], ["update"], ["auth", "check"], ["--version"], ["--help"], ["--export", "file"]]) {
    assert.equal(wantsInteractivePatch(args, terminal), false, args.join(" "));
  }
  assert.equal(wantsInteractivePatch([], {}), false);
  assert.equal(wantsInteractivePatch([], { ...terminal, disabled: true }), false);
  assert.equal(wantsInteractivePatch(["--", "--print"], terminal), true);
});

test("wrong packages and unsupported Pi versions fail before patching", async () => {
  const root = mkdtempSync(join(tmpdir(), "pi-ui-version-"));
  try {
    mkdirSync(join(root, "dist/bundle"), { recursive: true });
    writeFileSync(join(root, "dist/bundle/cli.js"), "");
    writeFileSync(join(root, "package.json"), JSON.stringify({ name: "not-pi", version: "1.4.0" }));
    assert.throws(() => inspectRoot(root), /不是 Pi/);
    writeFileSync(join(root, "package.json"), JSON.stringify({ name: "@earendil-works/pi-coding-agent", version: "9.0.0" }));
    await assert.rejects(applyPatch(root), /当前为 9.0.0/);
  } finally { rmSync(root, { recursive: true }); }
});

test("applying the patch twice is idempotent", async () => {
  assert.equal(await applyPatch(installation.root), runtime);
  const user = new c.UserMessageComponent("hello");
  assert.equal(countFrames(user.render(50)), 1);
});

test("frames fit Chinese, emoji, ANSI content and very narrow windows", () => {
  const frame = new frames.CornerFrame(new tui.Text("中文 👩‍💻 é ** test long content", 0, 0), { label: "宽度测试" });
  for (const width of [1, 2, 5, 7, 8, 12, 30, 80, 160]) {
    const lines = frame.render(width);
    bounds(lines, width);
    noBackground(lines);
  }
});

test("empty and whitespace-only components do not create empty frames", () => {
  for (const text of ["", "\n\n", "   "]) {
    const frame = new frames.CornerFrame(new tui.Text(text, 0, 0));
    assert.deepEqual(frame.render(40), []);
  }
});

test("image protocol rows are passed through unchanged", () => {
  const image = "\x1b_Ga=T,f=24,s=1,v=1;AAAA\x1b\\";
  const frame = new frames.CornerFrame({ render: () => [image], invalidate() {} });
  assert.equal(frame.render(40)[1], image);
});

test("mouse coordinates account for corners, outer gap and trimmed child rows", () => {
  let received;
  const child = { render: () => ["", "", "hello", ""], invalidate() {}, handleMouse(input) { received = input; return { handled: true }; } };
  const frame = new frames.CornerFrame(child, { gap: true });
  frame.render(60);
  const handled = frame.handleMouse(event({ x: 4, y: 2 }));
  assert.ok(handled.handled);
  assert.equal(received.x, 3);
  assert.equal(received.y, 2);
  assert.equal(received.width, 58);
  assert.equal(handled.target.originX, 101);
  assert.equal(frame.handleMouse(event({ y: 1 })), undefined);
});

test("decorating in place preserves identity and invalidation", () => {
  const text = new tui.Text("first", 0, 0);
  assert.equal(frames.decorate(text, { label: "状态" }), text);
  assert.equal(countFrames(text.render(40)), 1);
  text.setText("second"); text.invalidate();
  assert.match(plain(text.render(40)), /second/);
  frames.decorate(text);
  assert.equal(countFrames(text.render(40)), 1);
});

test("user frames retain OSC 133 navigation markers and original Markdown", () => {
  const source = "中文 **bold**\n\n```sh\nprintf hello\n```";
  const user = new c.UserMessageComponent(source);
  const lines = user.render(70);
  assert.equal(user.text, source);
  assert.equal(countFrames(lines), 1);
  assert.ok(lines[0].startsWith("\x1b]133;A"));
  assert.ok(lines.at(-1).startsWith("\x1b]133;B"));
  bounds(lines, 70); noBackground(lines);
});

test("thinking and assistant output use separate frames without mutating messages", () => {
  const input = message([{ type: "thinking", thinking: "独立思考" }, { type: "text", text: "最终回答" }]);
  const before = JSON.stringify(input);
  const assistant = new c.AssistantMessageComponent(input);
  const lines = assistant.render(60);
  assert.equal(countFrames(lines), 2);
  assert.match(plain(lines), /思考/); assert.match(plain(lines), /回答/);
  assert.equal(JSON.stringify(input), before);
  bounds(lines, 60); noBackground(lines);
});

test("thinking click and visibility toggle survive the coordinate wrapper", () => {
  const assistant = new c.AssistantMessageComponent(message([{ type: "thinking", thinking: "隐藏内容" }]));
  const frame = assistant.contentContainer.children.find(child => child instanceof frames.CornerFrame);
  frame.render(60);
  assert.equal(frame.handleMouse(event({ y: 1 })).handled, true);
  assert.match(plain(assistant.render(60)), /Thinking/);
  assistant.setHideThinkingBlock(false);
  assert.match(plain(assistant.render(60)), /隐藏内容/);
});

test("streaming shrink, errors and cancellation leave only the current frame", () => {
  const assistant = new c.AssistantMessageComponent(message([{ type: "text", text: "long\n".repeat(20) }]));
  const expanded = assistant.render(40).length;
  assistant.updateContent(message([{ type: "text", text: "short" }]), true);
  assert.ok(assistant.render(40).length < expanded);
  assert.equal(countFrames(assistant.render(40)), 1);
  assistant.updateContent({ ...message([]), stopReason: "error", errorMessage: "fixture error" });
  assert.match(plain(assistant.render(40)), /fixture error/);
  assistant.updateContent({ ...message([]), stopReason: "aborted" });
  assert.match(plain(assistant.render(40)), /提示/);
});

test("tool frames keep built-in renderers, completion, failure, expansion and mouse", () => {
  const component = tool("bash", createShellRenderers("$"));
  assert.match(plain(component.render(60)), /执行中/);
  component.updateResult({ content: [{ type: "text", text: "result\n".repeat(30) }], isError: false });
  const collapsed = component.render(60);
  assert.match(plain(collapsed), /完成/);
  component.handleMouse(event());
  assert.equal(component.expanded, true);
  assert.ok(component.render(60).length > collapsed.length);
  component.updateResult({ content: [{ type: "text", text: "failure" }], isError: true });
  const failed = component.render(60);
  assert.match(plain(failed), /失败/); assert.match(plain(failed), /failure/);
  bounds(failed, 60); noBackground(failed);
});

test("tools with self-rendered shells keep the existing call and result renderers", () => {
  const definition = { renderShell: "self", renderCall: () => new tui.Text("custom call", 0, 0), renderResult: () => new tui.Text("custom result", 0, 0) };
  const component = tool("custom", definition);
  component.updateResult({ content: [{ type: "text", text: "payload" }] });
  const lines = component.render(50);
  assert.equal(countFrames(lines), 1);
  assert.match(plain(lines), /custom call/); assert.match(plain(lines), /custom result/);
});

test("manual commands retain streamed output and do not retain old horizontal rules", () => {
  const bash = new c.BashExecutionComponent("printf 中文", ui);
  try {
    bash.appendOutput("中文\n");
    assert.match(plain(bash.render(60)), /执行中/);
    bash.setComplete(0, false);
    const lines = bash.render(60);
    assert.equal(countFrames(lines), 1);
    assert.match(plain(lines), /中文/); assert.match(plain(lines), /完成/);
    assert.doesNotMatch(plain(lines).split("\n").filter(line => !/^[┏┗]/.test(line)).join("\n"), /[─━]{5}/);
    assert.equal(bash.getOutput(), "中文\n");
    noBackground(lines);
  } finally { bash.setComplete(0, false); }
});

test("summary, skill, custom messages and custom entries retain expansion", () => {
  const components = [
    new c.CompactionSummaryMessageComponent({ summary: "summary fixture", tokensBefore: 2000 }),
    new c.BranchSummaryMessageComponent({ summary: "branch fixture" }),
    new c.SkillInvocationMessageComponent({ name: "example", content: "skill fixture" }),
    new c.CustomMessageComponent({ customType: "fixture", content: "custom fixture" }),
    new c.CustomEntryComponent({ customType: "fixture" }, () => new tui.Text("entry fixture", 0, 0)),
  ];
  for (const component of components) {
    component.setExpanded(true);
    const lines = component.render(60);
    assert.equal(countFrames(lines), 1);
    assert.match(plain(lines), /fixture/);
    bounds(lines, 60); noBackground(lines);
    component.invalidate();
    assert.equal(countFrames(component.render(60)), 1);
  }
});

test("status deduplication and error/warning notice frames preserve stored references", () => {
  const host = Object.create(runtime.InteractiveMode.prototype);
  host.chatContainer = new tui.Container(); host.ui = ui; host.outputPad = 1;
  host.showStatus("first");
  const length = host.chatContainer.children.length;
  host.chatContainer.render(60);
  host.showStatus("second");
  assert.equal(host.chatContainer.children.length, length);
  assert.equal(host.chatContainer.children.at(-1), host.lastStatusText);
  assert.match(plain(host.chatContainer.render(60)), /second/);
  assert.doesNotMatch(plain(host.chatContainer.render(60)), /first/);
  host.showError("test failure"); host.showWarning("test warning");
  const lines = host.chatContainer.render(60);
  assert.equal(countFrames(lines), 3);
  assert.match(plain(lines), /错误/); assert.match(plain(lines), /警告/);
  noBackground(lines);
});

test("update notification is one common frame instead of nested text frames", () => {
  const host = Object.create(runtime.InteractiveMode.prototype);
  host.chatContainer = new tui.Container(); host.ui = ui;
  host.showPackageUpdateNotification(["test-package"]);
  const lines = host.chatContainer.render(80);
  assert.equal(countFrames(lines), 1);
  assert.match(plain(lines), /test-package/);
  assert.doesNotMatch(plain(lines).split("\n").filter(line => !/^[┏┗]/.test(line)).join("\n"), /[─━]{5}/);
});

test("custom renderer failures and message severity override the category color", () => {
  const entry = new c.CustomEntryComponent({ customType: "broken" }, () => { throw new Error("fixture failure"); });
  const lines = entry.render(80);
  const errorPrefix = themeModule.theme.fg("error", "X").split("X")[0];
  assert.ok(lines.find(line => line.includes("┏")).includes(errorPrefix));
  const warning = new c.CustomMessageComponent({ customType: "status", content: "fixture", details: { level: "warn" } });
  const warningPrefix = themeModule.theme.fg("warning", "X").split("X")[0];
  assert.ok(warning.render(80).find(line => line.includes("┏")).includes(warningPrefix));
});

test("fullscreen search distinguishes matches without reverse-video backgrounds", () => {
  const terminal = { columns: 80, rows: 24, write() {} };
  const viewport = new tui.TuiAltScreen(terminal, false, undefined, { mouse: false });
  try {
    viewport.beforeTerminalStart();
    const normal = viewport.searchMatchStyle("fixture");
    const current = viewport.searchCurrentMatchStyle("fixture");
    assert.notEqual(normal, current);
    noBackground([normal, current]);
    assert.doesNotMatch(current, /\x1b\[7m/);
  } finally { viewport.beforeTerminalStop({}); }
});

test("theme changes redraw frame colors while panels and search remain transparent", () => {
  const user = new c.UserMessageComponent("theme fixture");
  const custom = user.render(60).join("\n");
  themeModule.setTheme("dark", false);
  user.invalidate();
  const changed = user.render(60);
  assert.notEqual(changed.join("\n"), custom);
  noBackground(changed);
  assert.doesNotMatch(themeModule.theme.bg("selectedBg", "selected"), /\x1b\[48/);
  themeModule.setTheme("myTheme", false);
});
