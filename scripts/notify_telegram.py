from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT / "data" / "daily"

# Telegram sendMessage rejects payloads longer than 4096 characters.
TELEGRAM_MAX_CHARS = 4096


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


def _today_str() -> str:
    return datetime.now().astimezone().date().isoformat()


def _today_daily_path() -> Path:
    return DAILY_DIR / f"{_today_str()}.json"


def _prior_days_seen(today_str: str) -> set[str]:
    """URLs already reported on days before today (ISO date stems sort lexicographically)."""
    seen: set[str] = set()
    if not DAILY_DIR.exists():
        return seen
    for path in DAILY_DIR.glob("*.json"):
        if path.stem >= today_str:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for run in data.get("runs", []):
            for page in run.get("pages", []):
                for url in page.get("new_urls", []):
                    if isinstance(url, str):
                        seen.add(url)
    return seen


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


def build_message(
    daily_data: dict,
    report_base_url: str,
    max_items: int = 20,
    char_limit: int = TELEGRAM_MAX_CHARS,
    prior_seen: set[str] | None = None,
) -> str | None:
    runs = daily_data.get("runs", [])
    if not runs:
        return None

    latest = runs[-1]
    run_at = str(latest.get("run_at", ""))
    urls = _latest_new_urls(daily_data)
    if prior_seen:
        urls = [u for u in urls if u not in prior_seen]
    if not urls:
        return None

    total = len(urls)
    report_url = report_base_url.rstrip("/") + "/"
    day = str(daily_data.get("date", ""))

    head = [
        "URL Crawler - New External URLs Detected",
        f"Run at: {run_at}",
        f"Count: {total}",
        "",
    ]
    tail_links = [f"Report: {report_url}"]
    if day:
        tail_links.append(f"Daily: {report_url}daily/{day}.html")

    def assemble(shown: list[str]) -> str:
        omitted = total - len(shown)
        body = [f"- {u}" for u in shown]
        note = [f"... and {omitted} more"] if omitted else []
        return "\n".join(head + body + note + [""] + tail_links)

    shown = urls[:max_items]
    message = assemble(shown)
    # Trim further until the payload fits within Telegram's character limit.
    while shown and len(message) > char_limit:
        shown = shown[:-1]
        message = assemble(shown)
    return message


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
    prior_seen = _prior_days_seen(_today_str())
    message = build_message(
        daily_data,
        report_base_url or "http://localhost/",
        prior_seen=prior_seen,
    )
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
