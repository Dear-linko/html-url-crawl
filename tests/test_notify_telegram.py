from scripts.notify_telegram import build_message, TELEGRAM_MAX_CHARS


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


def _daily_with(urls):
    return {
        "date": "2026-02-17",
        "runs": [{"run_at": "2026-02-17T10:00:00+08:00", "pages": [{"new_urls": urls, "new_count": len(urls)}]}],
    }


def test_build_message_excludes_prior_seen_urls():
    daily = _daily_with(["https://x.com/1", "https://x.com/2"])
    msg = build_message(daily, "https://example.com/report", prior_seen={"https://x.com/1"})
    assert msg is not None
    assert "Count: 1" in msg
    assert "https://x.com/2" in msg
    assert "https://x.com/1" not in msg


def test_build_message_returns_none_when_all_prior_seen():
    daily = _daily_with(["https://x.com/1"])
    assert build_message(daily, "https://example.com/report", prior_seen={"https://x.com/1"}) is None


def test_build_message_stays_within_telegram_limit():
    urls = [f"https://x.com/{'p' * 300}/{i}" for i in range(50)]
    daily = _daily_with(urls)
    msg = build_message(daily, "https://example.com/report", max_items=50)
    assert msg is not None
    assert len(msg) <= TELEGRAM_MAX_CHARS
    assert "more" in msg  # some URLs were trimmed
    assert "Count: 50" in msg  # header still reports the true total
