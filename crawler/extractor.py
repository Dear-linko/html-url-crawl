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
