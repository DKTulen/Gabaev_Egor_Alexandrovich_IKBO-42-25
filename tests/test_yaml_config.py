"""Тесты разбора простого YAML."""

import unittest

from depviz.errors import ConfigError
from depviz.yaml_config import parse_simple_yaml


class YamlTests(unittest.TestCase):
    """Проверки parse_simple_yaml."""

    def test_basic(self) -> None:
        """Читает ключи, комментарии и кавычки."""
        text = 'a: 1\n# note\nb: "x y"  # tail\nc:\n'
        result = parse_simple_yaml(text)
        self.assertEqual(result, {"a": "1", "b": "x y", "c": ""})

    def test_hash_inside_url(self) -> None:
        """Решётка без пробела перед ней — не комментарий."""
        result = parse_simple_yaml("u: http://x/#frag")
        self.assertEqual(result["u"], "http://x/#frag")

    def test_errors(self) -> None:
        """Дубликаты, вложенность и строки без двоеточия — ошибки."""
        for bad in ("a: 1\na: 2", "  a: 1", "just text"):
            with self.assertRaises(ConfigError):
                parse_simple_yaml(bad)


if __name__ == "__main__":
    unittest.main()
