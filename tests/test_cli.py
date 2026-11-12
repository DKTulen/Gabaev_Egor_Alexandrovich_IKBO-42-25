"""Сквозные тесты: запуск программы целиком (все этапы)."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from depviz.cli import main

DATA = (Path(__file__).resolve().parent / "data").as_posix()


def run(extra: str, name: str = "acyclic.txt"):
    """Запускает программу с конфигом и возвращает (код, вывод, ошибки)."""
    with tempfile.TemporaryDirectory() as folder:
        config = Path(folder) / "c.yaml"
        text = (
            f"package_name: A\nrepository: {DATA}/{name}\nrepo_mode: test\n"
            f"max_depth: 5\ndot_file: {folder}/g.dot\n"
            f"image_file: {folder}/g.png\nshow_image: false\n{extra}"
        )
        config.write_text(text, encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([str(config)])
        files = sorted(item.name for item in Path(folder).iterdir())
        return code, out.getvalue(), err.getvalue(), files


class CliTests(unittest.TestCase):
    """Проверки main()."""

    def test_params(self) -> None:
        """Печатает ключи и значения."""
        code, out, _, _ = run("mode: params\n")
        self.assertEqual(code, 0)
        self.assertIn("max_depth: 5", out)
        self.assertIn("repo_mode: test", out)

    def test_direct(self) -> None:
        """Печатает прямые зависимости A."""
        code, out, _, _ = run("mode: direct\n")
        self.assertEqual(code, 0)
        self.assertIn("  - B\n  - C\n", out)

    def test_graph(self) -> None:
        """Печатает уровни и итог."""
        code, out, _, _ = run("mode: graph\n", "cyclic.txt")
        self.assertEqual(code, 0)
        self.assertIn("Уровень 1: B", out)
        self.assertIn("C -> A", out)

    def test_reverse(self) -> None:
        """Печатает тех, кто зависит от F."""
        code, out, _, _ = run("mode: reverse\nreverse_target: F\n")
        self.assertEqual(code, 0)
        self.assertIn("Уровень 1: D, E", out)

    def test_visualize(self) -> None:
        """Создаёт .dot и картинку."""
        code, out, _, files = run("mode: visualize\n")
        self.assertEqual(code, 0)
        self.assertIn("digraph", out)
        self.assertIn("g.dot", files)
        images = [name for name in files if name.startswith("g.png")]
        images += [name for name in files if name == "g.svg"]
        self.assertTrue(images)

    def test_errors(self) -> None:
        """Ошибка настроек даёт код 2, ошибка репозитория — код 3."""
        code, _, err, _ = run("mode: dance\n")
        self.assertEqual((code, "Ошибка" in err), (2, True))
        code, _, err, _ = run("mode: reverse\nreverse_target: Z\n")
        self.assertEqual((code, "Ошибка" in err), (3, True))


if __name__ == "__main__":
    unittest.main()
