#!/usr/bin/env python3
"""Fish/tmux regression tests using isolated sockets and disposable panes."""

import fcntl
import os
from pathlib import Path
import pty
import re
import select
import shutil
import struct
import subprocess
import tempfile
import termios
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT / 'fish/.config/fish/functions'
FUNCTION = FUNCTIONS / 'tmkeys.fish'
CONFIG = ROOT / 'tmux/.tmux.conf'
FISH = shutil.which('fish')
TMUX = shutil.which('tmux')
KEYS = {
    **{f'M-{n}': b'\x1b' + str(n).encode() for n in range(10)},
    **{f'M-{c}': b'\x1b' + c.encode() for c in 'dhjkqrstvw'},
    'M-Enter': b'\x1b\r',
    'M-Left': b'\x1b[1;3D',
    'M-Right': b'\x1b[1;3C',
    'M-Up': b'\x1b[1;3A',
    'M-Down': b'\x1b[1;3B',
    'M-S-Left': b'\x1b[1;4D',
    'M-S-Right': b'\x1b[1;4C',
    'M-S-Up': b'\x1b[1;4A',
    'M-S-Down': b'\x1b[1;4B',
}
RECEIVER = """import os, sys, tty
tty.setraw(0)
with open(sys.argv[1], 'ab', buffering=0) as output:
    print('READY', flush=True)
    while True:
        data = os.read(0, 4096)
        if not data:
            break
        output.write(data)
"""


