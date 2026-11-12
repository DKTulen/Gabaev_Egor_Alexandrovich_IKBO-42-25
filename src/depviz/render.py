"""Сохранение файлов и показ изображения графа."""

from __future__ import annotations

import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Tuple

from .errors import RenderError

DOT_FORMATS = ("png", "svg", "pdf")


def save_text(path: Path, text: str) -> None:
    """Сохраняет текст в файл, создавая нужные папки."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as error:
        raise RenderError(f"не удалось записать {path}: {error}") from error


def run_dot(dot: str, source: Path, image: Path, fmt: str) -> None:
    """Запускает Graphviz, чтобы превратить .dot в картинку."""
    command = [dot, f"-T{fmt}", str(source), "-o", str(image)]
    try:
        image.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(command, check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise RenderError(f"Graphviz не справился: {error}") from error


def render_image(
    dot_path: Path, image_path: Path, svg_text: str
) -> Tuple[Path, bool]:

    """Рисует картинку; без Graphviz сохраняет встроенный SVG."""
    dot = shutil.which("dot")
    fmt = image_path.suffix.lstrip(".").lower()
    if dot and fmt in DOT_FORMATS:
        run_dot(dot, dot_path, image_path, fmt)
        return image_path, True
    fallback = image_path.with_suffix(".svg")
    save_text(fallback, svg_text)
    return fallback, False


def open_image(path: Path) -> bool:
    """Открывает файл в программе по умолчанию (браузер или просмотрщик)."""
    try:
        return bool(webbrowser.open(path.resolve().as_uri()))
    except webbrowser.Error:
        return False
