"""Текстовый вывод графа на экран."""

from __future__ import annotations

from typing import List

from .graph import Edge, Graph, levels


def print_levels(graph: Graph, skip_roots: bool = False) -> None:
    """Печатает узлы по уровням; при skip_roots пропускает уровень 0."""
    for number, nodes in enumerate(levels(graph)):
        if skip_roots and not number:
            continue
        print(f"  Уровень {number}: {', '.join(nodes)}")


def print_edges(graph: Graph) -> None:
    """Печатает рёбра в виде «пакет -> зависимость»."""
    for parent, children in graph.edges.items():
        for child in children:
            print(f"  {parent} -> {child}")


def print_cycles(cyclic: List[Edge]) -> None:
    """Печатает рёбра, входящие в циклические зависимости."""
    if not cyclic:
        print("  циклов нет")
        return
    for parent, child in cyclic:
        print(f"  {parent} -> {child}")


def print_summary(graph: Graph) -> None:
    """Печатает число узлов и рёбер."""
    edge_count = sum(len(items) for items in graph.edges.values())
    print(f"Всего узлов: {len(graph.depth)}, рёбер: {edge_count}")
