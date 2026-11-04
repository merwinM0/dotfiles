import { accessSync, constants, readFileSync, realpathSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

// Keep an explicit list of versions reviewed against the private rendering API.
export const SUPPORTED_VERSIONS = Object.freeze(["1.4.0", "1.5.0"]);
export const supportsVersion = version => SUPPORTED_VERSIONS.includes(version);

export function inspectRoot(root) {
  const path = realpathSync(root);
  const manifest = JSON.parse(readFileSync(join(path, "package.json"), "utf8"));
  if (manifest.name !== "@earendil-works/pi-coding-agent") throw new Error("不是 Pi 安装目录");
  const bundledEntry = join(path, "dist/bundle/cli.js");
  accessSync(bundledEntry, constants.R_OK);
  return { root: path, version: manifest.version, bundledEntry, plainEntry: join(path, "dist/cli.js") };
}

export function findInstallation(env = process.env) {
  if (env.PI_UI_AGENT_ROOT) return inspectRoot(env.PI_UI_AGENT_ROOT);
  for (const directory of (env.PATH ?? "").split(":")) {
    const candidate = resolve(directory || ".", "pi");
    try {
      accessSync(candidate, constants.X_OK);
      let parent = dirname(realpathSync(candidate));
      for (let depth = 0; depth < 7; depth++) {
        try { return inspectRoot(parent); } catch { /* Continue up this executable's ancestry. */ }
        const next = dirname(parent);
        if (next === parent) break;
        parent = next;
      }
    } catch { /* Ignore absent PATH entries and our own launcher. */ }
  }
  throw new Error("未找到原版 Pi；请检查 PATH，或设置 PI_UI_AGENT_ROOT 为其安装目录。");
}

export function wantsInteractivePatch(args, { stdin = false, stdout = false, disabled = false } = {}) {
  if (disabled || !stdin || !stdout) return false;
  const commands = new Set(["install", "remove", "uninstall", "update", "list", "config", "auth", "mcp"]);
  if (commands.has(args[0])) return false;
  const flags = new Set(["-p", "--print", "-h", "--help", "-v", "--version", "--export", "--list-models"]);
  for (let index = 0; index < args.length && args[index] !== "--"; index++) {
    if (flags.has(args[index]) || args[index].startsWith("--export=") || args[index].startsWith("--list-models=")) return false;
    if (args[index] === "--mode" && ["json", "rpc"].includes(args[index + 1])) return false;
    if (["--mode=json", "--mode=rpc"].includes(args[index])) return false;
  }
  return true;
}
