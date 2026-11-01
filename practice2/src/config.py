"""Параметры командной строки эмулятора."""
import argparse
from dataclasses import dataclass

NOT_SET = "(не задан)"


@dataclass
class Config:
    """Настройки запуска."""

    vfs_path: str = None
    script_path: str = None


def parse_args(argv=None):
    """Разобрать аргументы командной строки в Config."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор оболочки ОС с виртуальной ФС",
    )
    parser.add_argument("--vfs", help="путь к CSV-файлу с VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    args = parser.parse_args(argv)
    return Config(args.vfs, args.script)


def format_debug(config):
    """Текст отладочного вывода всех заданных параметров."""
    lines = [
        "Параметры запуска:",
        f"  vfs    = {config.vfs_path or NOT_SET}",
        f"  script = {config.script_path or NOT_SET}",
    ]
    return "\n".join(lines)
