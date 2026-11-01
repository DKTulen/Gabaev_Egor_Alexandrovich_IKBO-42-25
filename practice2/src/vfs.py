"""Виртуальная файловая система (VFS) в памяти.

Источник - CSV-файл с колонками path,type,content.
type: dir или file; content - base64 (для папок пусто).
"""
import base64
import binascii
import csv
from dataclasses import dataclass, field
from pathlib import Path

CSV_HEADER = ["path", "type", "content"]
TYPE_DIR = "dir"
TYPE_FILE = "file"
MOTD_NAME = "motd"
DEFAULT_NAME = "default"
FIRST_DATA_ROW = 2


class VFSError(Exception):
    """Ошибка загрузки или разбора VFS."""


@dataclass
class Node:
    """Узел дерева: папка (children) или файл (data)."""

    name: str
    is_dir: bool
    data: bytes = b""
    children: dict = field(default_factory=dict)


def split_path(path):
    """Разбить путь '/a/b' на список имён ['a', 'b']."""
    return [part for part in path.split("/") if part]


class VFS:
    """Дерево файлов и папок, целиком в памяти."""

    def __init__(self, name=DEFAULT_NAME):
        self.name = name
        self.root = Node("", True)

    def add_dir(self, path):
        """Создать папку (и недостающие родительские)."""
        node = self.root
        for part in split_path(path):
            child = node.children.get(part)
            if child is None:
                child = Node(part, True)
                node.children[part] = child
            elif not child.is_dir:
                raise VFSError(f"'{part}' в пути {path} - это файл")
            node = child
        return node

    def add_file(self, path, data):
        """Создать файл с содержимым data (bytes)."""
        parts = split_path(path)
        if not parts:
            raise VFSError("у файла не задано имя")
        parent = self.add_dir("/".join(parts[:-1]))
        name = parts[-1]
        existing = parent.children.get(name)
        if existing is not None and existing.is_dir:
            raise VFSError(f"{path}: такая папка уже есть")
        parent.children[name] = Node(name, False, data)

    def get(self, path):
        """Найти узел по пути; None, если его нет."""
        node = self.root
        for part in split_path(path):
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def read_motd(self):
        """Текст motd из корня VFS или None, если его нет."""
        node = self.root.children.get(MOTD_NAME)
        if node is None or node.is_dir:
            return None
        return node.data.decode("utf-8", errors="replace")


def _decode(content):
    """Раскодировать base64-содержимое файла."""
    try:
        return base64.b64decode(content, validate=True)
    except binascii.Error as err:
        raise VFSError("содержимое не является base64") from err


def _apply_row(vfs, row):
    """Добавить в VFS одну строку CSV."""
    if len(row) != len(CSV_HEADER):
        raise VFSError(f"ожидается колонок: {len(CSV_HEADER)}")
    path, kind, content = row
    if not path.startswith("/"):
        raise VFSError(f"путь должен начинаться с '/': {path}")
    if kind == TYPE_DIR:
        vfs.add_dir(path)
    elif kind == TYPE_FILE:
        vfs.add_file(path, _decode(content))
    else:
        raise VFSError(f"неизвестный тип '{kind}'")


def _read_rows(file):
    """Прочитать все строки CSV; ошибки чтения -> VFSError."""
    try:
        with open(file, encoding="utf-8-sig", newline="") as handle:
            return list(csv.reader(handle))
    except (OSError, UnicodeDecodeError, csv.Error) as err:
        raise VFSError(f"не удалось прочитать {file}: {err}") from err


def load_csv(path):
    """Загрузить VFS из CSV-файла. Любая ошибка -> VFSError."""
    file = Path(path)
    if not file.is_file():
        raise VFSError(f"файл VFS не найден: {path}")
    rows = _read_rows(file)
    if not rows or rows[0] != CSV_HEADER:
        raise VFSError("неверный формат: нужен заголовок "
                       + ",".join(CSV_HEADER))
    vfs = VFS(file.name)
    for number, row in enumerate(rows[1:], start=FIRST_DATA_ROW):
        if not row:
            continue
        try:
            _apply_row(vfs, row)
        except VFSError as err:
            raise VFSError(f"строка {number}: {err}") from err
    return vfs
