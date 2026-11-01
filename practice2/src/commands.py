def _describe(name, args):
    return f"команда: {name}, аргументы: {args}"

def cmd_ls(shell, args):
    return _describe("ls", args)

def cmd_cd(shell, args):
    return _describe("cd", args)

def cmd_exit(shell, args):
    """Завершить работу эмулятора."""
    shell.running = False
    return ""

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
