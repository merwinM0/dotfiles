#!/usr/bin/env node
import { pathToFileURL } from "node:url";
import { findInstallation, wantsInteractivePatch } from "./installation.mjs";

async function main() {
  const installation = findInstallation();
  const args = process.argv.slice(2);
  let entry = installation.bundledEntry;
  if (wantsInteractivePatch(args, {
    stdin: process.stdin.isTTY, stdout: process.stdout.isTTY, disabled: process.env.PI_UI_DISABLE === "1",
  })) {
    try {
      const { applyPatch } = await import("./frame-patch.mjs");
      await applyPatch(installation.root);
      entry = installation.plainEntry;
    } catch (error) {
      // Do not block upgrades or strand the user behind an incompatible private UI API.
      process.stderr.write(`[pi-ui] ${error.message}\n[pi-ui] 本次使用原版 Pi，可设置 PI_UI_DISABLE=1 手动停用补丁。\n`);
    }
  }
  process.argv = [process.execPath, entry, ...args];
  await import(pathToFileURL(entry).href);
}

main().catch(error => {
  process.stderr.write(`[pi-ui] ${error.message}\n`);
  process.exitCode = 1;
});
