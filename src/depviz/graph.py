"""Построение графа зависимостей обходом в ширину (BFS) без рекурсии."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Set, Tuple

from .errors import RepositoryError
from .sources import split_node

Neighbors = Callable[[str], Iterable[str]]
Edge = Tuple[str, str]


@dataclass
class Graph:
    """Граф: корни, рёбра и глубина каждого узла."""

    roots: List[str]
    edges: Dict[str, List[str]]
    depth: Dict[str, int]


def unique(items: Iterable[str]) -> List[str]:
    """Убирает повторы, сохраняя порядок."""
    return list(dict.fromkeys(items))


def build_graph(
    roots: Iterable[str], neighbors: Neighbors, max_depth: int
) -> Graph:
    """Строит граф обходом в ширину не глубже max_depth уровней."""
    graph = Graph(unique(roots), {}, {})
    queue: deque = deque()
    for root in graph.roots:
        graph.depth[root] = 0
        graph.edges[root] = []
        queue.append(root)
    while queue:
        node = queue.popleft()
        if graph.depth[node] >= max_depth:
            continue
        expand_node(graph, node, neighbors, queue)
    return graph


def expand_node(
    graph: Graph, node: str, neighbors: Neighbors, queue: deque
) -> None:
    """Добавляет рёбра узла и ставит новые узлы в очередь."""
    for child in unique(neighbors(node)):
        graph.edges[node].append(child)
        if child not in graph.depth:
            graph.depth[child] = graph.depth[node] + 1
            graph.edges[child] = []
            queue.append(child)


def levels(graph: Graph) -> List[List[str]]:
    """Узлы графа, сгруппированные по глубине."""
    groups: Dict[int, List[str]] = {}
    for node, depth in graph.depth.items():
        groups.setdefault(depth, []).append(node)
    return [groups[key] for key in sorted(groups)]


def reverse_edges(edges: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Меняет направление рёбер: «кто зависит от узла»."""
    reverse: Dict[str, List[str]] = {}
    for parent, children in edges.items():
        for child in children:
            reverse.setdefault(child, []).append(parent)
    return reverse


def reachable(edges: Dict[str, List[str]], start: str) -> Set[str]:
    """Все узлы, достижимые из start (включая сам start)."""
    seen = {start}
    queue = deque([start])
    while queue:
        for child in edges.get(queue.popleft(), []):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen


def find_cycle_edges(edges: Dict[str, List[str]]) -> List[Edge]:
    """Рёбра u->v, после которых из v можно вернуться в u (цикл)."""
    cache: Dict[str, Set[str]] = {}
    cyclic: List[Edge] = []
    for parent, children in edges.items():
        for child in children:
            if child not in cache:
                cache[child] = reachable(edges, child)
            if parent in cache[child]:
                cyclic.append((parent, child))
    return cyclic


def find_targets(graph: Graph, target: str) -> List[str]:
    """Находит узлы графа, чьё имя (или полное название) равно target."""
    found = [
        n for n in graph.depth if target in (n, split_node(n)[0])
    ]
    if not found:
        raise RepositoryError(f"пакет {target} не найден в графе")
    return found
