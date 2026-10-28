#!/usr/bin/env python3
"""Display one image silently; Enter restores the terminal and returns to Yazi."""

import copy
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import termios


# Legacy CR/LF, Kitty/CSI-u Enter (including modifiers), and xterm modifyOtherKeys.
CSI_ENTER = re.compile(
    rb"\x1b\[13(?::[0-9:]*)?(?:;[0-9]+(?::([123]))?)?(?:;[0-9:]+)?u"
)
XTERM_ENTER = re.compile(rb"\x1b\[27;[0-9]+;13~")


def open_terminal():
    """Find the real terminal even when the opener's stdin is /dev/null."""
    for descriptor in (0, 1, 2):
        if os.isatty(descriptor):
            try:
                return os.open(os.ttyname(descriptor), os.O_RDWR | os.O_NOCTTY)
            except OSError:
                continue
    try:
        return os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
    except OSError:
        return None


def wait_for_enter(descriptor):
    attributes = copy.deepcopy(termios.tcgetattr(descriptor))
    attributes[0] &= ~(termios.IGNCR | termios.ICRNL | termios.INLCR)
    attributes[3] &= ~(termios.ICANON | termios.ECHO)
    attributes[6][termios.VMIN] = 1
    attributes[6][termios.VTIME] = 0
    termios.tcsetattr(descriptor, termios.TCSANOW, attributes)

    sequence = bytearray()
    while True:
        byte = os.read(descriptor, 1)
        if not byte or byte in (b"\r", b"\n"):
            return
        if byte == b"\x03":
            raise KeyboardInterrupt
        if byte == b"\x1b":
            sequence.clear()
            sequence.extend(byte)
            continue
        if not sequence:
            continue
        sequence.extend(byte)
        if len(sequence) > 64:
            sequence.clear()
            continue
        # Wait for the final byte of a CSI sequence; ignore unrelated responses.
        if len(sequence) < 3 or not 0x40 <= byte[0] <= 0x7E:
            continue
        match = CSI_ENTER.fullmatch(sequence)
        if match is not None and match.group(1) != b"3":
            return  # Press/repeat, not the release of the key used to open Yazi.
        if XTERM_ENTER.fullmatch(sequence):
            return
        sequence.clear()


def interrupt(signum, _frame):
    raise SystemExit(128 + signum)


def main():
    if len(sys.argv) < 2:
        print("没有指定图片。", file=sys.stderr)
        return 64
    local = Path.home() / ".local/libexec/timg-images"
    viewer = str(local) if os.access(local, os.X_OK) else shutil.which("timg")
    if not viewer:
        print("找不到 timg。", file=sys.stderr)
        return 127

    descriptor = open_terminal()
    original = termios.tcgetattr(descriptor) if descriptor is not None else None
    alternate_screen = False
    try:
        if descriptor is not None:
            size = os.get_terminal_size(descriptor)
            columns, rows = max(1, size.columns), max(1, size.lines - 1)
            # Isolate Sixel/image output so it cannot cover Yazi after returning.
            os.write(descriptor, b"\x1b[?1049h\x1b[2J\x1b[H")
            alternate_screen = True
        else:
            columns, rows = 80, 23
        command = [
            viewer, "-I", "--clear", "--center", "--frames=1",
            "-g", f"{columns}x{rows}", "--", sys.argv[1],
        ]
        # Show only the current/first image: one Enter always returns to Yazi,
        # rather than silently advancing through all selected images.
        completed = subprocess.run(
            command, stdin=descriptor, stdout=descriptor, stderr=descriptor,
            check=False,
        )
        if completed.returncode:
            return completed.returncode if completed.returncode > 0 else 128 - completed.returncode
        if descriptor is not None:
            wait_for_enter(descriptor)
        return 0
    finally:
        if descriptor is not None:
            try:
                if alternate_screen:
                    cleanup = b"\x1b[0m\x1b[2J\x1b[H"
                    if os.environ.get("KITTY_WINDOW_ID") or os.environ.get("TERM") in {
                        "xterm-kitty", "xterm-ghostty",
                    }:
                        cleanup += b"\x1b_Ga=d,d=A\x1b\\"
                    os.write(descriptor, cleanup + b"\x1b[?1049l\x1b[?25h")
            finally:
                try:
                    # Discard queued Enter tails/replies; restore every tty flag.
                    termios.tcsetattr(descriptor, termios.TCSAFLUSH, original)
                finally:
                    os.close(descriptor)


if __name__ == "__main__":
    for event in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(event, interrupt)
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (OSError, termios.error) as error:
        print(f"图片查看器错误：{error}", file=sys.stderr)
        raise SystemExit(1)
