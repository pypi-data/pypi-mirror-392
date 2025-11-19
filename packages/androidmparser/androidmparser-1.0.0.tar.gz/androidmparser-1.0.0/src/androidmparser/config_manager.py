# config_manager.py
import os
import configparser

CONFIG_FILE = "../../manifest_parser.ini"

def load_window_geometry(section: str, default: str = "") -> str:
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding="utf-8")
    return config.get(section, "geometry", fallback=default)

def save_window_geometry(section: str, geometry: str):
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding="utf-8")
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, "geometry", geometry)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)