import sys

from gui import App
from shell import Shell
from vfs import VFS


def main():
    """Запустить эмулятор."""
    app = App(Shell(VFS()))
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
