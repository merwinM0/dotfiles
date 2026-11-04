#!/usr/bin/env python3
"""PTY display adapter; never interprets or answers package-manager prompts."""
import errno
import fcntl
import os
import pty
import re
import signal
import struct
import sys
import termios

RESET = '\033[0m'
CYAN = '\033[48;2;103;182;180m'
TRACK = '\033[48;2;60;65;75m'
# Pacman progress uses a bracketed bar followed by a percentage, including ILoveCandy.
SGR = re.compile(rb'\x1b\[[0-9;]*m')
BAR = re.compile(rb'\[((?:\x1b\[[0-9;]*m|[ =#<>CcoO.\-]){3,})\]([ \t]*)(\d{1,3})%')
STAGES = (
    (('error:', '错误：', '错误:', 'failed', '失败'), '255;183;197'),
    (('warning:', '警告：', '警告:'), '255;225;168'),
    (('==>',), '203;179;232'),
    (('checking ', '正在检查', '正在校验', 'loading package', '正在加载'), '183;230;255'),
    (('installing ', 'upgrading ', '正在安装', '正在更新', '正在升级'), '184;239;207'),
    (('removing ', '正在删除', '正在卸载'), '255;225;168'),
)


def render(data, color=True):
    def bar(match):
        percent = int(match[3])
        if percent > 100:
            return match[0]
        # Preserve the original terminal footprint, even on narrow windows.
        width = len(SGR.sub(b'', match[1]))
        filled = width * percent // 100
        if color:
            blocks = (CYAN + ' ' * filled + TRACK + ' ' * (width - filled) + RESET).encode()
        else:
            blocks = ('█' * filled + '░' * (width - filled)).encode()
        return b'[' + blocks + b']' + match[2] + match[3] + b'%'
    data = BAR.sub(bar, data)
    if color:
        for words, rgb in STAGES:
            if any(word.encode() in data.lower() for word in words):
                return ('\033[38;2;' + rgb + 'm').encode() + data + RESET.encode()
    return data


def main():
    args = sys.argv[1:]
    if args and args[0] == '--':
        args.pop(0)
    if not args:
        return 64
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        os.execvp(args[0], args)
    # pty.spawn preserves interactive stdin and restores termios on every exit.
    master = None
    previous = signal.getsignal(signal.SIGWINCH)

    def resize(*_):
        if master is not None:
            try:
                size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
                fcntl.ioctl(master, termios.TIOCSWINSZ, size)
            except OSError:
                pass

    def read(fd):
        nonlocal master
        if master is None:
            master = fd
            resize()
        try:
            data = os.read(fd, 65536)
        except OSError as error:
            if error.errno == errno.EIO:
                return b''
            raise
        # Unrecognized or split records pass through untouched; never delay prompts.
        return render(data, 'NO_COLOR' not in os.environ)

    signal.signal(signal.SIGWINCH, resize)
    try:
        status = pty.spawn(args, master_read=read)
    finally:
        signal.signal(signal.SIGWINCH, previous)
    code = os.waitstatus_to_exitcode(status)
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    sys.exit(main())
