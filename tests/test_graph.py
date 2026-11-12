"""Тесты тестового репозитория и обхода в ширину (этап 3)."""

import unittest
from pathlib import Path

from depviz.errors import RepositoryError
from depviz.graph import build_graph, find_cycle_edges, levels
from depviz.sources import TestSource
from depviz.test_repo import parse_test_repo

DATA = Path(__file__).resolve().parent / "data"


def make(name: str, root: str, depth: int):
    """Строит граф тестового репозитория name от корня root."""
    source = TestSource(str(DATA / name), root)
    return build_graph([source.root], source.neighbors, depth)


class GraphTests(unittest.TestCase):
    """Проверки построения графа."""

    def test_acyclic_levels(self) -> None:
        """Ромб: каждый пакет на своём уровне, повторов нет."""
        graph = make("acyclic.txt", "A", 5)
        self.assertEqual(levels(graph), [["A"], ["B", "C"], ["D", "E"], ["F"]])
        self.assertEqual(find_cycle_edges(graph.edges), [])

    def test_depth_limit(self) -> None:
        """При глубине 1 видны только прямые зависимости."""
        graph = make("acyclic.txt", "A", 1)
        self.assertEqual(levels(graph), [["A"], ["B", "C"]])
        self.assertEqual(graph.edges["B"], [])

    def test_cycle(self) -> None:
        """Цикл не зацикливает обход и находится."""
        graph = make("cyclic.txt", "A", 10)
        self.assertEqual(len(graph.depth), 4)
        found = find_cycle_edges(graph.edges)
        self.assertEqual(found, [("A", "B"), ("B", "C"), ("C", "A")])

    def test_complex(self) -> None:
        """Петля, неописанный пакет и пакет вне корня."""
        graph = make("complex.txt", "A", 10)
        self.assertIn(("B", "B"), find_cycle_edges(graph.edges))
        self.assertIn("G", graph.depth)
        self.assertNotIn("X", graph.depth)

    def test_parse_errors(self) -> None:
        """Плохие строки тестового репозитория."""
        for bad in ("A B", "a: B", "A: b", "A: B\nA: C"):
            with self.assertRaises(RepositoryError):
                parse_test_repo(bad)
        with self.assertRaises(RepositoryError):
            TestSource(str(DATA / "acyclic.txt"), "Z")
        with self.assertRaises(RepositoryError):
            TestSource(str(DATA / "missing.txt"), "A")


if __name__ == "__main__":
    unittest.main()
