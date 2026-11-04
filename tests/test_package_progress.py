"""Pure display tests: no sudo, network, or package transactions."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'package-tools/.local/libexec/package-tools/progress.py'
spec = importlib.util.spec_from_file_location('package_progress', PATH)
progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(progress)


class ProgressTest(unittest.TestCase):
    def test_regular_bar_keeps_metadata_and_percentage(self):
        output = progress.render(b'foo 10 MiB 2 MiB/s [#####     ]  50%\r')
        self.assertIn(b'foo 10 MiB 2 MiB/s ', output)
        self.assertIn(progress.CYAN.encode() + b' ' * 5, output)
        self.assertTrue(output.endswith(b'  50%\r'))

    def test_candy_sgr_is_replaced(self):
        output = progress.render(b'[\x1b[1;33mC\x1b[0;37mo o  \x1b[0m] 50%')
        self.assertIn(progress.CYAN.encode(), output)
        self.assertNotIn(b'33mC', output)

    def test_plain_blocks_without_ansi(self):
        output = progress.render(b'[====    ] 50%', False)
        self.assertEqual(output, '[████░░░░] 50%'.encode())

    def test_prompts_unknown_records_and_split_progress_passthrough(self):
        for data in (b'Password: ', b'Proceed? [Y/n]', b'[####', b'    ] 50%', b'[abcdef] 50%', b'[====] 101%'):
            self.assertEqual(progress.render(data), data)

    def test_stages_have_distinct_colors_and_keep_text(self):
        for data, rgb in ((b'==> Building foo', b'203;179;232'),
                          (b'checking keys in keyring', b'183;230;255'),
                          (b'installing foo', b'184;239;207'),
                          (b'removing foo', b'255;225;168'),
                          (b'error: failed', b'255;183;197')):
            output = progress.render(data)
            self.assertIn(data, output)
            self.assertIn(rgb, output)


if __name__ == '__main__':
    unittest.main()
