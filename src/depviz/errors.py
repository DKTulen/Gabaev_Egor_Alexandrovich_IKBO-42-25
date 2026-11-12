"""Классы ошибок приложения."""


class DepvizError(Exception):
    """Базовая ошибка приложения."""

    exit_code = 1


class ConfigError(DepvizError):
    """Ошибка в конфигурационном файле."""

    exit_code = 2


class RepositoryError(DepvizError):
    """Ошибка при работе с репозиторием пакетов."""

    exit_code = 3


class RenderError(DepvizError):
    """Ошибка при построении или показе изображения."""

    exit_code = 4
