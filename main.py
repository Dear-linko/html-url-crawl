from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from crawler.diff import build_baseline_index, compute_new_urls
from crawler.extractor import extract_a_hrefs
from crawler.fetcher import fetch_html
from crawler.normalize import filter_external_urls, normalize_and_dedupe
from crawler.storage import append_daily_added, load_baseline, load_source_urls_from_config, save_baseline


def crawl_pages(source_urls: list[str]) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for source_url in source_urls:
        try:
            final_url, html = fetch_html(source_url)
            hrefs = extract_a_hrefs(html)
            normalized_urls = normalize_and_dedupe(final_url, hrefs)
            urls = filter_external_urls(final_url, normalized_urls)
            pages.append(
                {
                    "source_url": source_url,
                    "final_url": final_url,
                    "status": "ok",
                    "urls": urls,
                    "error": None,
                }
            )
        except Exception as exc:
            pages.append(
                {
                    "source_url": source_url,
                    "final_url": source_url,
                    "status": "error",
                    "urls": [],
                    "error": str(exc),
                }
            )
    return pages


def cmd_init(root: Path, config_file: Path) -> int:
    source_urls = load_source_urls_from_config(config_file)
    pages = crawl_pages(source_urls)
    baseline_path = save_baseline(root, pages)
    print(f"baseline saved: {baseline_path}")
    for page in pages:
        print(f"[{page['status']}] {page['source_url']} urls={len(page['urls'])}")
    return 0


def _pages_for_baseline_update(
    baseline: dict[str, Any],
    current_pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous_by_source = {
        page.get("source_url"): page
        for page in baseline.get("pages", [])
        if isinstance(page, dict) and isinstance(page.get("source_url"), str)
    }

    pages: list[dict[str, Any]] = []
    for page in current_pages:
        source_url = page.get("source_url")
        if page.get("status") == "ok" or not isinstance(source_url, str):
            pages.append(page)
            continue

        previous = previous_by_source.get(source_url)
        if isinstance(previous, dict) and previous.get("urls"):
            pages.append(previous)
        else:
            pages.append(page)
    return pages


def cmd_check(root: Path, config_file: Path, update_baseline: bool) -> int:
    source_urls = load_source_urls_from_config(config_file)
    baseline = load_baseline(root)

    current_pages = crawl_pages(source_urls)
    baseline_index = build_baseline_index(baseline)
    diff_pages = compute_new_urls(baseline_index, current_pages)

    run_payload = {
        "run_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_count": len(source_urls),
        "pages": diff_pages,
    }
    daily_path = append_daily_added(root, run_payload)

    print(f"daily appended: {daily_path}")
    for page in diff_pages:
        print(f"[{page['status']}] new_count={page['new_count']} {page['source_url']}")
        if page["new_urls"]:
            print(json.dumps(page["new_urls"], ensure_ascii=False, indent=2))
        if page["status"] == "error":
            print(f"error: {page['error']}")

    if update_baseline:
        save_baseline(root, _pages_for_baseline_update(baseline, current_pages))
        print("baseline updated")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Incremental URL crawler")
    parser.add_argument(
        "subcommand",
        choices=["init", "check"],
        help="init baseline or check newly added URLs",
    )
    parser.add_argument("--update-baseline", action="store_true", help="update baseline after check")
    parser.add_argument("--config-file", default="config.json", help="path to config json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    config_file = Path(args.config_file)
    if not config_file.is_absolute():
        config_file = root / config_file

    if args.subcommand == "init":
        return cmd_init(root, config_file)
    if args.subcommand == "check":
        return cmd_check(root, config_file, args.update_baseline)
    raise ValueError(f"unknown subcommand: {args.subcommand}")


if __name__ == "__main__":
    raise SystemExit(main())
