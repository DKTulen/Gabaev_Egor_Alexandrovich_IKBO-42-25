"""Тесты оболочки и команд."""
import unittest

from shell import Shell
from vfs import VFS


class ShellTest(unittest.TestCase):
    """Проверки Shell.execute."""

    def setUp(self):
        self.shell = Shell(VFS())

    def test_ls_stub(self):
        out = self.shell.execute("ls -l")
        self.assertIn("ls", out)
        self.assertIn("-l", out)

    def test_cd_stub(self):
        self.assertIn("/home", self.shell.execute("cd /home"))

    def test_unknown(self):
        self.assertIn("не найдена", self.shell.execute("foo"))

    def test_empty_line(self):
        self.assertEqual(self.shell.execute(""), "")

    def test_exit(self):
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)


if __name__ == "__main__":
    unittest.main()
