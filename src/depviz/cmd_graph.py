"""Режим graph (этап 3): полный граф зависимостей с учётом глубины."""

from __future__ import annotations

from .config import Config
from .graph import build_graph, find_cycle_edges
from .report import print_cycles, print_edges, print_levels, print_summary
from .sources import make_source


def run(config: Config) -> int:
    """Строит граф зависимостей и печатает его."""
    source = make_source(config)
    graph = build_graph([source.root], source.neighbors, config.max_depth)
    print(f"Граф зависимостей {source.root} (глубина до {config.max_depth})")
    print("Узлы по уровням:")
    print_levels(graph)
    print("Рёбра (пакет -> его зависимость):")
    print_edges(graph)
    print("Циклические зависимости:")
    print_cycles(find_cycle_edges(graph.edges))
    print_summary(graph)
    return 0
