"""Чтение тестового репозитория: файл с графом из больших латинских букв."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from .errors import RepositoryError

NAME_RE = re.compile(r"^[A-Z]+$")
COMMENT_MARK = "#"


def check_name(name: str, number: int) -> None:
    """Проверяет имя пакета и сообщает номер строки при ошибке."""
    if not NAME_RE.match(name):
        raise RepositoryError(f"строка {number}: плохое имя пакета «{name}»")


def parse_line(line: str, number: int) -> tuple:
    """Разбирает строку «пакет: зависимость зависимость ...»."""
    name, separator, rest = line.partition(":")
    if not separator:
        raise RepositoryError(f"строка {number}: ожидается «A: B C»")
    name = name.strip()
    check_name(name, number)
    deps: List[str] = []
    for dep in rest.replace(",", " ").split():
        check_name(dep, number)
        if dep not in deps:
            deps.append(dep)
    return name, deps


def parse_test_repo(text: str) -> Dict[str, List[str]]:
    """Превращает текст файла в словарь «пакет -> зависимости»."""
    repo: Dict[str, List[str]] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split(COMMENT_MARK, 1)[0].strip()
        if not line:
            continue
        name, deps = parse_line(line, number)
        if name in repo:
            raise RepositoryError(f"строка {number}: пакет {name} уже описан")
        repo[name] = deps
    return repo


def load_test_repo(path: str) -> Dict[str, List[str]]:
    """Читает файл тестового репозитория."""
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        raise RepositoryError(f"не прочитать {path}: {error}") from error
    return parse_test_repo(text)
