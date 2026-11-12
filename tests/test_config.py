"""Тесты проверки настроек (этап 1)."""

import tempfile
import unittest
from pathlib import Path

from depviz.config import DEFAULT_MODE, config_items, load_config
from depviz.errors import ConfigError

DATA = Path(__file__).resolve().parent / "data"
ACYCLIC = (DATA / "acyclic.txt").as_posix()
GOOD = (
    f"package_name: A\nrepository: {ACYCLIC}\n"
    "repo_mode: test\nmax_depth: 2\n"
)


class ConfigTests(unittest.TestCase):
    """Проверки load_config."""

    def load(self, text: str):
        """Записывает текст во временный файл и загружает настройки."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "c.yaml"
            path.write_text(text, encoding="utf-8")
            return load_config(str(path))

    def fails(self, text: str) -> None:
        """Проверяет, что конфиг вызывает ConfigError."""
        with self.assertRaises(ConfigError):
            self.load(text)

    def test_good(self) -> None:
        """Правильный конфиг загружается, значения по умолчанию на месте."""
        config = self.load(GOOD)
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.mode, DEFAULT_MODE)
        self.assertIn(("repo_mode", "test"), config_items(config))

    def test_missing_and_unknown(self) -> None:
        """Нет обязательного параметра или есть неизвестный."""
        self.fails(GOOD.replace("package_name: A\n", ""))
        self.fails(GOOD + "colour: red\n")

    def test_bad_values(self) -> None:
        """Неверные глубина, режимы, имя, файл."""
        self.fails(GOOD.replace("max_depth: 2", "max_depth: abc"))
        self.fails(GOOD.replace("max_depth: 2", "max_depth: 0"))
        self.fails(GOOD.replace("repo_mode: test", "repo_mode: x"))
        self.fails(GOOD.replace("package_name: A", "package_name: a1"))
        self.fails(GOOD + "mode: reverse\n")
        self.fails(GOOD + "mode: dance\n")

    def test_remote_checks(self) -> None:
        """Для remote нужны версия и URL."""
        base = "package_name: serde\nrepo_mode: remote\nmax_depth: 1\n"
        self.fails(base + "repository: https://x.io\n")
        self.fails(base + "repository: ftp://x\npackage_version: 1.0.0\n")
        self.fails(base + "repository: https://x.io\npackage_version: 1\n")

    def test_no_file(self) -> None:
        """Несуществующий конфиг — ошибка."""
        with self.assertRaises(ConfigError):
            load_config("no_such_file.yaml")


if __name__ == "__main__":
    unittest.main()
