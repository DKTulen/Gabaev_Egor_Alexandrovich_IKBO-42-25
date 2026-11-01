"""Чтение стартового скрипта и удаление комментариев."""

COMMENT_CHAR = "#"


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def read_script(path):
    """Вернуть список строк скрипта. Ошибка чтения -> ScriptError."""
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as err:
        raise ScriptError(f"не удалось прочитать скрипт {path}: {err}") \
            from err


def clean_line(line):
    """Убрать комментарий (всё после #) и пробелы по краям."""
    return line.split(COMMENT_CHAR, 1)[0].strip()
