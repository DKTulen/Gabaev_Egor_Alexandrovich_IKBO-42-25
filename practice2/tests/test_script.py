"""Тесты чтения скрипта и параметров."""
import unittest

from config import Config, format_debug
from script import ScriptError, clean_line, read_script


class ScriptTest(unittest.TestCase):
    """Проверки script.py и config.py."""

    def test_clean_comment(self):
        self.assertEqual(clean_line("ls  # список"), "ls")

    def test_clean_full_comment(self):
        self.assertEqual(clean_line("# просто комментарий"), "")

    def test_missing_script(self):
        with self.assertRaises(ScriptError):
            read_script("no_such_script.emu")

    def test_debug_output(self):
        text = format_debug(Config("a.csv", None))
        self.assertIn("a.csv", text)
        self.assertIn("не задан", text)


if __name__ == "__main__":
    unittest.main()
