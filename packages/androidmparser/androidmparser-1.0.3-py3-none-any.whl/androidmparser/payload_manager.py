# payload_manager.py
import json
import os
from .paths import get_data_dir
from typing import Dict, List

DEFAULT_PAYLOAD_FILE = os.path.join(get_data_dir(), "payloads_default.json")

BUILTIN_DEFAULTS = {
    "endpoints": [
        "/promo/",
        "/api/v1/test"
    ],
    "query_params": [
        {"name": "debug", "value": "true"},
        {"name": "test", "value": "1"},
        {"name": "redirect", "value": "https://evil.com"},
        {"name": "url", "value": "https://evil.com"},
        {"name": "utm_source", "value": "intruder"}
    ]
}

def load_payloads(package_name: str) -> Dict[str, List]:
    # 1. Пользовательский файл
    user_file = os.path.join(get_data_dir(), f"payloads_{package_name}.json")
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return _validate_payloads(data)
        except Exception as e:
            print(f"[Payload] Warning: failed to load {user_file}: {e}")

    # 2. Общий дефолтный файл
    if os.path.exists(DEFAULT_PAYLOAD_FILE):
        try:
            with open(DEFAULT_PAYLOAD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return _validate_payloads(data)
        except Exception as e:
            print(f"[Payload] Warning: failed to load {DEFAULT_PAYLOAD_FILE}: {e}")

    # 3. Встроенные значения
    print("[Payload] Using built-in defaults")
    return BUILTIN_DEFAULTS.copy()

def _validate_payloads(data: dict) -> dict:
    endpoints = data.get("endpoints", [])
    params = data.get("query_params", [])
    # Приводим к нужному формату
    endpoints = [str(ep).strip() or "/" for ep in endpoints]
    params = [
        {"name": str(p.get("name", "")).strip(), "value": str(p.get("value", "")).strip()}
        for p in params
        if p.get("name")
    ]
    exclude = data.get("exclude_patterns", [])
    validated_exclude = []
    for p in exclude:
        if not isinstance(p, dict):
            continue
        validated_exclude.append({
            "pattern": str(p.get("pattern", "")).strip(),
            "enabled": bool(p.get("enabled", True)),
            "invert": bool(p.get("invert", False)),
            "case_sensitive": bool(p.get("case_sensitive", False)),
            "auto_escape": bool(p.get("auto_escape", True))
        })
    return {
        "endpoints": endpoints,
        "query_params": params,
        "exclude_patterns": validated_exclude
    }

def save_payloads(package_name: str, data: Dict[str, List]):
    filepath = os.path.join(get_data_dir(), f"payloads_{package_name}.json")
    validated = _validate_payloads(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)
    return filepath

