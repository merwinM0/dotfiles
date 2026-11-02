#!/usr/bin/env python3
"""Offline regression tests; never install packages or read personal documents."""

import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "yazi/.config/yazi"
SCRIPT = CONFIG / "scripts/document-text.py"
SPEC = importlib.util.spec_from_file_location("document_text", SCRIPT)
DOCUMENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DOCUMENT)


def sample_pdf(path):
    """Create a minimal text PDF without external libraries."""
    stream = b"BT /F1 12 Tf 72 720 Td (Yazi document preview test) Tj ET\n"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, content in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode() + content + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    path.write_bytes(data)


class ConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = tomllib.loads((CONFIG / "yazi.toml").read_text())

    def test_pdf_prefers_terminal_viewer_with_fallbacks(self):
        for key, value in (("mime", "application/pdf"), ("url", "*.pdf")):
            rule = next(rule for rule in self.config["open"]["rules"] if rule.get(key) == value)
            self.assertEqual(rule["use"], ["Tdf", "PdfText", "Zathura"])

    def test_word_extensions_route_to_distinct_readers(self):
        rules = {rule.get("url"): rule for rule in self.config["open"]["rules"]}
        self.assertEqual(rules["*.docx"]["use"], ["Doxx", "DocxText"])
        self.assertEqual(rules["*.doc"]["use"], ["Doc"])
        self.assertNotIn("application/vnd.openxmlformats-officedocument.*", rules)

    def test_terminal_openers_block_without_detaching(self):
        for name in ("Tdf", "Doxx", "PdfText", "DocxText", "Doc"):
            opener = self.config["opener"][name][0]
            self.assertTrue(opener["block"])
            self.assertFalse(opener.get("orphan", False))
            self.assertIn("%s1", opener["run"])
            self.assertNotIn('"%s1"', opener["run"])

    def test_word_preview_does_not_replace_builtin_pdf_preview(self):
        rules = self.config["plugin"]["prepend_previewers"]
        for extension, document_format in (("*.docx", "docx"), ("*.doc", "doc")):
            rule = next(rule for rule in rules if rule.get("url") == extension)
            self.assertIn("piper -- ", rule["run"])
            self.assertIn(f'{document_format} "$1"', rule["run"])
            self.assertIn('--width "$w"', rule["run"])
        self.assertFalse(any(rule.get("mime") == "application/pdf" for rule in rules))
        self.assertNotIn("previewers", self.config["plugin"])

    def test_piper_version_is_recorded(self):
        manifest = tomllib.loads((CONFIG / "package.toml").read_text())
        dependency = next(item for item in manifest["plugin"]["deps"]
                          if item["use"] == "yazi-rs/plugins:piper")
        self.assertTrue(dependency["rev"])
        self.assertTrue(dependency["hash"])

    def test_preview_keys_are_not_duplicated(self):
        keymap = tomllib.loads((CONFIG / "keymap.toml").read_text())["mgr"]["keymap"]
        for key, action in (("<A-Up>", "seek -1"), ("<A-Down>", "seek 1")):
            matches = [item for item in keymap if item["on"] == key]
            self.assertEqual([item["run"] for item in matches], [action])


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "-中文 空格 ; $(echo unsafe).docx"
        self.path.write_bytes(b"test")

    def test_docx_command_preserves_filename_as_one_argument(self):
        command = DOCUMENT.converter_command("docx", self.path, 42)
        self.assertIn("--sandbox", command)
        self.assertIn("--columns=42", command)
        self.assertEqual(command[-2:], ["--", str(self.path)])

    def test_pdf_uses_utf8_and_layout(self):
        command = DOCUMENT.converter_command("pdf", self.path, 80)
        self.assertEqual(command, ["pdftotext", "-layout", "-enc", "UTF-8", str(self.path), "-"])

    def test_legacy_doc_uses_utf8_and_absolute_path(self):
        command = DOCUMENT.converter_command("doc", "-报告.doc", 0)
        self.assertEqual(command[:5], ["antiword", "-m", "UTF-8.txt", "-w", "1"])
        self.assertTrue(Path(command[-1]).is_absolute())

    def test_missing_file_returns_error_without_running_tools(self):
        with patch.object(DOCUMENT.subprocess, "run") as run, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(DOCUMENT.main(["docx", str(self.path) + ".missing"]), 66)
        run.assert_not_called()

    def test_missing_converter_returns_error(self):
        with patch.object(DOCUMENT.shutil, "which", return_value=None), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(DOCUMENT.main(["docx", str(self.path)]), 127)

    def test_preview_preserves_converter_failure(self):
        with patch.object(DOCUMENT.shutil, "which", return_value="/mock/tool"), \
             patch.object(DOCUMENT.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)) as run:
            self.assertEqual(DOCUMENT.main(["--preview", "docx", str(self.path)]), 7)
            self.assertEqual(run.call_count, 1)

    def test_conversion_failure_never_opens_pager(self):
        with patch.object(DOCUMENT.shutil, "which", return_value="/mock/tool"), \
             patch.object(DOCUMENT.subprocess, "run", return_value=subprocess.CompletedProcess([], 9)) as run:
            self.assertEqual(DOCUMENT.main(["docx", str(self.path)]), 9)
            self.assertEqual(run.call_count, 1)

    def test_empty_extraction_never_opens_pager(self):
        with patch.object(DOCUMENT.shutil, "which", return_value="/mock/tool"), \
             patch.object(DOCUMENT.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(DOCUMENT.main(["pdf", str(self.path)]), 65)
            self.assertEqual(run.call_count, 1)

    def test_pager_gets_completed_text_without_recording_history(self):
        def run(command, **kwargs):
            if command[0] == "pandoc":
                kwargs["stdout"].write("测试内容\n".encode())
            else:
                self.assertEqual(command, ["less", "-R"])
                self.assertEqual(kwargs["stdin"].read().decode(), "测试内容\n")
                self.assertEqual(kwargs["env"]["LESSHISTFILE"], "-")
            return subprocess.CompletedProcess(command, 0)

        with patch.object(DOCUMENT.shutil, "which", return_value="/mock/tool"), \
             patch.object(DOCUMENT.subprocess, "run", side_effect=run) as mocked:
            self.assertEqual(DOCUMENT.main(["docx", str(self.path)]), 0)
            self.assertEqual(mocked.call_count, 2)


class PreviewIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
    def test_real_docx_preview_with_chinese_spaces_and_leading_hyphen(self):
        path = self.root / "-中文 报告.DOCX"
        subprocess.run(["pandoc", "--from=markdown", "--to=docx", "-o", str(path)],
                       input="# 测试报告\n\n中文预览成功。\n".encode(), check=True)
        result = subprocess.run([sys.executable, str(SCRIPT), "--preview", "--width", "40", "docx", str(path)],
                                capture_output=True, text=True, check=True)
        self.assertIn("测试报告", result.stdout)
        self.assertIn("中文预览成功", result.stdout)

    @unittest.skipUnless(shutil.which("pdftotext"), "pdftotext is not installed")
    def test_real_pdf_text_extraction(self):
        path = self.root / "-PDF 预览.pdf"
        sample_pdf(path)
        result = subprocess.run([sys.executable, str(SCRIPT), "--preview", "pdf", str(path)],
                                capture_output=True, text=True, check=True)
        self.assertIn("Yazi document preview test", result.stdout)

    @unittest.skipUnless(shutil.which("pdftoppm"), "pdftoppm is not installed")
    def test_pdf_can_be_rendered_for_builtin_preview(self):
        path = self.root / "预览.pdf"
        sample_pdf(path)
        subprocess.run(["pdftoppm", "-f", "1", "-singlefile", "-scale-to", "200", "-png",
                        str(path), str(self.root / "page")], capture_output=True, check=True)
        self.assertTrue((self.root / "page.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))


if __name__ == "__main__":
    unittest.main()
