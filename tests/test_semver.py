"""Тесты версий и требований Cargo (этап 2)."""

import unittest

from depviz.semver import best_match, parse_version, version_matches

CASES = [
    ("^1.2.3", "1.9.0", True),
    ("^1.2.3", "2.0.0", False),
    ("^0.2.3", "0.2.9", True),
    ("^0.2.3", "0.3.0", False),
    ("^0.0.3", "0.0.4", False),
    ("1.2", "1.9.9", True),
    ("~1.2.3", "1.2.9", True),
    ("~1.2.3", "1.3.0", False),
    ("=1.2.3", "1.2.3", True),
    ("=1.2.3", "1.2.4", False),
    (">=1.0, <1.5", "1.4.0", True),
    (">=1.0, <1.5", "1.5.0", False),
    ("1.*", "1.7.0", True),
    ("1.2.*", "1.3.0", False),
    ("*", "9.9.9", True),
    (">1.2", "1.3.0", True),
    ("<=1.2", "1.2.9", True),
    ("^1.0", "1.1.0-beta", False),
]


class SemverTests(unittest.TestCase):
    """Проверки semver."""

    def test_table(self) -> None:
        """Все случаи из таблицы CASES."""
        for requirement, text, expected in CASES:
            with self.subTest(requirement=requirement, version=text):
                version = parse_version(text)
                actual = version_matches(version, requirement)
                self.assertEqual(actual, expected)

    def test_order_and_best(self) -> None:
        """Сравнение пре-релизов и выбор самой новой версии."""
        pre, release = parse_version("1.0.0-rc.1"), parse_version("1.0.0")
        self.assertLess(pre.sort_key(), release.sort_key())
        versions = [parse_version(v) for v in ("1.0.0", "1.2.0", "2.0.0")]
        self.assertEqual(str(best_match(versions, "^1.0")), "1.2.0")
        self.assertIsNone(best_match(versions, "^3.0"))

    def test_bad_input(self) -> None:
        """Некорректные записи вызывают ValueError."""
        with self.assertRaises(ValueError):
            parse_version("1.2")
        with self.assertRaises(ValueError):
            version_matches(parse_version("1.0.0"), "abc")


if __name__ == "__main__":
    unittest.main()
