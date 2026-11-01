"""Тесты парсера строки."""
import unittest

from line_parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки parse_line."""

    def test_command_and_args(self):
        self.assertEqual(parse_line("ls -l /tmp"), ("ls", ["-l", "/tmp"]))

    def test_extra_spaces(self):
        self.assertEqual(parse_line("  cd    a  "), ("cd", ["a"]))

    def test_empty(self):
        self.assertEqual(parse_line("   "), ("", []))


if __name__ == "__main__":
    unittest.main()
