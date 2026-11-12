"""Версии SemVer и требования к версиям в формате Cargo."""

from __future__ import annotations

import operator
import re
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

WILDCARD = "*"
PRE_MARK = "-"
VERSION_RE = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)
COMPARATOR_RE = re.compile(
    r"^(\^|~|=|>=|<=|>|<)?\s*(\*|\d+)(?:\.(\*|\d+))?(?:\.(\*|\d+))?"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)
COMPARATORS = {
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
    "==": operator.eq,
}


def identifier_key(text: str) -> Tuple[int, int, str]:
    """Ключ одного идентификатора пре-релиза: числа меньше строк."""
    if text.isdigit():
        return (0, int(text), "")
    return (1, 0, text)


def prerelease_key(pre: str) -> tuple:
    """Ключ пре-релиза: обычный релиз старше любого пре-релиза."""
    if not pre:
        return (1,)
    return (0, tuple(identifier_key(part) for part in pre.split(".")))


@dataclass(frozen=True)
class Version:
    """Версия вида MAJOR.MINOR.PATCH с необязательным пре-релизом."""

    major: int
    minor: int
    patch: int
    pre: str = ""

    def sort_key(self) -> tuple:
        """Ключ для сравнения версий по правилам SemVer."""
        return (self.major, self.minor, self.patch, prerelease_key(self.pre))

    def __str__(self) -> str:
        """Текст версии, например 1.2.3 или 1.2.3-beta.1."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.pre}" if self.pre else base


@dataclass(frozen=True)
class Constraint:
    """Условие вида «версия >= 1.2.0»."""

    operator: str
    version: Version


@dataclass(frozen=True)
class Partial:
    """Версия, где часть номеров может отсутствовать."""

    major: Optional[int]
    minor: Optional[int]
    patch: Optional[int]
    pre: str
    wild: bool


def parse_version(text: str) -> Version:
    """Разбирает строку вида 1.2.3 в объект Version."""
    match = VERSION_RE.match(text.strip())
    if not match:
        raise ValueError(f"некорректная версия «{text}»")
    major, minor, patch, pre = match.groups()
    return Version(int(major), int(minor), int(patch), pre or "")


def to_number(text: Optional[str]) -> Optional[int]:
    """Число из части версии; None для «*» и отсутствующей части."""
    if text is None or text == WILDCARD:
        return None
    return int(text)


def parse_comparator(text: str) -> Tuple[str, Partial]:
    """Разбирает одно условие, например «^1.2» или «>=0.3.1»."""
    match = COMPARATOR_RE.match(text.strip())
    if not match:
        raise ValueError(f"некорректное требование к версии «{text}»")
    sign, major, minor, patch, pre = match.groups()
    wild = WILDCARD in (major, minor, patch)
    numbers = (to_number(major), to_number(minor), to_number(patch))
    return sign or "", Partial(*numbers, pre or "", wild)


def tilde_upper(part: Partial) -> Version:
    """Первая версия, которая уже не подходит под тильду."""
    if part.minor is None:
        return Version(part.major + 1, 0, 0)
    return Version(part.major, part.minor + 1, 0)


def caret_upper(part: Partial) -> Version:
    """Первая версия, которая уже не подходит под «^»."""
    if part.major:
        return Version(part.major + 1, 0, 0)
    if part.minor is None:
        return Version(1, 0, 0)
    if part.minor:
        return Version(0, part.minor + 1, 0)
    if part.patch is None:
        return Version(0, 1, 0)
    return Version(0, 0, part.patch + 1)


def caret_rule(part: Partial, low: Version) -> List[Constraint]:
    """Правило «^»: от low до границы совместимости."""
    return [Constraint(">=", low), Constraint("<", caret_upper(part))]


def tilde_rule(part: Partial, low: Version) -> List[Constraint]:
    """Правило «~»: от low до следующего второго/главного номера."""
    return [Constraint(">=", low), Constraint("<", tilde_upper(part))]


def equal_rule(part: Partial, low: Version) -> List[Constraint]:
    """Правило «=»: точная версия или диапазон для неполной записи."""
    if part.patch is not None:
        return [Constraint("==", low)]
    return tilde_rule(part, low)


def greater_rule(part: Partial, low: Version) -> List[Constraint]:
    """Правило «>»: строго больше."""
    if part.patch is not None:
        return [Constraint(">", low)]
    return [Constraint(">=", tilde_upper(part))]


def less_eq_rule(part: Partial, low: Version) -> List[Constraint]:
    """Правило «<=»: не больше."""
    if part.patch is not None:
        return [Constraint("<=", low)]
    return [Constraint("<", tilde_upper(part))]


RULES = {
    "": caret_rule,
    "^": caret_rule,
    "~": tilde_rule,
    "=": equal_rule,
    ">": greater_rule,
    ">=": lambda part, low: [Constraint(">=", low)],
    "<": lambda part, low: [Constraint("<", low)],
    "<=": less_eq_rule,
}


def partial_constraints(sign: str, part: Partial) -> List[Constraint]:
    """Переводит одно условие в список простых сравнений."""
    if part.major is None:
        return []
    if not sign and part.wild:
        sign = "="
    low = Version(part.major, part.minor or 0, part.patch or 0, part.pre)
    return RULES[sign](part, low)


def parse_requirement(text: str) -> List[Constraint]:
    """Разбирает требование вида «>=1.2, <2» в список условий."""
    constraints: List[Constraint] = []
    for piece in (text.strip() or WILDCARD).split(","):
        sign, part = parse_comparator(piece)
        constraints.extend(partial_constraints(sign, part))
    return constraints


def satisfies(version: Version, constraint: Constraint) -> bool:
    """Проверяет версию по одному простому условию."""
    compare: Callable = COMPARATORS[constraint.operator]
    return compare(version.sort_key(), constraint.version.sort_key())


def is_suitable(
    version: Version, constraints: List[Constraint], allow_pre: bool
) -> bool:
    """Версия подходит, если выполнены все условия."""
    if version.pre and not allow_pre:
        return False
    return all(satisfies(version, item) for item in constraints)


def version_matches(version: Version, requirement: str) -> bool:
    """Проверяет версию по текстовому требованию Cargo."""
    constraints = parse_requirement(requirement)
    return is_suitable(version, constraints, PRE_MARK in requirement)


def best_match(
    versions: Iterable[Version], requirement: str
) -> Optional[Version]:
    """Самая новая версия из списка, подходящая под требование."""
    constraints = parse_requirement(requirement)
    allow_pre = PRE_MARK in requirement
    suitable = [v for v in versions if is_suitable(v, constraints, allow_pre)]
    return max(suitable, key=Version.sort_key) if suitable else None
