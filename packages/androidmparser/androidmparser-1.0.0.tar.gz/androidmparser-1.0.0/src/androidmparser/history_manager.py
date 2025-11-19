# history_manager.py
import json
import os
from typing import List

def get_history_file(package_name: str) -> str:
    return f"intents_{package_name}.json"

def load_history(package_name: str) -> List[str]:
    filepath = get_history_file(package_name)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(package_name: str, commands: List[str]):
    filepath = get_history_file(package_name)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(commands, f, indent=2, ensure_ascii=False)