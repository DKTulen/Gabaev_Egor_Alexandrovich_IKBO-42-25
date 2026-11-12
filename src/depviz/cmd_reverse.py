"""Режим reverse (этап 4): обратные зависимости заданного пакета."""

from __future__ import annotations

from .config import Config
from .graph import build_graph, find_targets, reverse_edges
from .report import print_levels
from .sources import make_source


def run(config: Config) -> int:
    """Печатает пакеты, которые зависят от reverse_target."""
    source = make_source(config)
    forward = build_graph([source.root], source.neighbors, config.max_depth)
    targets = find_targets(forward, config.reverse_target)
    reverse = reverse_edges(forward.edges)
    result = build_graph(
        targets, lambda node: reverse.get(node, []), config.max_depth
    )
    print(f"Обратные зависимости пакета {config.reverse_target}:")
    if len(result.depth) == len(result.roots):
        print("  (от пакета никто не зависит)")
    print_levels(result, skip_roots=True)
    return 0
