import json
from pathlib import Path

from scripts import render_report


def test_build_report_generates_index_and_daily(tmp_path: Path, monkeypatch):
    root = tmp_path
    daily_dir = root / "data" / "daily"
    public_dir = root / "public"
    public_daily_dir = public_dir / "daily"
    daily_dir.mkdir(parents=True)

    payload = {
        "date": "2026-02-17",
        "runs": [
            {
                "run_at": "2026-02-17T10:00:00+08:00",
                "source_count": 1,
                "pages": [
                    {
                        "source_url": "https://a.com",
                        "final_url": "https://a.com",
                        "status": "ok",
                        "new_count": 2,
                        "new_urls": ["https://x.com/1", "https://x.com/2"],
                        "error": None,
                    }
                ],
            }
        ],
    }
    (daily_dir / "2026-02-17.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(render_report, "ROOT", root)
    monkeypatch.setattr(render_report, "DAILY_DIR", daily_dir)
    monkeypatch.setattr(render_report, "PUBLIC_DIR", public_dir)
    monkeypatch.setattr(render_report, "PUBLIC_DAILY_DIR", public_daily_dir)

    index, daily_pages = render_report.build_report()

    assert index.exists()
    assert len(daily_pages) == 1
    assert (public_daily_dir / "2026-02-17.html").exists()

    index_html = index.read_text(encoding="utf-8")
    assert "2026-02-17" in index_html
    assert "Unique Added (Day)" in index_html