@unittest.skipUnless(FISH, 'fish is required')
class FunctionTests(unittest.TestCase):
    def invoke(self, *args, **overrides):
        env = dict(os.environ)
        env.pop('TMUX', None)
        env.pop('TMUX_PANE', None)
        env.update(overrides)
        return subprocess.run(
            [FISH, '--no-config', '-c', 'source "$argv[1]"; tmkeys $argv[2..-1]',
             str(FUNCTION), *args],
            env=env, capture_output=True, text=True, timeout=5,
        )

    def test_fish_syntax(self):
        for path in FUNCTIONS.glob('*.fish'):
            with self.subTest(path=path.name):
                result = subprocess.run([FISH, '--no-config', '--no-execute', str(path)],
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_help_without_tmux(self):
        result = self.invoke('--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('tmkeys fish', result.stdout)

    def test_outside_tmux_does_not_succeed(self):
        result = self.invoke('fish')
        self.assertEqual(result.returncode, 1)
        self.assertIn('不在 tmux', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_empty_context_does_not_succeed(self):
        self.assertEqual(self.invoke('tmux', TMUX='', TMUX_PANE='').returncode, 1)

    def test_invalid_argument(self):
        result = self.invoke('invalid')
        self.assertEqual(result.returncode, 2)
        self.assertIn('未知模式', result.stderr)

    def test_extra_argument(self):
        self.assertEqual(self.invoke('tmux', 'fish').returncode, 2)

    def test_empty_argument(self):
        self.assertEqual(self.invoke('').returncode, 2)

    def test_missing_tmux(self):
        result = self.invoke('status', TMUX='unused,1,0', TMUX_PANE='%0', PATH='')
        self.assertEqual(result.returncode, 127)
        self.assertIn('找不到 tmux', result.stderr)

    def test_read_failure_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock = Path(tmp) / 'tmux'
            mock.write_text('#!/bin/sh\nexit 23\n')
            mock.chmod(0o755)
            result = self.invoke('fish', TMUX='unused,1,0', TMUX_PANE='%0', PATH=tmp)
        self.assertEqual(result.returncode, 23)
        self.assertEqual(result.stdout, '')

    def test_write_failure_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            mock = Path(tmp) / 'tmux'
            mock.write_text('#!/bin/sh\ncase "$1" in\ndisplay-message) echo tmux;;\n*) exit 24;;\nesac\n')
            mock.chmod(0o755)
            result = self.invoke('fish', TMUX='unused,1,0', TMUX_PANE='%0', PATH=tmp)
        self.assertEqual(result.returncode, 24)
        self.assertEqual(result.stdout, '')

    def test_documentation_covers_functions(self):
        text = (FUNCTIONS / '函数说明.md').read_text()
        for path in FUNCTIONS.glob('*.fish'):
            self.assertIn(f'`{path.stem}`', text)


@unittest.skipUnless(FISH and TMUX, 'fish and tmux are required')
class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tmkeys-test-')
        self.path = Path(self.temp.name)
        self.cwd = self.path / '目录 with spaces'
        self.cwd.mkdir()
        self.socket = str(self.path / 'socket')
        self.base = [TMUX, '-S', self.socket]
        self.client_pid = self.client_fd = None
        self.env = dict(os.environ, TERM='xterm-256color')
        self.env.pop('TMUX', None)
        self.env.pop('TMUX_PANE', None)
        self.log = self.path / 'input.bin'
        self.addCleanup(self.cleanup)
        result = self.tmux('-f', '/dev/null', 'new-session', '-d', '-P', '-F', '#{pane_id}',
                           '-s', 'test', '-n', 'shell', '-x', '120', '-y', '40', '-c', str(self.cwd),
                           'python3', '-u', '-c', RECEIVER, str(self.log))
        self.pane = result.stdout.strip()
        self.tmux('source-file', str(CONFIG))
        self.tmux('set-option', '-g', 'default-shell', '/bin/sh')
        self.tmux('set-option', '-g', 'default-command', 'exec sleep 120')
        self.env['TMUX'] = f'{self.socket},{self.query("#{pid}")},0'
        self.env['TMUX_PANE'] = self.pane
        self.wait_for(self.log.exists)

    def cleanup(self):
        self.tmux('kill-server', check=False)
        if self.client_fd is not None:
            os.close(self.client_fd)
        if self.client_pid is not None:
            os.waitpid(self.client_pid, 0)
        self.temp.cleanup()

    def tmux(self, *args, check=True):
        return subprocess.run(self.base + list(args), env=self.env, text=True,
                              capture_output=True, check=check, timeout=5)

    def query(self, fmt, pane=None):
        return self.tmux('display-message', '-p', '-t', pane or self.pane, fmt).stdout.strip()

    def fish(self, *args):
        return subprocess.run(
            [FISH, '--no-config', '-c', 'source "$argv[1]"; tmkeys $argv[2..-1]',
             str(FUNCTION), *args], env=self.env, text=True, capture_output=True, timeout=5,
        )

    def mode(self, pane=None):
        return self.query('#{@altkeys_mode}', pane)

    def wait_for(self, condition, timeout=3):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if condition():
                return
            time.sleep(.02)
        self.fail('Timed out waiting for isolated tmux state')

    def attach(self):
        self.client_pid, self.client_fd = pty.fork()
        if self.client_pid == 0:
            env = dict(self.env)
            env.pop('TMUX', None)
            env.pop('TMUX_PANE', None)
            os.execvpe(TMUX, self.base + ['attach-session', '-t', 'test'], env)
        fcntl.ioctl(self.client_fd, termios.TIOCSWINSZ, struct.pack('HHHH', 40, 120, 0, 0))
        self.wait_for(lambda: bool(self.tmux('list-clients').stdout.strip()))
        self.drain(.1)

    def drain(self, seconds=.08):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if select.select([self.client_fd], [], [], .01)[0]:
                try:
                    os.read(self.client_fd, 65536)
                except OSError:
                    break

    def press(self, keys):
        os.write(self.client_fd, keys)
        self.drain()

    def test_default_status_and_autoload(self):
        self.assertEqual(self.mode(), 'tmux')
        self.assertEqual(self.fish().stdout, 'tmux\n')
        result = subprocess.run(
            [FISH, '--no-config', '-c', 'set -p fish_function_path "$argv[1]"; tmkeys status',
             str(FUNCTIONS)], env=self.env, text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'tmux\n')

    def test_set_and_toggle(self):
        for command, expected in [('fish', 'fish'), ('toggle', 'tmux'),
                                  ('toggle', 'fish'), ('tmux', 'tmux')]:
            with self.subTest(command=command):
                result = self.fish(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected + '\n')
                self.assertEqual(self.mode(), expected)

    def test_scope_and_new_pane_default(self):
        other = self.tmux('split-window', '-h', '-P', '-F', '#{pane_id}').stdout.strip()
        self.assertEqual(self.fish('fish').returncode, 0)
        self.assertEqual(self.mode(), 'fish')
        self.assertEqual(self.mode(other), 'tmux')
        new = self.tmux('split-window', '-v', '-t', self.pane, '-P', '-F', '#{pane_id}').stdout.strip()
        self.assertEqual(self.mode(new), 'tmux')

    def test_status_bar_shows_pane_mode(self):
        self.assertIn('tmux', self.query('#{E:status-right}'))
        self.assertEqual(self.fish('fish').returncode, 0)
        self.assertIn('fish', self.query('#{E:status-right}'))

    def test_reload_preserves_pane_mode(self):
        self.assertEqual(self.fish('fish').returncode, 0)
        self.tmux('source-file', str(CONFIG))
        self.assertEqual(self.mode(), 'fish')

    def test_unconfigured_server_reports_error(self):
        self.tmux('set-option', '-gu', '@altkeys_mode')
        result = self.fish('fish')
        self.assertEqual(result.returncode, 1)
        self.assertIn('先加载配置', result.stderr)

    def test_stale_pane_reports_error(self):
        self.env['TMUX_PANE'] = '%99999999'
        result = self.fish('fish')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_all_custom_keys_have_mode_guard(self):
        bindings = self.tmux('list-keys', '-T', 'root').stdout
        found = {}
        for line in bindings.splitlines():
            match = re.search(r'-T root (M-\S+)\s+(.*)', line)
            if match and match[1] in KEYS:
                found[match[1]] = match[2]
        self.assertEqual(set(found), set(KEYS))
        self.assertEqual(len(KEYS), 29)
        for key, command in found.items():
            with self.subTest(key=key):
                self.assertIn('#{==:#{@altkeys_mode},fish}', command)
                self.assertIn(f'send-keys {key}', command)
        self.assertIn('confirm-before', found['M-q'])
        self.assertEqual(self.tmux('show-options', '-gv', 'prefix').stdout.strip(), 'C-b')

    def test_fish_mode_forwards_all_managed_keys(self):
        self.attach()
        self.assertEqual(self.fish('fish').returncode, 0)
        expected = b''
        for key, data in KEYS.items():
            with self.subTest(key=key):
                self.press(data)
                expected += data
                self.wait_for(lambda: self.log.read_bytes() == expected)
                self.assertEqual(self.query('#{window_panes}'), '1')
        self.assertEqual(self.mode(), 'fish')

    def test_tmux_mode_splits_and_preserves_directory(self):
        self.attach()
        self.press(KEYS['M-h'])
        self.wait_for(lambda: self.query('#{window_panes}') == '2')
        self.press(KEYS['M-v'])
        self.wait_for(lambda: self.query('#{window_panes}') == '3')
        paths = self.tmux('list-panes', '-F', '#{pane_current_path}').stdout.splitlines()
        self.assertEqual(paths, [str(self.cwd)] * 3)
        self.assertEqual(self.log.read_bytes(), b'')

    def test_alt_enter_creates_window(self):
        self.attach()
        self.press(KEYS['M-Enter'])
        self.wait_for(lambda: self.query('#{session_windows}') == '2')
        new = self.tmux('display-message', '-p', '#{pane_id}').stdout.strip()
        self.assertEqual(self.mode(new), 'tmux')
        self.assertEqual(self.query('#{pane_current_path}', new), str(self.cwd))

    def test_window_edge_navigation_and_zero(self):
        self.tmux('new-window', '-d')
        self.attach()
        self.press(KEYS['M-Right'])
        self.wait_for(lambda: self.tmux('display-message', '-p', '#{window_index}').stdout.strip() == '1')
        self.press(KEYS['M-Left'])
        self.wait_for(lambda: self.tmux('display-message', '-p', '#{window_index}').stdout.strip() == '0')
        self.press(KEYS['M-1'])
        self.wait_for(lambda: self.tmux('display-message', '-p', '#{window_index}').stdout.strip() == '1')
        self.press(KEYS['M-0'])
        self.wait_for(lambda: self.tmux('display-message', '-p', '#{window_index}').stdout.strip() == '0')

    def test_close_requires_confirmation(self):
        self.attach()
        self.press(KEYS['M-q'])
        self.assertEqual(self.query('#{window_panes}'), '1')
        self.press(b'n')
        self.assertEqual(self.query('#{window_panes}'), '1')
        self.assertEqual(self.log.read_bytes(), b'')

    def test_prefix_remains_available_in_fish_mode(self):
        self.attach()
        self.assertEqual(self.fish('fish').returncode, 0)
        self.press(b'\x02:')
        self.press(b'set-option -p @test_prefix works\r')
        self.assertEqual(self.query('#{@test_prefix}'), 'works')
        self.assertEqual(self.log.read_bytes(), b'')

    def test_copy_mode_keeps_its_own_bindings(self):
        self.attach()
        self.assertEqual(self.fish('fish').returncode, 0)
        self.tmux('copy-mode', '-t', self.pane)
        self.press(KEYS['M-v'])
        self.assertEqual(self.query('#{pane_mode}'), 'copy-mode')
        self.assertEqual(self.query('#{window_panes}'), '1')
        self.press(b'q')
        self.assertEqual(self.query('#{pane_in_mode}'), '0')
        self.assertEqual(self.mode(), 'fish')
        self.assertEqual(self.log.read_bytes(), b'')

    def test_unmanaged_fish_shortcuts_are_untouched(self):
        self.attach()
        data = b''.join(b'\x1b' + char.encode() for char in 'zmxpi')
        self.press(data)
        self.wait_for(lambda: self.log.read_bytes() == data)


if __name__ == '__main__':
    unittest.main()
