"""Режим visualize (этап 5): описание Graphviz и картинка графа."""

from __future__ import annotations

from pathlib import Path

from .config import Config
from .dot import graph_to_dot
from .graph import build_graph, find_cycle_edges
from .render import open_image, render_image, save_text
from .sources import make_source
from .svg import graph_to_svg


def run(config: Config) -> int:
    """Строит граф, сохраняет .dot, рисует и показывает картинку."""
    source = make_source(config)
    graph = build_graph([source.root], source.neighbors, config.max_depth)
    cyclic = find_cycle_edges(graph.edges)
    dot_path = Path(config.dot_file)
    dot_text = graph_to_dot(graph, cyclic)
    save_text(dot_path, dot_text)
    print(dot_text, end="")
    image, used = render_image(
        dot_path, Path(config.image_file), graph_to_svg(graph, cyclic)
    )
    note = "Graphviz" if used else "встроенный SVG (Graphviz не найден)"
    print(f"Картинка сохранена: {image} [{note}]")
    if config.show_image and not open_image(image):
        print("Откройте картинку вручную: автоматически не открылась.")
    return 0
