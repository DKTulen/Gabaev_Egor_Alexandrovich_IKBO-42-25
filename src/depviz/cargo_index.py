"""Чтение индекса реестра Cargo (формат sparse index, например crates.io)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import RepositoryError
from .semver import Version, best_match, parse_version

REQUEST_TIMEOUT = 20
USER_AGENT = "depviz-student-tool/1.0"
HTTP_NOT_FOUND = 404
DEV_KIND = "dev"
SHORT_PREFIX = {1: "1", 2: "2"}
THREE_LETTERS = 3


@dataclass(frozen=True)
class Dependency:
    """Зависимость: имя пакета и требование к его версии."""

    name: str
    requirement: str


@dataclass(frozen=True)
class CrateVersion:
    """Версия пакета с её зависимостями."""

    version: Version
    yanked: bool
    dependencies: List[Dependency]


def index_path(name: str) -> str:
    """Путь файла пакета в индексе: 1/a, 2/ab, 3/a/abc, ab/cd/abcd."""
    name = name.lower()
    size = len(name)
    if size in SHORT_PREFIX:
        return f"{SHORT_PREFIX[size]}/{name}"
    if size == THREE_LETTERS:
        return f"3/{name[0]}/{name}"
    return f"{name[:2]}/{name[2:4]}/{name}"


def fetch_text(url: str) -> str:
    """Скачивает страницу и возвращает её текст."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.read().decode("utf-8")
    except HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise RepositoryError(f"пакет не найден: {url}") from None
        raise RepositoryError(f"ошибка HTTP {error.code}: {url}") from error
    except (URLError, OSError, ValueError) as error:
        raise RepositoryError(f"не удалось получить {url}: {error}") from error


def parse_dependency(item: dict) -> Optional[Dependency]:
    """Превращает запись deps в Dependency или None, если она не нужна."""
    if item.get("kind") == DEV_KIND or item.get("optional"):
        return None
    real_name = item.get("package") or item["name"]
    return Dependency(real_name, item.get("req", "*"))


def parse_entry(line: str, crate: str) -> CrateVersion:
    """Разбирает одну JSON-строку индекса."""
    try:
        data = json.loads(line)
        version = parse_version(data["vers"])
        found = [parse_dependency(item) for item in data.get("deps", [])]
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise RepositoryError(f"битая запись {crate}: {error}") from error
    deps = [item for item in found if item]
    return CrateVersion(version, bool(data.get("yanked")), deps)


def parse_index(text: str, crate: str) -> List[CrateVersion]:
    """Разбирает весь файл индекса пакета."""
    lines = [line for line in text.splitlines() if line.strip()]
    return [parse_entry(line, crate) for line in lines]


class CargoIndex:
    """Клиент индекса: каждый пакет скачивается один раз."""

    def __init__(self, base_url: str) -> None:
        """Запоминает адрес индекса и создаёт пустой кэш."""
        self.base_url = base_url.rstrip("/")
        self.cache: Dict[str, List[CrateVersion]] = {}

    def versions(self, crate: str) -> List[CrateVersion]:
        """Возвращает все версии пакета (из кэша или из сети)."""
        key = crate.lower()
        if key not in self.cache:
            url = f"{self.base_url}/{index_path(key)}"
            self.cache[key] = parse_index(fetch_text(url), crate)
        return self.cache[key]

    def exact(self, crate: str, version_text: str) -> CrateVersion:
        """Находит запись о точной версии пакета."""
        try:
            wanted = parse_version(version_text)
        except ValueError as error:
            raise RepositoryError(f"{crate}: {error}") from error
        for entry in self.versions(crate):
            if entry.version == wanted:
                return entry
        raise RepositoryError(f"у пакета {crate} нет версии {version_text}")

    def resolve(self, crate: str, requirement: str) -> CrateVersion:
        """Выбирает самую новую неотозванную версию под требование."""
        alive = {e.version: e for e in self.versions(crate) if not e.yanked}
        try:
            best = best_match(alive, requirement)
        except ValueError as error:
            raise RepositoryError(f"пакет {crate}: {error}") from error
        if best is None:
            raise RepositoryError(f"для {crate} нет версии под «{requirement}»")
        return alive[best]
