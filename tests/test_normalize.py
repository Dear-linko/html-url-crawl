from crawler.normalize import filter_external_urls, normalize_href


def test_normalize_relative_and_strip_fragment():
    got = normalize_href("https://Example.COM/base/path", "../a?q=1#top")
    assert got == "https://example.com/a?q=1"


def test_normalize_filters_invalid_schemes():
    assert normalize_href("https://example.com", "javascript:void(0)") is None
    assert normalize_href("https://example.com", "#section") is None


def test_normalize_remove_default_port():
    assert normalize_href("https://example.com", "https://EXAMPLE.com:443/p") == "https://example.com/p"


def test_filter_external_urls_by_hostname():
    urls = [
        "https://example.com/a",
        "https://example.com/b",
        "https://other.com/x",
        "https://sub.example.com/y",
    ]
    got = filter_external_urls("https://example.com/page", urls)
    assert got == ["https://other.com/x", "https://sub.example.com/y"]
