from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def ensure_data_dirs(root: Path) -> None:
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / "daily").mkdir(parents=True, exist_ok=True)


def load_source_urls_from_config(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_urls = data.get("source_urls", [])
    if not isinstance(source_urls, list):
        raise ValueError("config 'source_urls' must be a list")

    urls: list[str] = []
    for item in source_urls:
        if isinstance(item, str):
            url = item.strip()
            if url:
                urls.append(url)
    if not urls:
        raise ValueError("config 'source_urls' is empty")
    return urls


def save_baseline(root: Path, pages: list[dict[str, Any]]) -> Path:
    ensure_data_dirs(root)
    payload = {
        "version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "pages": pages,
    }
    path = root / "data" / "baseline.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_baseline(root: Path) -> dict[str, Any]:
    path = root / "data" / "baseline.json"
    if not path.exists():
        raise FileNotFoundError("baseline missing, run: python3 main.py init")
    return json.loads(path.read_text(encoding="utf-8"))


def append_daily_added(root: Path, run_payload: dict[str, Any], now: datetime | None = None) -> Path:
    ensure_data_dirs(root)
    current = (now or datetime.now().astimezone())
    date_str = current.date().isoformat()
    daily_path = root / "data" / "daily" / f"{date_str}.json"

    if daily_path.exists():
        daily = json.loads(daily_path.read_text(encoding="utf-8"))
        if daily.get("date") != date_str:
            daily = {"date": date_str, "runs": []}
    else:
        daily = {"date": date_str, "runs": []}

    daily.setdefault("runs", []).append(run_payload)
    daily_path.write_text(json.dumps(daily, ensure_ascii=False, indent=2), encoding="utf-8")
    return daily_path
