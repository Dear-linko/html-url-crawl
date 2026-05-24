from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TextIO


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
    _write_json(path, payload)
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
    _write_json(daily_path, daily)
    return daily_path


def _write_json(path: Path, data: Any) -> None:
    def write(f: TextIO) -> None:
        json.dump(data, f, ensure_ascii=False, indent=2)

    _atomic_write(path, write)


def _atomic_write(path: Path, write: Callable[[TextIO], None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            write(f)
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise
