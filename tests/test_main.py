import json
from pathlib import Path

import main
from crawler.storage import load_baseline, save_baseline


def test_crawl_pages_resolves_relative_links_against_base_href(monkeypatch) -> None:
    html = """
    <html><head><base href="https://cdn.other.example/app/"></head>
    <body><a href="page.html">x</a><a href="https://third.example/y">y</a></body></html>
    """
    monkeypatch.setattr(main, "fetch_html", lambda url: ("https://site.example/", html))

    page = main.crawl_pages(["https://site.example/"])[0]

    assert page["status"] == "ok"
    # "page.html" resolves against <base>, not the page URL
    assert "https://cdn.other.example/app/page.html" in page["urls"]
    assert "https://third.example/y" in page["urls"]


def test_check_update_preserves_previous_urls_when_current_fetch_fails(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"source_urls": ["https://source.example/page"]}), encoding="utf-8")
    save_baseline(
        tmp_path,
        [
            {
                "source_url": "https://source.example/page",
                "final_url": "https://source.example/page",
                "status": "ok",
                "urls": ["https://old.example/a"],
                "error": None,
            }
        ],
    )

    monkeypatch.setattr(
        main,
        "crawl_pages",
        lambda urls: [
            {
                "source_url": urls[0],
                "final_url": urls[0],
                "status": "error",
                "urls": [],
                "error": "timeout",
            }
        ],
    )

    assert main.cmd_check(tmp_path, config, update_baseline=True) == 0

    baseline = load_baseline(tmp_path)
    assert baseline["pages"][0]["status"] == "ok"
    assert baseline["pages"][0]["urls"] == ["https://old.example/a"]

    daily = json.loads(next((tmp_path / "data" / "daily").glob("*.json")).read_text(encoding="utf-8"))
    page = daily["runs"][0]["pages"][0]
    assert page["status"] == "error"
    assert page["new_count"] == 0
