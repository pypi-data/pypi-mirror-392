# history_manager.py
import json
import os
from typing import List
from .paths import get_data_dir

def get_history_file(package_name: str) -> str:
    return os.path.join(get_data_dir(), f"intents_{package_name}.json")

def load_history(package_name: str) -> List[str]:
    filepath = get_history_file(package_name)
    if not os.path.isfile(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, ValueError):
        return []

def save_history(package_name: str, commands: List[str]):
    filepath = get_history_file(package_name)
    # Убедимся, что папка существует (на случай, если platformdirs не создал)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(commands, f, indent=2, ensure_ascii=False)