"""Точка входа: аргументы командной строки и запуск выбранного режима."""

from __future__ import annotations

import argparse
import importlib
import sys
from typing import List, Optional

from .config import load_config
from .errors import DepvizError

DEFAULT_CONFIG = "config.yaml"
INTERRUPTED_CODE = 130
COMMANDS = {
    "params": "cmd_params",
}


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        prog="depviz", description="Визуализация графа зависимостей Cargo"
    )
    parser.add_argument(
        "config", nargs="?", default=DEFAULT_CONFIG,
        help="путь к YAML-файлу настроек (по умолчанию config.yaml)",
    )
    return parser.parse_args(argv)


def configure_output() -> None:
    """Включает вывод в UTF-8, чтобы русский текст не ломался в Windows."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def load_command(mode: str):
    """Подключает модуль выбранного режима."""
    return importlib.import_module("." + COMMANDS[mode], __package__)


def main(argv: Optional[List[str]] = None) -> int:
    """Запускает программу и возвращает код завершения."""
    configure_output()
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        return load_command(config.mode).run(config)
    except DepvizError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return error.exit_code
    except KeyboardInterrupt:
        print("Прервано пользователем", file=sys.stderr)
        return INTERRUPTED_CODE
