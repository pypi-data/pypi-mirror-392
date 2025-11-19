# config_manager.py
import os
import configparser
from .paths import get_config_file

def load_window_geometry(section: str, default: str = "") -> str:
    config = configparser.ConfigParser()
    config_file = get_config_file()  # ← замена
    if os.path.exists(config_file):
        config.read(config_file, encoding="utf-8")
    return config.get(section, "geometry", fallback=default)

def save_window_geometry(section: str, geometry: str):
    config_file = get_config_file()  # ← замена
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file, encoding="utf-8")
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, "geometry", geometry)
    with open(config_file, "w", encoding="utf-8") as f:
        config.write(f)