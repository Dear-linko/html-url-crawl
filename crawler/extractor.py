from __future__ import annotations

from bs4 import BeautifulSoup


def extract_a_hrefs(html: str) -> list[str]:
    """Extract href values from <a> tags only."""
    soup = BeautifulSoup(html, "html.parser")
    hrefs: list[str] = []
    for tag in soup.find_all("a"):
        href = tag.get("href")
        if isinstance(href, str):
            hrefs.append(href)
    return hrefs


def extract_base_href(html: str) -> str | None:
    """Return the first <base href> value, used as the base for resolving relative links."""
    soup = BeautifulSoup(html, "html.parser")
    base = soup.find("base")
    if base is None:
        return None
    href = base.get("href")
    if isinstance(href, str) and href.strip():
        return href.strip()
    return None
