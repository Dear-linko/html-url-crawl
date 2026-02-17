from __future__ import annotations

from urllib.parse import urljoin, urlsplit, urlunsplit


_BLOCKED_SCHEMES = ("javascript:", "mailto:", "tel:", "data:")


def normalize_href(base_url: str, href: str) -> str | None:
    raw = href.strip()
    if not raw:
        return None
    lower = raw.lower()
    if raw.startswith("#"):
        return None
    if lower.startswith(_BLOCKED_SCHEMES):
        return None

    absolute = urljoin(base_url, raw)
    parts = urlsplit(absolute)
    if parts.scheme not in ("http", "https"):
        return None

    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    if not hostname:
        return None

    port = parts.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    normalized = urlunsplit((scheme, netloc, parts.path or "/", parts.query, ""))
    return normalized


def normalize_and_dedupe(base_url: str, hrefs: list[str]) -> list[str]:
    items = set()
    for href in hrefs:
        normalized = normalize_href(base_url, href)
        if normalized:
            items.add(normalized)
    return sorted(items)


def filter_external_urls(page_url: str, urls: list[str]) -> list[str]:
    """Keep URLs whose hostname differs from the page hostname."""
    page_host = (urlsplit(page_url).hostname or "").lower()
    if not page_host:
        return []

    external = []
    for url in urls:
        host = (urlsplit(url).hostname or "").lower()
        if host and host != page_host:
            external.append(url)
    return sorted(set(external))
