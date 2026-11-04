#!/usr/bin/env python3
"""Offline package-helper regression tests; package managers and sudo are mocked."""

import fcntl
import json
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import struct
import subprocess
import tempfile
import termios
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "package-tools/.local/bin"
REAL_FZF = shutil.which("fzf")
MOCK = r'''#!/usr/bin/env python3
import json, os, pathlib, sys, time
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
base = pathlib.Path(os.environ['FAKE_ROOT'])
with (base / 'calls.jsonl').open('a') as out:
    out.write(json.dumps({'name': name, 'args': args, 'pid': os.getpid(), 'tty': os.isatty(0)}) + '\n')
if name == 'sudo':
    if args == ['-v']:
        sys.exit(int(os.environ.get('FAKE_AUTH_EXIT', '0')))
    assert args[0] == 'pacman', args
    os.execv(str(base / 'bin/pacman'), ['pacman', *args[1:]])
if name == 'fzf':
    code = int(os.environ.get('FAKE_FZF_EXIT', '0'))
    if code == 0:
        sys.stdout.write(os.environ.get('FAKE_SELECTION', 'alpha\n'))
    sys.exit(code)
if any(arg in args for arg in ['-Sii', '-Siia', '-Qi', '-Gpa']):
    print('Mock package information: ' + args[-1])
    sys.exit(0)
dbpath = base / 'db.json'
db = json.loads(dbpath.read_text())
listing = '-Slq' in args or '-Slqa' in args or '-Qqe' in args
if listing:
    time.sleep(float(os.environ.get('FAKE_LIST_DELAY', '0')))
    code = int(os.environ.get('FAKE_LIST_EXIT', '0'))
    if code:
        print('mock list failure', file=sys.stderr)
        sys.exit(code)
    values = os.environ.get('FAKE_PACKAGES', 'alpha\nbeta\n')
    if '-Qqe' in args:
        values = ''.join(pkg + '\n' for pkg in sorted(db))
    sys.stdout.write(values)
    sys.exit(0)
if '-Q' in args:
    time.sleep(float(os.environ.get('FAKE_QUERY_DELAY', '0')))
    code = int(os.environ.get('FAKE_QUERY_EXIT', '0'))
    if code:
        print('mock query failure', file=sys.stderr)
        sys.exit(code)
    if os.environ.get('FAKE_MALFORMED_DB'):
        print('broken-record')
    else:
        for pkg, version in sorted(db.items()):
            print(pkg, version)
    sys.exit(0)
assert '-S' in args or '-Rns' in args, (name, args)
assert '--noconfirm' not in args
packages = [pkg.removeprefix('aur/') for pkg in args[args.index('--') + 1:]]
if os.environ.get('FAKE_CONFIRM'):
    print('Proceed? [Y/n]', flush=True)
    if sys.stdin.readline().strip().lower() != 'y':
        sys.exit(1)
code = int(os.environ.get('FAKE_TRANSACTION_EXIT', '0'))
changed = [] if code or os.environ.get('FAKE_NO_CHANGE') else packages
if os.environ.get('FAKE_PARTIAL'):
    changed = packages[:1]
for pkg in changed:
    if '-Rns' in args:
        db.pop(pkg, None)
    else:
        db[pkg] = '1.0'
dbpath.write_text(json.dumps(db))
print('mock native download/install progress: 100%', flush=True)
if os.environ.get('FAKE_BAR'):
    print('foo 12 MiB 2 MiB/s [C o o o   ] 50%', flush=True)
sys.exit(code)
'''


class PackageToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="package-tools-test-")
        self.base = Path(self.temp.name)
        (self.base / "bin").mkdir()
        (self.base / "tmp").mkdir()
        for name in ("fzf", "sudo", "pacman", "yay"):
            path = self.base / "bin" / name
            path.write_text(MOCK)
            path.chmod(0o755)
        (self.base / "db.json").write_text("{}")
        (self.base / "calls.jsonl").write_text("")
        self.env = dict(os.environ)
        for key in ("NO_COLOR", "FZF_DEFAULT_OPTS", "FZF_DEFAULT_OPTS_FILE"):
            self.env.pop(key, None)
        self.env.update(
            FAKE_ROOT=str(self.base),
            PATH=str(self.base / "bin") + os.pathsep + os.environ["PATH"],
            TMPDIR=str(self.base / "tmp"),
            TERM="xterm-256color",
        )

    def tearDown(self):
        self.temp.cleanup()

    def db(self, **values):
        (self.base / "db.json").write_text(json.dumps(values))

    def calls(self):
        return [json.loads(line) for line in (self.base / "calls.jsonl").read_text().splitlines()]

    def transactions(self):
        return [
            c for c in self.calls()
            if c["name"] in {"pacman", "yay"}
            and ("-S" in c["args"] or "-Rns" in c["args"])
        ]

    def run_tool(self, mode="pac", *args, **env):
        result = subprocess.run(
            ["bash", str(BIN / mode), *args], env=dict(self.env, **env),
            cwd=self.base, capture_output=True, text=True, timeout=8,
        )
        self.assertFalse(list((self.base / "tmp").iterdir()), "Private temporary files leaked")
        return result

    def test_repository_install_verified(self):
        result = self.run_tool(FAKE_SELECTION="alpha\nbeta\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("安装成功：已确认 2", result.stderr)
        self.assertIn("alpha 1.0", result.stderr)
        self.assertEqual(len(self.transactions()), 1)
        self.assertNotIn("--noconfirm", self.transactions()[0]["args"])

    def test_aur_prefix_dedup_and_query(self):
        result = self.run_tool("aur", "keyword with spaces", FAKE_SELECTION="alpha\nbeta\nalpha\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        transaction = self.transactions()[0]["args"]
        self.assertEqual(transaction[transaction.index("--") + 1:], ["aur/alpha", "aur/beta"])
        picker = next(c for c in self.calls() if c["name"] == "fzf")["args"]
        self.assertIn("--layout=reverse", picker)
        self.assertIn("--query=keyword with spaces", picker)
        self.assertTrue(any("#BEE7E3" in arg and "#A7DFDB" in arg for arg in picker))

    def test_uninstall_verified_absent(self):
        self.db(alpha="1.0", beta="2.0", keep="3.0")
        result = self.run_tool("uninstall", FAKE_SELECTION="alpha\nbeta\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("卸载成功：已确认 2", result.stderr)
        self.assertEqual(json.loads((self.base / "db.json").read_text()), {"keep": "3.0"})

    def test_failed_command_never_succeeds_for_preinstalled_package(self):
        self.db(alpha="old")
        result = self.run_tool(FAKE_TRANSACTION_EXIT="9")
        self.assertEqual(result.returncode, 9)
        self.assertNotIn("安装成功：", result.stderr)
        self.assertIn("[已安装] alpha old", result.stderr)

    def test_zero_exit_without_install_fails_verification(self):
        result = self.run_tool(FAKE_NO_CHANGE="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("[尚未安装] alpha", result.stderr)
        self.assertNotIn("安装成功：", result.stderr)

    def test_partial_install_reports_both_states(self):
        result = self.run_tool("aur", FAKE_SELECTION="alpha\nbeta\n", FAKE_PARTIAL="1", FAKE_TRANSACTION_EXIT="7")
        self.assertEqual(result.returncode, 7)
        self.assertIn("[已安装] alpha", result.stderr)
        self.assertIn("[尚未安装] beta", result.stderr)
        self.assertNotIn("安装成功：", result.stderr)

    def test_failed_uninstall_retains_package(self):
        self.db(alpha="1.0")
        result = self.run_tool("uninstall", FAKE_TRANSACTION_EXIT="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("[仍然安装] alpha", result.stderr)
        self.assertNotIn("卸载成功：", result.stderr)

    def test_zero_exit_with_remaining_package_fails(self):
        self.db(alpha="1.0")
        result = self.run_tool("uninstall", FAKE_NO_CHANGE="1")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("卸载成功：", result.stderr)

    def test_database_error_is_not_treated_as_absence(self):
        self.db(alpha="1.0")
        result = self.run_tool("uninstall", FAKE_QUERY_EXIT="4")
        self.assertEqual(result.returncode, 4)
        self.assertIn("不能确认结果", result.stderr)
        self.assertNotIn("卸载成功：", result.stderr)

    def test_malformed_database_is_not_success(self):
        result = self.run_tool(FAKE_MALFORMED_DB="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("数据库输出异常", result.stderr)
        self.assertNotIn("安装成功：", result.stderr)

    def test_list_failure_stops_before_picker(self):
        result = self.run_tool(FAKE_LIST_EXIT="6")
        self.assertEqual(result.returncode, 6)
        self.assertFalse(any(c["name"] in {"fzf", "sudo"} for c in self.calls()))

    def test_picker_cancel_is_noop(self):
        result = self.run_tool(FAKE_FZF_EXIT="130")
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.transactions())
        self.assertFalse(any(c["name"] == "sudo" for c in self.calls()))

    def test_picker_error_is_not_cancel(self):
        result = self.run_tool(FAKE_FZF_EXIT="2")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.transactions())

    def test_auth_failure_stops_transaction(self):
        result = self.run_tool(FAKE_AUTH_EXIT="3")
        self.assertEqual(result.returncode, 3)
        self.assertFalse(self.transactions())

    def test_injected_selection_rejected(self):
        result = self.run_tool(FAKE_SELECTION="alpha;touch INJECTED\n")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.transactions())
        self.assertFalse((self.base / "INJECTED").exists())
        self.assertFalse(any(c["name"] == "sudo" for c in self.calls()))

    def test_invalid_list_rejected_before_preview(self):
        result = self.run_tool(FAKE_PACKAGES="--help\n")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(any(c["name"] == "fzf" for c in self.calls()))

    def test_empty_list_is_noop(self):
        result = self.run_tool(FAKE_PACKAGES="")
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.transactions())

    def test_no_color_supported(self):
        result = self.run_tool(NO_COLOR="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        picker = next(c for c in self.calls() if c["name"] == "fzf")["args"]
        self.assertIn("--no-color", picker)
        self.assertNotIn("\033[", result.stderr)

    @unittest.skipUnless(REAL_FZF, "fzf not installed")
    def test_real_fzf_accepts_appearance_flags_without_running_previews(self):
        self.run_tool()
        picker = next(c for c in self.calls() if c["name"] == "fzf")["args"]
        result = subprocess.run([REAL_FZF, *picker, "--filter=alpha"], input="alpha\nbeta\n", text=True, capture_output=True, timeout=4)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "alpha")

    @unittest.skipUnless(REAL_FZF, "fzf not installed")
    def test_real_picker_at_narrow_and_wide_terminal_sizes(self):
        (self.base / "bin/fzf").unlink()
        (self.base / "bin/fzf").symlink_to(REAL_FZF)
        for width in (40, 120):
            with self.subTest(width=width):
                master, slave = pty.openpty()
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 30, width, 0, 0))

                def controlling_terminal():
                    os.setsid()
                    fcntl.ioctl(0, termios.TIOCSCTTY, 0)

                process = subprocess.Popen(
                    ["bash", str(BIN / "pac")], stdin=slave, stdout=slave, stderr=slave,
                    env=dict(self.env, FAKE_LIST_DELAY="0.2"), cwd=self.base,
                    preexec_fn=controlling_terminal,
                )
                os.close(slave)
                output = bytearray()
                started = time.monotonic()
                sent = False
                try:
                    while time.monotonic() - started < 8:
                        if select.select([master], [], [], .03)[0]:
                            try:
                                data = os.read(master, 262144)
                            except OSError:
                                break
                            if not data:
                                break
                            output.extend(data)
                            if b"\x1b[6n" in data:
                                os.write(master, b"\x1b[1;1R")
                        if not sent and time.monotonic() - started > 2:
                            os.write(master, b"\x1b")
                            sent = True
                        if process.poll() is not None:
                            break
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=3)
                        self.fail("Real fzf did not cancel")
                    process.wait(timeout=3)
                finally:
                    os.close(master)
                self.assertEqual(process.returncode, 0, output.decode(errors="replace"))
                self.assertIn("搜索".encode(), output)
                self.assertIn(b"alpha", output)
                self.assertNotIn(b"unknown color", output)
                self.assertFalse(self.transactions())
                self.assertFalse(list((self.base / "tmp").iterdir()))

    def run_pty(self, extra=None, cancel=False, confirm=False, width=80):
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, width, 0, 0))
        env = dict(self.env, FAKE_LIST_DELAY="0.4", FAKE_QUERY_DELAY="0.2", **(extra or {}))
        if cancel:
            env["FAKE_LIST_DELAY"] = "20"
        if confirm:
            env["FAKE_CONFIRM"] = "1"
        process = subprocess.Popen(["bash", str(BIN / "pac")], stdin=slave, stdout=slave, stderr=slave, env=env, cwd=self.base)
        os.close(slave)
        output = bytearray()
        started = time.monotonic()
        sent = False
        deadline = started + 8
        try:
            while time.monotonic() < deadline:
                if select.select([master], [], [], .03)[0]:
                    try:
                        data = os.read(master, 262144)
                    except OSError:
                        break
                    if not data:
                        break
                    output.extend(data)
                if (
                    cancel and not sent and b"\033[?25l" in output
                    and any(call["name"] == "pacman" for call in self.calls())
                ):
                    process.send_signal(signal.SIGINT)
                    sent = True
                if confirm and not sent and b"Proceed? [Y/n]" in output:
                    os.write(master, b"n\n")
                    sent = True
                if process.poll() is not None:
                    break
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=3)
                self.fail("PTY transaction timed out")
            process.wait(timeout=3)
        finally:
            os.close(master)
        self.assertFalse(list((self.base / "tmp").iterdir()))
        return process.returncode, bytes(output)

    def test_animation_and_tty_preserved(self):
        code, output = self.run_pty(width=40)
        self.assertEqual(code, 0, output.decode(errors="replace"))
        self.assertIn("██░░░░░░".encode(), output)
        self.assertIn("░██░░░░░".encode(), output)
        self.assertIn(b"\033[38;2;167;223;219m", output)
        self.assertIn(b"\033[?25h", output)
        self.assertTrue(self.transactions()[0]["tty"])

    def test_cyan_progress_adapter_preserves_exit_and_interaction(self):
        code, output = self.run_pty(extra={"FAKE_BAR": "1"})
        self.assertEqual(code, 0, output.decode(errors="replace"))
        self.assertIn(b"\033[48;2;103;182;180m", output)
        self.assertIn(b"50%", output)
        self.assertNotIn(b"C o o o", output)
        self.assertTrue(self.transactions()[0]["tty"])

    def test_progress_opt_out_keeps_native_output(self):
        code, output = self.run_pty(extra={"FAKE_BAR": "1", "PACKAGE_TOOLS_PROGRESS": "0"})
        self.assertEqual(code, 0)
        self.assertIn(b"C o o o", output)
        self.assertNotIn(b"\033[48;2;103;182;180m", output)

    def test_transaction_confirmation_stays_interactive(self):
        code, output = self.run_pty(confirm=True)
        self.assertEqual(code, 1, output.decode(errors="replace"))
        self.assertIn(b"Proceed? [Y/n]", output)
        self.assertNotIn("安装成功：".encode(), output)
        self.assertTrue(self.transactions()[0]["tty"])

    def test_cancel_loader_restores_cursor_and_cleans_child(self):
        code, output = self.run_pty(cancel=True)
        self.assertEqual(code, 130, output.decode(errors="replace"))
        self.assertIn(b"\033[?25h", output)
        self.assertFalse(self.transactions())
        query = next(c for c in self.calls() if c["name"] == "pacman")
        with self.assertRaises(ProcessLookupError):
            os.kill(query["pid"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
