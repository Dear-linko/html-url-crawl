from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _today_daily_path() -> Path:
    day = datetime.now().date().isoformat()
    return ROOT / "data" / "daily" / f"{day}.json"


def _latest_new_urls(daily_data: dict) -> list[str]:
    runs = daily_data.get("runs", [])
    if not runs:
        return []
    latest = runs[-1]
    urls = set()
    for page in latest.get("pages", []):
        for url in page.get("new_urls", []):
            if isinstance(url, str):
                urls.add(url)
    return sorted(urls)


def build_message(daily_data: dict, report_base_url: str, max_items: int = 20) -> str | None:
    runs = daily_data.get("runs", [])
    if not runs:
        return None

    latest = runs[-1]
    run_at = str(latest.get("run_at", ""))
    urls = _latest_new_urls(daily_data)
    if not urls:
        return None

    head = [
        "URL Crawler - New External URLs Detected",
        f"Run at: {run_at}",
        f"Count: {len(urls)}",
        "",
    ]
    body = [f"- {u}" for u in urls[:max_items]]
    tail = []
    if len(urls) > max_items:
        tail.append(f"... and {len(urls) - max_items} more")

    report_url = report_base_url.rstrip("/") + "/"
    day = str(daily_data.get("date", ""))
    tail.append(f"Report: {report_url}")
    if day:
        tail.append(f"Daily: {report_url}daily/{day}.html")

    return "\n".join(head + body + [""] + tail)


def send_telegram_message(token: str, chat_id: str, text: str, timeout: int = 15) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=timeout)
    response.raise_for_status()


def main() -> int:
    load_env_file(ROOT / ".env")

    daily_path = _today_daily_path()
    if not daily_path.exists():
        print(f"skip notify: daily file not found: {daily_path}")
        return 0

    daily_data = json.loads(daily_path.read_text(encoding="utf-8"))

    report_base_url = os.getenv("REPORT_BASE_URL", "").strip()
    message = build_message(daily_data, report_base_url or "http://localhost/")
    if not message:
        print("skip notify: no new urls in latest run")
        return 0

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("skip notify: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing")
        return 0

    send_telegram_message(token, chat_id, message)
    print("telegram notification sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
