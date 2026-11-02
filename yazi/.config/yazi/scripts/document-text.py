#!/usr/bin/env python3
"""Extract PDF/Word text for piper, or read it in less without hiding errors."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def converter_command(document_format, path, width):
    """Use absolute paths so leading hyphens cannot become tool options."""
    path = str(Path(path).resolve())
    width = max(1, width)
    if document_format == "pdf":
        return ["pdftotext", "-layout", "-enc", "UTF-8", path, "-"]
    if document_format == "docx":
        return [
            "pandoc", "--sandbox", "--from=docx", "--to=plain",
            "--wrap=auto", f"--columns={width}", "--", path,
        ]
    if document_format == "doc":
        return ["antiword", "-m", "UTF-8.txt", "-w", str(width), path]
    raise ValueError(f"不支持的文档格式：{document_format}")


def exit_code(code):
    return code if code >= 0 else 128 - code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="输出文字，不启动分页器")
    parser.add_argument("--width", type=int, default=shutil.get_terminal_size().columns)
    parser.add_argument("format", choices=("pdf", "docx", "doc"))
    parser.add_argument("file")
    args = parser.parse_args(argv)

    path = Path(args.file).resolve()
    if not path.is_file():
        print(f"找不到文档：{path}", file=sys.stderr)
        return 66
    command = converter_command(args.format, path, args.width)
    if not shutil.which(command[0]):
        print(f"缺少文档转换程序：{command[0]}", file=sys.stderr)
        return 127
    if args.preview:
        return exit_code(subprocess.run(command, check=False).returncode)
    if not shutil.which("less"):
        print("缺少分页器：less", file=sys.stderr)
        return 127

    # Complete conversion before opening less: never show an empty pager as success.
    # TemporaryFile is private and automatically removed, even on conversion failure.
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(command, stdout=output, check=False)
        if result.returncode:
            return exit_code(result.returncode)
        if output.tell() == 0:
            print("未提取到文字；扫描版 PDF 请用 tdf 查看，搜索文字需要先 OCR。", file=sys.stderr)
            return 65
        output.seek(0)
        environment = dict(os.environ, LESSHISTFILE="-")
        return exit_code(subprocess.run(
            ["less", "-R"], stdin=output, env=environment, check=False,
        ).returncode)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except OSError as error:
        print(f"文档查看器错误：{error}", file=sys.stderr)
        raise SystemExit(1)
