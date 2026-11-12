"""Запасной рисовальщик графа в SVG (если Graphviz не установлен)."""

from __future__ import annotations

from html import escape
from typing import Dict, Iterable, List, Tuple

from .graph import Graph, levels

BOX_W = 190
BOX_H = 34
GAP_X = 90
GAP_Y = 24
MARGIN = 30
BEND = 60
Point = Tuple[int, int]
HEADER = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">\n'
    '<defs>{markers}</defs>\n'
    '<rect width="100%" height="100%" fill="white"/>\n'
)
MARKER = (
    '<marker id="{id}" viewBox="0 0 10 10" refX="9" refY="5" '
    'markerWidth="7" markerHeight="7" orient="auto">'
    '<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
)


def layout(graph: Graph) -> Dict[str, Point]:
    """Левый верхний угол каждого узла: колонка = глубина."""
    positions: Dict[str, Point] = {}
    for column, nodes in enumerate(levels(graph)):
        for row, node in enumerate(nodes):
            x = MARGIN + column * (BOX_W + GAP_X)
            y = MARGIN + row * (BOX_H + GAP_Y)
            positions[node] = (x, y)
    return positions


def svg_node(label: str, point: Point, is_root: bool) -> str:
    """SVG-код прямоугольника с подписью."""
    fill = "#cfe8ff" if is_root else "#f4f4f4"
    x, y = point
    rect = (
        f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="5" '
        f'fill="{fill}" stroke="#333"/>'
    )
    text = (
        f'<text x="{x + BOX_W // 2}" y="{y + BOX_H // 2 + 4}" '
        f'text-anchor="middle" font-size="12" font-family="monospace">'
        f"{escape(label)}</text>"
    )
    return rect + text + "\n"


def svg_edge(start: Point, end: Point, is_cycle: bool) -> str:
    """SVG-код изогнутой стрелки от узла start к узлу end."""
    x1, y1 = start[0] + BOX_W, start[1] + BOX_H // 2
    x2, y2 = end[0], end[1] + BOX_H // 2
    color = "red" if is_cycle else "#555"
    curve = f"M{x1},{y1} C{x1 + BEND},{y1} {x2 - BEND},{y2} {x2},{y2}"
    marker = "arrow-red" if is_cycle else "arrow"
    return (
        f'<path d="{curve}" fill="none" stroke="{color}" '
        f'marker-end="url(#{marker})"/>\n'
    )


def canvas_size(positions: Dict[str, Point]) -> Point:
    """Ширина и высота картинки по самым дальним узлам."""
    width = max(x for x, _ in positions.values()) + BOX_W + MARGIN
    height = max(y for _, y in positions.values()) + BOX_H + MARGIN
    return width, height


def graph_to_svg(graph: Graph, cyclic: Iterable[Tuple[str, str]]) -> str:
    """Возвращает SVG-картинку графа."""
    cycle_set = set(cyclic)
    positions = layout(graph)
    width, height = canvas_size(positions)
    markers = MARKER.format(id="arrow", color="#555")
    markers += MARKER.format(id="arrow-red", color="red")
    parts: List[str] = [HEADER.format(w=width, h=height, markers=markers)]
    for parent, children in graph.edges.items():
        for child in children:
            flag = (parent, child) in cycle_set
            parts.append(svg_edge(positions[parent], positions[child], flag))
    for node, point in positions.items():
        parts.append(svg_node(node, point, node in graph.roots))
    parts.append("</svg>\n")
    return "".join(parts)
