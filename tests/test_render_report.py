import json
from pathlib import Path

from scripts import render_report


def test_build_report_generates_index_and_daily(tmp_path: Path, monkeypatch):
    root = tmp_path
    daily_dir = root / "data" / "daily"
    public_dir = root / "public"
    public_daily_dir = public_dir / "daily"
    domain_cache_path = root / "data" / "domain_registration_cache.json"
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
    monkeypatch.setattr(render_report, "DOMAIN_REG_CACHE_PATH", domain_cache_path)
    monkeypatch.setenv("DOMAIN_REG_LOOKUP_LIMIT", "0")

    index, daily_pages = render_report.build_report()

    assert index.exists()
    assert len(daily_pages) == 1
    assert (public_daily_dir / "2026-02-17.html").exists()

    index_html = index.read_text(encoding="utf-8")
    assert "2026-02-17" in index_html
    assert "Unique Added (Day)" in index_html
    assert "daily/2026-02-17.html?v=2026-02-17T10%3A00%3A00%2B08%3A00" in index_html

    day_html = (public_daily_dir / "2026-02-17.html").read_text(encoding="utf-8")
    assert "<h2>Unique URLs · 2</h2>" in day_html
    assert "https://x.com/1" in day_html
    assert "https://x.com/2" in day_html


def _day_payload(date_str, urls):
    return {
        "date": date_str,
        "runs": [
            {
                "run_at": f"{date_str}T10:00:00+08:00",
                "source_count": 1,
                "pages": [
                    {
                        "source_url": "https://a.com",
                        "final_url": "https://a.com",
                        "status": "ok",
                        "new_count": len(urls),
                        "new_urls": urls,
                        "error": None,
                    }
                ],
            }
        ],
    }


def test_daily_unique_section_dedupes_against_prior_days(tmp_path: Path, monkeypatch):
    root = tmp_path
    daily_dir = root / "data" / "daily"
    public_dir = root / "public"
    public_daily_dir = public_dir / "daily"
    domain_cache_path = root / "data" / "domain_registration_cache.json"
    daily_dir.mkdir(parents=True)

    (daily_dir / "2026-02-17.json").write_text(
        json.dumps(_day_payload("2026-02-17", ["https://x.com/1"])), encoding="utf-8"
    )
    (daily_dir / "2026-02-18.json").write_text(
        json.dumps(_day_payload("2026-02-18", ["https://x.com/1", "https://x.com/2"])), encoding="utf-8"
    )

    monkeypatch.setattr(render_report, "ROOT", root)
    monkeypatch.setattr(render_report, "DAILY_DIR", daily_dir)
    monkeypatch.setattr(render_report, "PUBLIC_DIR", public_dir)
    monkeypatch.setattr(render_report, "PUBLIC_DAILY_DIR", public_daily_dir)
    monkeypatch.setattr(render_report, "DOMAIN_REG_CACHE_PATH", domain_cache_path)
    monkeypatch.setenv("DOMAIN_REG_LOOKUP_LIMIT", "0")

    render_report.build_report()

    day18 = (public_daily_dir / "2026-02-18.html").read_text(encoding="utf-8")
    # x.com/1 already appeared on 2026-02-17, so the unique section lists only x.com/2
    assert "<h2>Unique URLs · 1</h2>" in day18
    assert "https://x.com/2" in day18
    assert "https://x.com/1" not in day18


def test_daily_page_renders_domain_registration_from_cache(tmp_path: Path, monkeypatch):
    root = tmp_path
    daily_dir = root / "data" / "daily"
    public_dir = root / "public"
    public_daily_dir = public_dir / "daily"
    domain_cache_path = root / "data" / "domain_registration_cache.json"
    daily_dir.mkdir(parents=True)

    payload = _day_payload("2026-02-17", ["https://blog.example.com/post-1"])
    (daily_dir / "2026-02-17.json").write_text(json.dumps(payload), encoding="utf-8")
    domain_cache_path.write_text(
        json.dumps(
            {
                "version": 1,
                "domains": {
                    "example.com": {"registration_date": "2018-01-20", "status": "found"},
                },
                "hosts": {"blog.example.com": "example.com"},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(render_report, "ROOT", root)
    monkeypatch.setattr(render_report, "DAILY_DIR", daily_dir)
    monkeypatch.setattr(render_report, "PUBLIC_DIR", public_dir)
    monkeypatch.setattr(render_report, "PUBLIC_DAILY_DIR", public_daily_dir)
    monkeypatch.setattr(render_report, "DOMAIN_REG_CACHE_PATH", domain_cache_path)
    monkeypatch.setenv("DOMAIN_REG_LOOKUP_LIMIT", "0")

    render_report.build_report()

    day_html = (public_daily_dir / "2026-02-17.html").read_text(encoding="utf-8")
    assert "domain: example.com · registered: 2018-01-20" in day_html
