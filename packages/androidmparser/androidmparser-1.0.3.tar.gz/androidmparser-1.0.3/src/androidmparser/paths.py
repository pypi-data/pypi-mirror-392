"""
Модуль для получения стандартных путей к конфигурации, данным и кэшу приложения.
Использует platformdirs для соблюдения XDG Base Directory Specification (Linux),
стандартов macOS и Windows.
"""

from platformdirs import user_config_dir, user_data_dir, user_cache_dir
import os

APP_NAME = "androidmparser"
APP_AUTHOR = "sevvet"  # или "Alice", если хочешь группировку по автору


def get_config_dir() -> str:
    """Возвращает путь к директории конфигурации. Создаёт её при первом вызове."""
    path = user_config_dir(APP_NAME, APP_AUTHOR, ensure_exists=True)
    return path


def get_data_dir() -> str:
    """Возвращает путь к директории данных (сохранённые файлы, экспорт и т.п.)."""
    path = user_data_dir(APP_NAME, APP_AUTHOR, ensure_exists=True)
    return path


def get_cache_dir() -> str:
    """Возвращает путь к директории кэша (временные файлы, ADB-кэш и т.п.)."""
    path = user_cache_dir(APP_NAME, APP_AUTHOR, ensure_exists=True)
    return path


def get_config_file(filename: str = "manifest_parser.ini") -> str:
    """Возвращает полный путь к указанному файлу конфигурации."""
    return os.path.join(get_config_dir(), filename)


def get_data_file(filename: str) -> str:
    """Возвращает полный путь к указанному файлу в директории данных."""
    return os.path.join(get_data_dir(), filename)


def get_cache_file(filename: str) -> str:
    """Возвращает полный путь к указанному файлу в директории кэша."""
    return os.path.join(get_cache_dir(), filename)