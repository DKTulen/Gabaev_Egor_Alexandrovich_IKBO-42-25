from commands import COMMANDS
from line_parser import parse_line

class Shell:
    def __init__(self, vfs):
        self.vfs = vfs
        self.running = True

    def execute(self, line):
        name, args = parse_line(line)
        if not name:
            return ""
        handler = COMMANDS.get(name)
        if handler is None:
            return f"{name}: команда не найдена"
        return handler(self, args)
