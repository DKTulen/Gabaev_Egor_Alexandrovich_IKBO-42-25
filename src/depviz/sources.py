"""Источники данных о зависимостях: реальный индекс Cargo и тестовый файл."""

from __future__ import annotations

from typing import Dict, List, Tuple

from .cargo_index import CargoIndex
from .config import TEST_MODE, Config
from .errors import RepositoryError
from .test_repo import load_test_repo

NODE_SEPARATOR = " "


def make_node(name: str, version: object) -> str:
    """Название узла графа: «имя версия»."""
    return f"{name}{NODE_SEPARATOR}{version}"


def split_node(node: str) -> Tuple[str, str]:
    """Делит название узла на имя и версию."""
    name, _, version = node.partition(NODE_SEPARATOR)
    return name, version


class CargoSource:
    """Источник данных: индекс реестра Cargo по HTTP."""

    def __init__(self, base_url: str, name: str, version: str) -> None:
        """Проверяет, что корневая версия существует в индексе."""
        self.index = CargoIndex(base_url)
        self.index.exact(name, version)
        self.root = make_node(name, version)

    def neighbors(self, node: str) -> List[str]:
        """Прямые зависимости узла с выбранными версиями."""
        name, version = split_node(node)
        entry = self.index.exact(name, version)
        children: List[str] = []
        for dep in entry.dependencies:
            found = self.index.resolve(dep.name, dep.requirement)
            children.append(make_node(dep.name, found.version))
        return children


class TestSource:
    """Источник данных: тестовый файл с графом."""

    __test__ = False

    def __init__(self, path: str, root: str) -> None:
        """Загружает файл и проверяет, что корневой пакет в нём есть."""
        self.repo: Dict[str, List[str]] = load_test_repo(path)
        known = set(self.repo)
        known.update(dep for deps in self.repo.values() for dep in deps)
        if root not in known:
            raise RepositoryError(f"пакет {root} не найден в {path}")
        self.root = root

    def neighbors(self, node: str) -> List[str]:
        """Прямые зависимости узла (для неописанных пакетов — пусто)."""
        return list(self.repo.get(node, []))


def make_source(config: Config):
    """Создаёт источник данных в соответствии с настройками."""
    if config.repo_mode == TEST_MODE:
        return TestSource(config.repository, config.package_name)
    return CargoSource(
        config.repository, config.package_name, config.package_version
    )
