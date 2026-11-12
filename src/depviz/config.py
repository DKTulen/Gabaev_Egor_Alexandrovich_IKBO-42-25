"""Загрузка и проверка настроек приложения из YAML-файла."""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Dict, List, Tuple

from .errors import ConfigError
from .yaml_config import parse_simple_yaml

MODES = (
    "params",
)
REMOTE_MODE = "remote"
TEST_MODE = "test"
REPO_MODES = (REMOTE_MODE, TEST_MODE)
MIN_DEPTH = 1
URL_PREFIXES = ("http://", "https://")
CRATE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TEST_NAME_RE = re.compile(r"^[A-Z]+$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?$")
TRUE_WORDS = ("true", "yes", "on")
FALSE_WORDS = ("false", "no", "off")
REQUIRED_KEYS = ("package_name", "repository", "repo_mode", "max_depth")
DEFAULT_MODE = "params"
DEFAULT_DOT = "out/graph.dot"
DEFAULT_IMAGE = "out/graph.png"


@dataclass(frozen=True)
class Config:
    """Все настройки программы (порядок полей = порядок вывода)."""

    package_name: str
    repository: str
    repo_mode: str
    package_version: str
    max_depth: int
    mode: str
    reverse_target: str
    dot_file: str
    image_file: str
    show_image: bool


def read_config_text(path: str) -> str:
    """Читает конфигурационный файл и возвращает его текст."""
    file = Path(path)
    if not file.is_file():
        raise ConfigError(f"файл конфигурации не найден: {path}")
    try:
        return file.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        raise ConfigError(f"не удалось прочитать {path}: {error}") from error


def require_text(raw: Dict[str, str], key: str) -> str:
    """Возвращает обязательный непустой параметр."""
    value = raw.get(key, "")
    if not value:
        raise ConfigError(f"параметр «{key}» обязателен и не может быть пустым")
    return value


def parse_choice(
    raw: Dict[str, str], key: str, allowed: tuple, default: str
) -> str:
    """Возвращает значение параметра, проверяя, что оно допустимо."""
    value = raw.get(key, default)
    if not value:
        raise ConfigError(f"параметр «{key}» обязателен")
    if value not in allowed:
        variants = ", ".join(allowed)
        raise ConfigError(
            f"параметр «{key}»: «{value}» не подходит, нужно: {variants}"
        )
    return value


def parse_depth(raw: Dict[str, str]) -> int:
    """Читает max_depth: целое число не меньше MIN_DEPTH."""
    text = raw.get("max_depth", "")
    try:
        value = int(text)
    except ValueError:
        raise ConfigError(
            f"max_depth должен быть целым числом, получено «{text}»"
        ) from None
    if value < MIN_DEPTH:
        raise ConfigError(f"max_depth должен быть не меньше {MIN_DEPTH}")
    return value


def parse_bool(raw: Dict[str, str], key: str, default: bool) -> bool:
    """Читает логический параметр (true/false, yes/no, on/off)."""
    text = raw.get(key)
    if text is None:
        return default
    if text.lower() in TRUE_WORDS:
        return True
    if text.lower() in FALSE_WORDS:
        return False
    raise ConfigError(f"параметр «{key}» должен быть true или false")


def check_unknown_keys(raw: Dict[str, str]) -> None:
    """Запрещает неизвестные параметры (так ловятся опечатки)."""
    known = {item.name for item in fields(Config)}
    for key in raw:
        if key not in known:
            raise ConfigError(f"неизвестный параметр «{key}»")


def check_remote(config: Config) -> None:
    """Проверяет параметры для работы с реальным репозиторием."""
    if not CRATE_RE.match(config.package_name):
        raise ConfigError(f"недопустимое имя пакета «{config.package_name}»")
    if not VERSION_RE.match(config.package_version):
        raise ConfigError("package_version должна иметь вид 1.2.3")
    if not config.repository.startswith(URL_PREFIXES):
        raise ConfigError("в режиме remote repository — это URL (http/https)")


def check_test(config: Config) -> None:
    """Проверяет параметры для работы с тестовым файлом."""
    if not TEST_NAME_RE.match(config.package_name):
        raise ConfigError("в режиме test имя пакета — большие латинские буквы")
    if not Path(config.repository).is_file():
        raise ConfigError(f"файл не найден: {config.repository}")


def check_reverse_target(config: Config) -> None:
    """Проверяет reverse_target, если выбран режим reverse."""
    target = config.reverse_target
    pattern = TEST_NAME_RE if config.repo_mode == TEST_MODE else CRATE_RE
    if not target or not pattern.match(target):
        raise ConfigError("для режима reverse задайте reverse_target")


def build_config(raw: Dict[str, str]) -> Config:
    """Создаёт Config из словаря значений и проверяет его целиком."""
    check_unknown_keys(raw)
    config = Config(
        package_name=require_text(raw, "package_name"),
        repository=require_text(raw, "repository"),
        repo_mode=parse_choice(raw, "repo_mode", REPO_MODES, ""),
        package_version=raw.get("package_version", ""),
        max_depth=parse_depth(raw),
        mode=parse_choice(raw, "mode", MODES, DEFAULT_MODE),
        reverse_target=raw.get("reverse_target", ""),
        dot_file=raw.get("dot_file", DEFAULT_DOT),
        image_file=raw.get("image_file", DEFAULT_IMAGE),
        show_image=parse_bool(raw, "show_image", True),
    )
    if config.repo_mode == TEST_MODE:
        check_test(config)
    else:
        check_remote(config)
    if config.mode == "reverse":
        check_reverse_target(config)
    return config


def load_config(path: str) -> Config:
    """Читает YAML-файл и возвращает проверенные настройки."""
    raw = parse_simple_yaml(read_config_text(path))
    return build_config(raw)


def format_value(value: object) -> str:
    """Превращает значение настройки в строку для вывода."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value) if value != "" else '""'


def config_items(config: Config) -> List[Tuple[str, str]]:
    """Возвращает пары (ключ, значение) всех настроек по порядку."""
    return [
        (item.name, format_value(getattr(config, item.name)))
        for item in fields(config)
    ]
