from scripts.notify_telegram import build_message


def test_build_message_returns_none_when_no_new_urls():
    daily = {
        "date": "2026-02-17",
        "runs": [
            {
                "run_at": "2026-02-17T10:00:00+08:00",
                "pages": [
                    {
                        "new_urls": [],
                        "new_count": 0,
                    }
                ],
            }
        ],
    }
    assert build_message(daily, "https://example.com/report") is None


def test_build_message_contains_report_and_urls():
    daily = {
        "date": "2026-02-17",
        "runs": [
            {
                "run_at": "2026-02-17T10:00:00+08:00",
                "pages": [
                    {
                        "new_urls": ["https://x.com/1", "https://x.com/2"],
                        "new_count": 2,
                    }
                ],
            }
        ],
    }
    msg = build_message(daily, "https://example.com/report")
    assert msg is not None
    assert "Count: 2" in msg
    assert "https://x.com/1" in msg
    assert "https://example.com/report/" in msg
    assert "daily/2026-02-17.html" in msg
