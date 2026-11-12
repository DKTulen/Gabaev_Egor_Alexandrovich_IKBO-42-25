"""Текстовое описание графа на языке Graphviz (DOT)."""

from __future__ import annotations

from typing import Iterable, List, Tuple

from .graph import Graph

CYCLE_ATTR = " [color=red]"
ROOT_ATTR = " [style=filled, fillcolor=lightblue]"


def quote(text: str) -> str:
    """Оборачивает текст в кавычки и экранирует спецсимволы."""
    safe = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{safe}"'


def graph_to_dot(graph: Graph, cyclic: Iterable[Tuple[str, str]]) -> str:
    """Возвращает текст графа на языке Graphviz."""
    cycle_set = set(cyclic)
    lines: List[str] = [
        f"digraph {quote(graph.roots[0])} {{",
        "  rankdir=LR;",
        "  node [shape=box];",
    ]
    for root in graph.roots:
        lines.append(f"  {quote(root)}{ROOT_ATTR};")
    for parent, children in graph.edges.items():
        for child in children:
            attr = CYCLE_ATTR if (parent, child) in cycle_set else ""
            lines.append(f"  {quote(parent)} -> {quote(child)}{attr};")
    lines.append("}")
    return "\n".join(lines) + "\n"
