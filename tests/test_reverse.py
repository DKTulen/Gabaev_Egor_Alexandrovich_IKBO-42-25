"""Тесты обратных зависимостей (этап 4)."""

import unittest
from pathlib import Path

from depviz.errors import RepositoryError
from depviz.graph import build_graph, find_targets, levels, reverse_edges
from depviz.sources import TestSource

DATA = Path(__file__).resolve().parent / "data"


def dependents(name: str, root: str, target: str, depth: int):
    """Уровни обратных зависимостей target в графе от root."""
    source = TestSource(str(DATA / name), root)
    forward = build_graph([source.root], source.neighbors, depth)
    reverse = reverse_edges(forward.edges)
    roots = find_targets(forward, target)
    result = build_graph(roots, lambda n: reverse.get(n, []), depth)
    return levels(result)


class ReverseTests(unittest.TestCase):
    """Проверки обратного обхода."""

    def test_acyclic(self) -> None:
        """От F зависят D и E, затем B и C, затем A."""
        result = dependents("acyclic.txt", "A", "F", 5)
        self.assertEqual(result, [["F"], ["D", "E"], ["B", "C"], ["A"]])

    def test_depth_limit(self) -> None:
        """Глубина ограничивает и прямой, и обратный обход."""
        result = dependents("acyclic.txt", "A", "C", 1)
        self.assertEqual(result, [["C"], ["A"]])
        result = dependents("acyclic.txt", "A", "D", 2)
        self.assertEqual(result, [["D"], ["B", "C"], ["A"]])
        with self.assertRaises(RepositoryError):
            dependents("acyclic.txt", "A", "F", 2)

    def test_nobody(self) -> None:
        """От корня никто не зависит."""
        self.assertEqual(dependents("acyclic.txt", "A", "A", 5), [["A"]])

    def test_cycle(self) -> None:
        """В цикле обратный обход тоже завершается."""
        result = dependents("complex.txt", "A", "D", 10)
        self.assertEqual(result[0], ["D"])
        self.assertEqual(sorted(sum(result, [])), ["A", "B", "C", "D"])

    def test_unknown_target(self) -> None:
        """Пакета нет в графе — ошибка."""
        with self.assertRaises(RepositoryError):
            dependents("acyclic.txt", "A", "Z", 5)


if __name__ == "__main__":
    unittest.main()
