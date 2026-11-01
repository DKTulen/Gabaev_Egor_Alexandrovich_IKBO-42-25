"""Точка входа: python3 src/main.py [--vfs FILE] [--script FILE]."""
import sys

from config import format_debug, parse_args
from gui import App
from script import ScriptError, read_script
from shell import Shell
from vfs import VFS, VFSError, load_csv


def load_vfs(path):
    """Загрузить VFS из CSV или создать VFS по умолчанию."""
    if path is None:
        return VFS()
    return load_csv(path)


def load_inputs(config):
    """Загрузить VFS и строки скрипта (пустой список без скрипта)."""
    vfs = load_vfs(config.vfs_path)
    lines = []
    if config.script_path:
        lines = read_script(config.script_path)
    return vfs, lines


def main(argv=None):
    """Запустить эмулятор. Возвращает код завершения."""
    config = parse_args(argv)
    debug = format_debug(config)
    print(debug)
    try:
        vfs, lines = load_inputs(config)
    except (VFSError, ScriptError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1
    app = App(Shell(vfs))
    app.write(debug)
    motd = vfs.read_motd()
    if motd:
        app.write(motd.rstrip("\n"))
    app.run_script(lines)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
