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

    def set_up(self) -> None:
        """Запускает локальный сервер с поддельным индексом."""
        handler = functools.partial(QuietHandler, directory=str(INDEX_DIR))
        self.server = HTTPServer(("127.0.0.1", 0), handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(
            target=self.server.serve_forever, daemon=True
        ).start()

    def tear_down(self) -> None:
        """Останавливает сервер."""
        self.server.shutdown()
        self.server.server_close()

    def test_index_path(self) -> None:
        """Схема папок индекса для имён разной длины."""
        self.assertEqual(index_path("a"), "1/a")
        self.assertEqual(index_path("ab"), "2/ab")
        self.assertEqual(index_path("abc"), "3/a/abc")
        self.assertEqual(index_path("Serde"), "se/rd/serde")

    def test_resolve(self) -> None:
        """Берётся новая версия, но не пре-релиз, не отозванная и не 2.x."""
        self.set_up()
        index = CargoIndex(self.url)
        self.assertEqual(str(index.resolve("libx", "^1.0").version), "1.2.0")
        self.assertEqual(str(index.exact("libx", "2.0.0").version), "2.0.0")
        self.tear_down()

    def test_errors(self) -> None:
        """Нет пакета, нет версии, нет подходящей версии."""
        self.set_up()
        index = CargoIndex(self.url)
        with self.assertRaises(RepositoryError):
            index.versions("nothing")
        with self.assertRaises(RepositoryError):
            index.exact("libx", "9.9.9")
        with self.assertRaises(RepositoryError):
            index.resolve("libx", "^7.0")
        self.tear_down()

    def test_server_down(self) -> None:
        """Недоступный сервер — понятная ошибка, а не падение."""
        with self.assertRaises(RepositoryError):
            CargoIndex("http://127.0.0.1:9").versions("libx")

    def test_source(self) -> None:
        """Прямые зависимости app: dev и необязательные пропущены."""
        self.set_up()
        source = CargoSource(self.url, "app", "1.0.0")
        found = source.neighbors(source.root)
        self.assertEqual(found, ["libx 1.2.0", "liby 0.2.5"])
        self.tear_down()


if __name__ == "__main__":
    unittest.main()
