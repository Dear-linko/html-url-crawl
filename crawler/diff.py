from __future__ import annotations

from typing import Any


def build_baseline_index(baseline: dict[str, Any]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for page in baseline.get("pages", []):
        source_url = page.get("source_url")
        urls = page.get("urls", [])
        if isinstance(source_url, str):
            index[source_url] = set(urls)
    return index


def compute_new_urls(
    baseline_index: dict[str, set[str]],
    current_pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for page in current_pages:
        source_url = page["source_url"]
        status = page["status"]
        current_urls = set(page.get("urls", [])) if status == "ok" else set()
        base_urls = baseline_index.get(source_url, set())
        new_urls = sorted(current_urls - base_urls)
        result.append(
            {
                "source_url": source_url,
                "final_url": page.get("final_url"),
                "status": status,
                "new_count": len(new_urls),
                "new_urls": new_urls,
                "error": page.get("error"),
            }
        )
    return result
