"""Точка входа: python3 src/main.py [--vfs FILE] [--script FILE]."""
import sys

from config import format_debug, parse_args
from gui import App
from script import ScriptError, read_script
from shell import Shell
from vfs import VFS


def load_script(path):
    """Прочитать строки скрипта (пустой список, если скрипта нет)."""
    if path is None:
        return []
    return read_script(path)


def main(argv=None):
    """Запустить эмулятор. Возвращает код завершения."""
    config = parse_args(argv)
    debug = format_debug(config)
    print(debug)
    try:
        lines = load_script(config.script_path)
    except ScriptError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1
    app = App(Shell(VFS()))
    app.write(debug)
    app.run_script(lines)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
