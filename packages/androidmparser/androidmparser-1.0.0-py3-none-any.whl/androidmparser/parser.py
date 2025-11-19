# parser.py
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Tuple

ANDROID_NS = "http://schemas.android.com/apk/res/android"

def _get_attr(elem, attr):
    if elem is None:
        return None
    return elem.get(f"{{{ANDROID_NS}}}{attr}")

def extract_deeplinks_from_manifest(root) -> Tuple[List[str], List[str]]:
    deeplinks = []
    applinks = []

    # Ищем и <activity>, и <activity-alias>
    for activity in root.findall(".//activity") + root.findall(".//activity-alias"):
        exported = _get_attr(activity, "exported")
        # Если exported не задан, но есть LAUNCHER — считаем экспортированным
        has_launcher = any(
            "android.intent.category.LAUNCHER" in {_get_attr(cat, "name") for cat in intent_filter.findall("category")}
            for intent_filter in activity.findall("intent-filter")
        )
        is_exported = (exported == "true") or (exported is None and has_launcher)

        if not is_exported:
            continue

        for intent_filter in activity.findall("intent-filter"):
            actions = {_get_attr(a, "name") for a in intent_filter.findall("action")}
            categories = {_get_attr(c, "name") for c in intent_filter.findall("category")}

            if "android.intent.action.VIEW" not in actions:
                continue
            if "android.intent.category.BROWSABLE" not in categories:
                continue

            auto_verify = intent_filter.get("autoVerify") == "true"
            datas = intent_filter.findall("data")
            if not datas:
                continue

            # Собираем все возможные атрибуты из <data>
            schemes = []
            hosts = []
            paths = []
            path_patterns = []
            path_prefixes = []

            for d in datas:
                s = _get_attr(d, "scheme")
                h = _get_attr(d, "host")
                pt = _get_attr(d, "path")
                pp = _get_attr(d, "pathPattern")
                px = _get_attr(d, "pathPrefix")

                if s:
                    schemes.append(s)
                if h:
                    hosts.append(h)
                if pt:
                    paths.append(pt)
                if pp:
                    path_patterns.append(pp)
                if px:
                    path_prefixes.append(px)

            # Если нет схемы — пропускаем
            if not schemes:
                continue

            # Если хостов нет — генерируем только схему (например, spaysdk://)
            if not hosts:
                for scheme in schemes:
                    url = f"{scheme}://"
                    deeplinks.append(url)
                    if auto_verify:
                        applinks.append(url)
                continue

            # Иначе комбинируем схемы и хосты
            for scheme in schemes:
                for host in hosts:
                    base = f"{scheme}://{host}"
                    # Без пути
                    deeplinks.append(base)
                    if auto_verify:
                        applinks.append(base)

                    # С путями
                    for path_list in [paths, path_patterns, path_prefixes]:
                        for path in path_list:
                            full_url = f"{scheme}://{host}{path}"
                            deeplinks.append(full_url)
                            if auto_verify:
                                applinks.append(full_url)

    # Убираем дубликаты и сортируем
    return sorted(set(deeplinks)), sorted(set(applinks))


def parse_manifest(manifest_input: str) -> Dict[str, Any]:
    """
    manifest_input: str — либо путь к файлу, либо XML-содержимое
    """
    from io import StringIO
    import os

    if os.path.isfile(manifest_input):
        tree = ET.parse(manifest_input)
    else:
        # Считаем, что это XML-строка
        try:
            tree = ET.parse(StringIO(manifest_input.strip()))
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML content: {e}")

    root = tree.getroot()

    package = root.get("package")
    app_elem = root.find("application")
    application_class = _get_attr(app_elem, "name") if app_elem is not None else None

    components = {
        "activities": [],
        "services": [],
        "receivers": [],
        "providers": []
    }

    dangerous_permissions = [
        "INTERNET", "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION",
        "READ_CONTACTS", "WRITE_EXTERNAL_STORAGE", "READ_EXTERNAL_STORAGE",
        "CAMERA", "RECORD_AUDIO", "READ_SMS", "SEND_SMS", "CALL_PHONE",
        "READ_PHONE_STATE", "USE_BIOMETRIC", "USE_FINGERPRINT"
    ]

    permissions = []
    for perm in root.findall("uses-permission"):
        name = _get_attr(perm, "name")
        if name:
            short_name = name.split(".")[-1]
            is_dangerous = short_name in dangerous_permissions
            permissions.append({"name": name, "dangerous": is_dangerous})

    queries = []
    for q in root.findall("queries/*"):
        pkg = _get_attr(q, "name")
        if pkg:
            queries.append(pkg)
        elif q.tag == "intent":
            action = q.find("action")
            if action is not None:
                act_name = _get_attr(action, "name")
                queries.append(f"<intent> {act_name}")

    def extract_components(tag_name, key):
        for comp in root.findall(tag_name):
            cname = _get_attr(comp, "name")
            exported = _get_attr(comp, "exported") == "true"
            authority = _get_attr(comp, "authorities")  # ← новое!
            filters = []
            for intent_filter in comp.findall("intent-filter"):
                actions = [_get_attr(a, "name") for a in intent_filter.findall("action") if _get_attr(a, "name")]
                categories = [_get_attr(c, "name") for c in intent_filter.findall("category") if _get_attr(c, "name")]
                data_elems = intent_filter.findall("data")
                schemes = []
                hosts = []
                for d in data_elems:
                    s = _get_attr(d, "scheme")
                    h = _get_attr(d, "host")
                    if s:
                        schemes.append(s)
                    if h:
                        hosts.append(h)
                filters.append({
                    "actions": actions,
                    "categories": categories,
                    "schemes": schemes,
                    "hosts": hosts
                })
            components[key].append({
                "class": cname,
                "exported": exported,
                "authority": authority,
                "intent_filters": filters
            })

    extract_components("application/activity", "activities")
    extract_components("application/service", "services")
    extract_components("application/receiver", "receivers")
    extract_components("application/provider", "providers")

    # 🔥 Вот здесь вызываем новую функцию для deeplinks
    deeplinks, applinks = extract_deeplinks_from_manifest(root)

    return {
        "package": package,
        "application_class": application_class,
        "permissions": permissions,
        "queries": queries,
        "components": components,
        "deeplinks": deeplinks,
        "applinks": applinks,
        "min_sdk": _get_attr(root.find("uses-sdk"), "minSdkVersion"),
        "target_sdk": _get_attr(root.find("uses-sdk"), "targetSdkVersion"),
    }