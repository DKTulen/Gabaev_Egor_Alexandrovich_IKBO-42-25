"""Тесты VFS и загрузки из CSV."""
import os
import tempfile
import unittest

from vfs import VFS, VFSError, load_csv

HEADER = "path,type,content\n"


class LoadCsvTest(unittest.TestCase):
    """Проверки load_csv и класса VFS."""

    def make_csv(self, text):
        """Создать временный CSV и вернуть путь к нему."""
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def test_nested_tree(self):
        text = HEADER + "/a/b/c,dir,\n/a/b/c/f.txt,file,aGk=\n"
        vfs = load_csv(self.make_csv(text))
        self.assertEqual(vfs.get("/a/b/c/f.txt").data, b"hi")
        self.assertTrue(vfs.get("/a/b").is_dir)

    def test_motd(self):
        vfs = load_csv(self.make_csv(HEADER + "/motd,file,SGVsbG8=\n"))
        self.assertEqual(vfs.read_motd(), "Hello")

    def test_no_motd(self):
        self.assertIsNone(VFS().read_motd())

    def test_binary_data(self):
        vfs = load_csv(self.make_csv(HEADER + "/x.bin,file,AAEC\n"))
        self.assertEqual(vfs.get("/x.bin").data, b"\x00\x01\x02")

    def test_missing_file(self):
        with self.assertRaises(VFSError):
            load_csv("no_such_file.csv")

    def test_bad_header(self):
        with self.assertRaises(VFSError):
            load_csv(self.make_csv("a,b\n1,2\n"))

    def test_bad_base64(self):
        with self.assertRaises(VFSError):
            load_csv(self.make_csv(HEADER + "/f,file,@@@\n"))

    def test_bad_type(self):
        with self.assertRaises(VFSError):
            load_csv(self.make_csv(HEADER + "/f,link,\n"))

    def test_short_row(self):
        with self.assertRaises(VFSError):
            load_csv(self.make_csv(HEADER + "/f,file\n"))

    def test_file_over_dir(self):
        with self.assertRaises(VFSError):
            load_csv(self.make_csv(HEADER + "/a,dir,\n/a,file,\n"))

    def test_get_missing(self):
        self.assertIsNone(VFS().get("/nope"))


if __name__ == "__main__":
    unittest.main()
