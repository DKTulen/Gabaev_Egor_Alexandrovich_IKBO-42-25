"""Режим direct (этап 2): вывод прямых зависимостей пакета."""

from __future__ import annotations

from .config import Config
from .sources import make_source


def run(config: Config) -> int:
    """Печатает прямые зависимости корневого пакета."""
    source = make_source(config)
    children = source.neighbors(source.root)
    print(f"Прямые зависимости пакета {source.root}:")
    if not children:
        print("  (нет зависимостей)")
    for child in children:
        print(f"  - {child}")
    return 0
