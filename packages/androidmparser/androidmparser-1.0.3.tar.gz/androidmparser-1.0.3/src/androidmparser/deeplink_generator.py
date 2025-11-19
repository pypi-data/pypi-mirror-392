# deeplink_generator.py
from urllib.parse import urlparse, urlunparse, urlencode
from typing import List, Tuple

def generate_intruder_html(base_urls: List[str], endpoints: List[str], query_params: List[Tuple[str, str]], combine_all: bool = True) -> str:
    results = set()

    # 1. Все исходные ссылки — без изменений
    for url in base_urls:
        results.add(url)

    # 2. Расширяем каждую ссылку по правилам
    for url in base_urls:
        parsed = urlparse(url)
        scheme = parsed.scheme
        netloc = parsed.netloc
        path = parsed.path

        # === HTTP/HTTPS: полная поддержка ===
        if scheme in ("http", "https"):
            base = f"{scheme}://{netloc}"
            # Endpoints
            for ep in endpoints or ["/"]:
                if not ep.startswith("/"):
                    ep = "/" + ep
                full_path = ep if ep != "/" else ""
                results.add(f"{base}{full_path}")
            # Query
            if query_params:
                qs = urlencode(query_params)
                # базовый путь + query
                results.add(f"{base}{path}?{qs}")
                # endpoints + query
                for ep in endpoints or ["/"]:
                    if not ep.startswith("/"):
                        ep = "/" + ep
                    full_path = ep if ep != "/" else ""
                    results.add(f"{base}{full_path}?{qs}")

        # === Custom schemes: только query (и осторожно — path) ===
        else:
            # 2.1. Query-параметры — ДА, почти всегда работают
            if query_params:
                full_qs = urlencode(query_params)
                new_query = parsed.query + ("&" if parsed.query else "") + full_qs
                new_url = urlunparse((scheme, netloc, path, "", new_query, ""))
                results.add(new_url)

            # 2.2. Endpoints — только если нет host (например, wildberries://)
            if endpoints:
                # Случай A: есть host (spaysdk://payment) → добавляем путь, НО без дублирования /
                if netloc:
                    for ep in endpoints:
                        if ep == "/":
                            continue
                        # Убираем начальные /, чтобы не было spaysdk://payment//test
                        ep_clean = ep.lstrip("/")
                        if not ep_clean:
                            continue
                        new_path = path.rstrip("/") + "/" + ep_clean
                        new_url = urlunparse((scheme, netloc, new_path, "", "", ""))
                        results.add(new_url)

                        # + query
                        if query_params:
                            qs = urlencode(query_params)
                            new_url = urlunparse((scheme, netloc, new_path, "", qs, ""))
                            results.add(new_url)

                # Случай B: нет host (wildberries://) → генерируем wildberries://endpoint
                else:
                    for ep in endpoints:
                        if ep == "/":
                            continue
                        # Убираем все / → endpoint как host или как path после ///
                        # Вариант 1 (рекомендуемый): как host — wildberries://endpoint
                        host = ep.lstrip("/").rstrip("/")
                        if host:
                            new_url = f"{scheme}://{host}"
                            results.add(new_url)
                            if query_params:
                                qs = urlencode(query_params)
                                results.add(f"{new_url}?{qs}")

    # Сортируем
    def sort_key(u):
        if u.startswith("https://"): return (0, u)
        if u.startswith("http://"): return (1, u)
        return (2, u)

    sorted_urls = sorted(results, key=sort_key)
    links = "\n".join(f'<a href="{u}">{u}</a><br>' for u in sorted_urls)
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Deeplinks Payloads</title>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Consolas, monospace; background: #282a36; color: #50fa7b; padding: 20px; }}
    a {{ color: #bd93f9; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
<h2>Generated Payloads ({len(sorted_urls)}):</h2>
{links}
</body>
</html>"""