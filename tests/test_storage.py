import json
from datetime import datetime, timezone
from pathlib import Path

from crawler.storage import append_daily_added, load_source_urls_from_config


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_append_same_day(tmp_path: Path):
    run1 = {"run_at": "2026-02-17T10:00:00+00:00", "source_count": 3, "pages": []}
    run2 = {"run_at": "2026-02-17T11:00:00+00:00", "source_count": 3, "pages": []}

    t1 = datetime(2026, 2, 17, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 2, 17, 11, 0, 0, tzinfo=timezone.utc)

    p1 = append_daily_added(tmp_path, run1, now=t1)
    p2 = append_daily_added(tmp_path, run2, now=t2)

    assert p1 == p2
    data = _read(p1)
    assert data["date"] == "2026-02-17"
    assert len(data["runs"]) == 2


def test_append_cross_day(tmp_path: Path):
    run = {"run_at": "2026-02-17T10:00:00+00:00", "source_count": 3, "pages": []}

    p1 = append_daily_added(tmp_path, run, now=datetime(2026, 2, 17, 10, 0, 0, tzinfo=timezone.utc))
    p2 = append_daily_added(tmp_path, run, now=datetime(2026, 2, 18, 10, 0, 0, tzinfo=timezone.utc))

    assert p1 != p2
    assert p1.name == "2026-02-17.json"
    assert p2.name == "2026-02-18.json"


def test_load_source_urls_from_config(tmp_path: Path):
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "source_urls": [
                    "https://example.com/a",
                    " https://example.com/b ",
                    "",
                ]
            }
        ),
        encoding="utf-8",
    )
    urls = load_source_urls_from_config(config)
    assert urls == ["https://example.com/a", "https://example.com/b"]
