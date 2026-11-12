"""Тесты чтения индекса Cargo через локальный HTTP-сервер (этап 2)."""

import functools
import threading
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from depviz.cargo_index import CargoIndex, index_path
from depviz.errors import RepositoryError
from depviz.sources import CargoSource

INDEX_DIR = Path(__file__).resolve().parent / "data" / "index"


class QuietHandler(SimpleHTTPRequestHandler):
    """Обработчик, который не пишет журнал запросов."""

    def log_message(self, *args) -> None:
        """Ничего не печатает."""


class IndexTests(unittest.TestCase):
    """Проверки CargoIndex и CargoSource."""

    @classmethod
    def setUpClass(cls) -> None:
        """Запускает локальный сервер с поддельным индексом."""
        handler = functools.partial(QuietHandler, directory=str(INDEX_DIR))
        cls.server = HTTPServer(("127.0.0.1", 0), handler)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Останавливает сервер."""
        cls.server.shutdown()
        cls.server.server_close()

    def test_index_path(self) -> None:
        """Схема папок индекса для имён разной длины."""
        self.assertEqual(index_path("a"), "1/a")
        self.assertEqual(index_path("ab"), "2/ab")
        self.assertEqual(index_path("abc"), "3/a/abc")
        self.assertEqual(index_path("Serde"), "se/rd/serde")

    def test_resolve(self) -> None:
        """Берётся новая версия, но не пре-релиз, не отозванная и не 2.x."""
        index = CargoIndex(self.url)
        self.assertEqual(str(index.resolve("libx", "^1.0").version), "1.2.0")
        self.assertEqual(str(index.exact("libx", "2.0.0").version), "2.0.0")

    def test_errors(self) -> None:
        """Нет пакета, нет версии, нет подходящей версии."""
        index = CargoIndex(self.url)
        with self.assertRaises(RepositoryError):
            index.versions("nothing")
        with self.assertRaises(RepositoryError):
            index.exact("libx", "9.9.9")
        with self.assertRaises(RepositoryError):
            index.resolve("libx", "^7.0")

    def test_server_down(self) -> None:
        """Недоступный сервер — понятная ошибка, а не падение."""
        with self.assertRaises(RepositoryError):
            CargoIndex("http://127.0.0.1:9").versions("libx")

    def test_source(self) -> None:
        """Прямые зависимости app: dev и необязательные пропущены."""
        source = CargoSource(self.url, "app", "1.0.0")
        found = source.neighbors(source.root)
        self.assertEqual(found, ["libx 1.2.0", "liby 0.2.5"])


if __name__ == "__main__":
    unittest.main()
