from crawler.diff import build_baseline_index, compute_new_urls


def test_compute_new_urls_only_added():
    baseline = {
        "pages": [
            {
                "source_url": "https://example.com/page",
                "urls": ["https://a.com/1", "https://a.com/2"],
            }
        ]
    }
    current_pages = [
        {
            "source_url": "https://example.com/page",
            "final_url": "https://example.com/page",
            "status": "ok",
            "urls": ["https://a.com/1", "https://a.com/2", "https://a.com/3"],
            "error": None,
        }
    ]

    index = build_baseline_index(baseline)
    result = compute_new_urls(index, current_pages)

    assert result[0]["new_count"] == 1
    assert result[0]["new_urls"] == ["https://a.com/3"]


def test_compute_new_urls_on_error_page():
    index = {}
    current_pages = [
        {
            "source_url": "https://example.com/404",
            "final_url": "https://example.com/404",
            "status": "error",
            "urls": [],
            "error": "fetch failed",
        }
    ]

    result = compute_new_urls(index, current_pages)

    assert result[0]["status"] == "error"
    assert result[0]["new_count"] == 0
    assert result[0]["new_urls"] == []
