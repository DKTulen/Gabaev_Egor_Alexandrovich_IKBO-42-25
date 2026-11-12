"""Режим params (этап 1): вывод всех настроек в формате «ключ: значение»."""

from __future__ import annotations

from .config import Config, config_items


def run(config: Config) -> int:
    """Печатает все настройки, заданные пользователем."""
    for key, value in config_items(config):
        print(f"{key}: {value}")
    return 0
