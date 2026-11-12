"""Тесты описания Graphviz и SVG (этап 5)."""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from depviz.dot import graph_to_dot, quote
from depviz.graph import build_graph, find_cycle_edges
from depviz.sources import TestSource
from depviz.svg import graph_to_svg, svg_edge

DATA = Path(__file__).resolve().parent / "data"


def prepare(name: str):
    """Граф и рёбра цикла для тестового файла."""
    source = TestSource(str(DATA / name), "A")
    graph = build_graph([source.root], source.neighbors, 5)
    return graph, find_cycle_edges(graph.edges)


class VisualTests(unittest.TestCase):
    """Проверки dot и svg."""

    def test_quote(self) -> None:
        """Кавычки и обратная косая экранируются."""
        self.assertEqual(quote('a"b'), '"a\\"b"')

    def test_dot(self) -> None:
        """В DOT есть заголовок, рёбра и красные рёбра цикла."""
        graph, cyclic = prepare("cyclic.txt")
        text = graph_to_dot(graph, cyclic)
        self.assertTrue(text.startswith('digraph "A" {'))
        self.assertIn('"A" -> "B" [color=red];', text)
        self.assertIn('"C" -> "D";', text)
        self.assertTrue(text.rstrip().endswith("}"))

    def test_svg(self) -> None:
        """SVG — корректный XML с узлом для каждого пакета."""
        graph, cyclic = prepare("acyclic.txt")
        root = ET.fromstring(graph_to_svg(graph, cyclic))
        tag = "{http://www.w3.org/2000/svg}text"
        texts = [item.text for item in root.iter(tag)]
        self.assertEqual(sorted(texts), ["A", "B", "C", "D", "E", "F"])

    def test_back_edge(self) -> None:
        """Ребро назад и петля идут дугой под узлами, а не поверх них."""
        back = svg_edge((300, 30), (30, 30), True)
        self.assertIn("C395,119 125,119 125,64", back)
        loop = svg_edge((30, 30), (30, 30), True)
        self.assertIn("M103,64 C103,119 147,119 147,64", loop)


if __name__ == "__main__":
    unittest.main()
