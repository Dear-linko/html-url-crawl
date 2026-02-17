from __future__ import annotations

import time
from typing import Tuple

import requests


def fetch_html(url: str, timeout: int = 10, retries: int = 2) -> Tuple[str, str]:
    """Fetch HTML with simple retry and return (final_url, html)."""
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            return response.url, response.text
        except Exception as exc:  # pragma: no cover - validated via integration behavior
            last_err = exc
            if attempt < retries:
                time.sleep(0.5 * (2**attempt))
    raise RuntimeError(f"fetch failed: {url}: {last_err}")
