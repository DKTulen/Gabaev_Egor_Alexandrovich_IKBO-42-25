"""Минимальный разбор YAML-файла вида «ключ: значение»."""

from __future__ import annotations

from typing import Dict, Tuple

from .errors import ConfigError

COMMENT_MARK = "#"
QUOTES = ("'", '"')
DOC_START = "---"
MIN_QUOTED_LEN = 2


def is_comment_start(value: str, index: int, quote: str) -> bool:
    """Проверяет, что в позиции index начинается комментарий."""
    if quote or value[index] != COMMENT_MARK:
        return False
    return not index or value[index - 1].isspace()


def update_quote(char: str, quote: str) -> str:
    """Возвращает открытую кавычку после просмотра символа char."""
    if not quote and char in QUOTES:
        return char
    if char == quote:
        return ""
    return quote


def strip_comment(value: str) -> str:
    """Убирает комментарий из строки, не трогая текст в кавычках."""
    quote = ""
    for index, char in enumerate(value):
        if is_comment_start(value, index, quote):
            return value[:index]
        quote = update_quote(char, quote)
    return value


def unquote(value: str) -> str:
    """Снимает одинарные или двойные кавычки вокруг значения."""
    value = value.strip()
    if len(value) >= MIN_QUOTED_LEN and value[0] in QUOTES:
        if value[-1] == value[0]:
            return value[1:-1]
    return value


def parse_line(line: str, number: int) -> Tuple[str, str]:
    """Разбирает одну строку формата «ключ: значение»."""
    if line[0].isspace():
        raise ConfigError(f"строка {number}: вложенность не поддерживается")
    key, separator, rest = line.partition(":")
    key = key.strip()
    if not separator or not key:
        raise ConfigError(f"строка {number}: ожидается «ключ: значение»")
    return key, unquote(rest)


def parse_simple_yaml(text: str) -> Dict[str, str]:
    """Превращает текст YAML в словарь «ключ -> строка»."""
    result: Dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = strip_comment(raw).rstrip()
        if not line.strip() or line.strip() == DOC_START:
            continue
        key, value = parse_line(line, number)
        if key in result:
            raise ConfigError(f"строка {number}: ключ «{key}» повторяется")
        result[key] = value
    return result
