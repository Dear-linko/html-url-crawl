from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT / "data" / "daily"
PUBLIC_DIR = ROOT / "public"
PUBLIC_DAILY_DIR = PUBLIC_DIR / "daily"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_day_unique_urls(day_data: dict[str, Any], seen: set | None = None) -> list[str]:
    """Collect unique new URLs for a day, optionally excluding URLs already seen on prior days."""
    unique: set = set()
    for run in day_data.get("runs", []):
        for page in run.get("pages", []):
            for url in page.get("new_urls", []):
                if isinstance(url, str):
                    unique.add(url)
    if seen is not None:
        unique -= seen
    return sorted(unique)


def _base_styles() -> str:
    return """
:root {
  --tw-bg: #f8fafc;
  --tw-surface: #ffffff;
  --tw-surface-soft: #f8fafc;
  --tw-text: #0f172a;
  --tw-muted: #64748b;
  --tw-line: #e2e8f0;
  --tw-line-strong: #cbd5e1;
  --tw-brand: #0f172a;
  --tw-ok-bg: #f0fdf4;
  --tw-ok-text: #166534;
  --tw-ok-line: #bbf7d0;
  --tw-err-bg: #fef2f2;
  --tw-err-text: #991b1b;
  --tw-err-line: #fecaca;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--tw-bg);
  color: var(--tw-text);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  line-height: 1.6;
}
a {
  color: var(--tw-brand);
  text-decoration: none;
  border-bottom: 1px solid transparent;
}
a:hover { border-bottom-color: var(--tw-line-strong); }

.container {
  width: min(1040px, calc(100% - 2rem));
  margin: 0 auto;
  padding: 2rem 0 2.5rem;
}

.stack { display: grid; gap: 1rem; }

.card {
  background: var(--tw-surface);
  border: 1px solid var(--tw-line);
  border-radius: 0.75rem;
}

.card-pad { padding: 1rem 1.1rem; }

.prose h1,
.prose h2,
.prose h3,
.prose p { margin: 0; }
.prose h1 {
  font-size: 1.5rem;
  line-height: 1.25;
  letter-spacing: -0.02em;
  font-weight: 700;
}
.prose h2 {
  font-size: 1.12rem;
  line-height: 1.4;
  letter-spacing: -0.01em;
  font-weight: 650;
}
.prose h3 {
  font-size: 0.95rem;
  line-height: 1.45;
  color: #334155;
  font-weight: 600;
}
.prose .prose-muted {
  margin-top: 0.4rem;
  color: var(--tw-muted);
  font-size: 0.9rem;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}
.metric {
  background: var(--tw-surface);
  border: 1px solid var(--tw-line);
  border-radius: 0.7rem;
  padding: 0.8rem 0.9rem;
}
.metric-label {
  margin: 0;
  color: var(--tw-muted);
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}
.metric-value {
  margin: 0.35rem 0 0;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--tw-line);
  border-radius: 0.65rem;
}
.mobile-list { display: none; }
.mobile-item + .mobile-item { margin-top: 0.65rem; }
.mobile-item {
  border: 1px solid var(--tw-line);
  border-radius: 0.65rem;
  padding: 0.72rem;
  background: var(--tw-surface-soft);
}
.mobile-item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.6rem;
}
.mobile-date {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 700;
  line-height: 1.35;
}
.mobile-time {
  margin: 0.3rem 0 0;
  color: var(--tw-muted);
  font-size: 0.78rem;
  line-height: 1.4;
}
.mobile-metrics {
  margin-top: 0.6rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.45rem;
}
.mobile-metric {
  border: 1px solid var(--tw-line);
  border-radius: 0.55rem;
  background: #fff;
  padding: 0.42rem 0.5rem;
}
.mobile-metric-label {
  margin: 0;
  color: var(--tw-muted);
  font-size: 0.7rem;
  line-height: 1.3;
}
.mobile-metric-value {
  margin: 0.18rem 0 0;
  font-size: 0.88rem;
  font-weight: 700;
  line-height: 1.35;
}
table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
}
th, td {
  border-bottom: 1px solid var(--tw-line);
  padding: 0.78rem 0.84rem;
  text-align: left;
  vertical-align: top;
}
tr:last-child td { border-bottom: 0; }
th {
  background: var(--tw-surface-soft);
  color: var(--tw-muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}
td { font-size: 0.9rem; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  border-radius: 999px;
  border: 1px solid var(--tw-line-strong);
  background: var(--tw-surface-soft);
  color: #334155;
  font-size: 0.74rem;
  font-weight: 650;
  line-height: 1;
  padding: 0.22rem 0.56rem;
}
.badge-ok {
  color: var(--tw-ok-text);
  border-color: var(--tw-ok-line);
  background: var(--tw-ok-bg);
}
.badge-err {
  color: var(--tw-err-text);
  border-color: var(--tw-err-line);
  background: var(--tw-err-bg);
}

.run {
  border: 1px solid var(--tw-line);
  border-radius: 0.65rem;
  overflow: hidden;
}
.run + .run { margin-top: 0.75rem; }
.run-head {
  border-bottom: 1px solid var(--tw-line);
  background: var(--tw-surface-soft);
  color: var(--tw-muted);
  font-size: 0.8rem;
  padding: 0.56rem 0.72rem;
}
.page {
  padding: 0.78rem;
  border-bottom: 1px solid var(--tw-line);
}
.page:last-child { border-bottom: 0; }
.page-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.42rem;
}
.page-source {
  margin: 0;
  font-size: 0.9rem;
  color: #1e293b;
  word-break: break-all;
}

.url-list {
  list-style: none;
  margin: 0.55rem 0 0;
  padding: 0;
  display: grid;
  gap: 0.42rem;
}
.url-item {
  background: var(--tw-surface-soft);
  border: 1px solid var(--tw-line);
  border-radius: 0.55rem;
  padding: 0.48rem 0.6rem;
  word-break: break-all;
  font-size: 0.84rem;
  line-height: 1.5;
}

.error-box {
  margin-top: 0.55rem;
  background: var(--tw-err-bg);
  border: 1px solid var(--tw-err-line);
  border-radius: 0.55rem;
  padding: 0.5rem 0.6rem;
  color: var(--tw-err-text);
  font-size: 0.8rem;
  word-break: break-all;
}

.link-back {
  display: inline-flex;
  align-items: center;
  margin-top: 0.6rem;
  color: var(--tw-muted);
  font-size: 0.85rem;
}

@media (max-width: 960px) {
  .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .container {
    width: calc(100% - 1rem);
    padding: 0.95rem 0 1.5rem;
  }
  .card-pad { padding: 0.82rem 0.88rem; }
  .prose h1 { font-size: 1.16rem; }
  .prose .prose-muted { font-size: 0.82rem; }
  .metrics { grid-template-columns: 1fr; gap: 0.55rem; }
  .metric { padding: 0.68rem 0.76rem; }
  .metric-value { font-size: 1.05rem; }
  .table-wrap { border-radius: 0.55rem; }
  th, td { padding: 0.62rem 0.62rem; font-size: 0.82rem; }
  .table-wrap { display: none; }
  .mobile-list { display: block; }
  .run-head { padding: 0.5rem 0.6rem; }
  .page { padding: 0.66rem; }
}
"""


def _render_day_page(day_data: dict[str, Any], day_file: Path, seen: set | None = None) -> str:
    """Render HTML for a single day. seen = URLs already shown on prior days (to deduplicate)."""
    day = str(day_data.get("date", day_file.stem))
    runs = day_data.get("runs", [])
    run_blocks: list[str] = []

    for idx, run in enumerate(reversed(runs), start=1):
        run_at = html.escape(str(run.get("run_at", "")))
        # Only show pages with new URLs
        pages = [p for p in run.get("pages", []) if int(p.get("new_count", 0) or 0) > 0]
        page_blocks: list[str] = []

        for page in pages:
            source = html.escape(str(page.get("source_url", "")))
            status = str(page.get("status", "")).lower()
            status_badge = "badge-ok" if status == "ok" else "badge-err"
            status_text = html.escape(status or "unknown")

            raw_urls = page.get("new_urls", [])
            # Filter out URLs already shown on prior days (cross-day dedup)
            if seen is not None:
                urls = [u for u in raw_urls if isinstance(u, str) and u not in seen]
            else:
                urls = [u for u in raw_urls if isinstance(u, str)]
            count = len(urls)  # Show deduplicated count
            if count == 0:
                continue  # Skip pages where all URLs were already shown before

            url_items = "".join(
                f"<li class='url-item'><a href='{html.escape(u)}' target='_blank' rel='noreferrer'>{html.escape(u)}</a></li>"
                for u in urls
            )
            urls_html = f"<ul class='url-list'>{url_items}</ul>" if url_items else "<p class='prose-muted'>No new URLs.</p>"

            error = page.get("error")
            err_html = f"<div class='error-box'>{html.escape(str(error))}</div>" if error else ""

            page_blocks.append(
                "\n".join(
                    [
                        "<article class='page prose'>",
                        "<div class='page-meta'>",
                        f"<span class='badge {status_badge}'>{status_text}</span>",
                        f"<span class='badge'>new: {count}</span>",
                        "</div>",
                        f"<p class='page-source'>{source}</p>",
                        urls_html,
                        err_html,
                        "</article>",
                    ]
                )
            )

        run_blocks.append(
            "\n".join(
                [
                    "<section class='run'>",
                    f"<div class='run-head'>Run {idx} · {run_at}</div>",
                    "".join(page_blocks) if page_blocks else "<div class='page prose'><p>No pages.</p></div>",
                    "</section>",
                ]
            )
        )

    latest_total = 0
    if runs:
        for p in runs[-1].get("pages", []):
            latest_total += int(p.get("new_count", 0) or 0)

    day_unique = _collect_day_unique_urls(day_data, seen=seen)
    unique_items = "".join(
        f"<li class='url-item'><a href='{html.escape(u)}' target='_blank' rel='noreferrer'>{html.escape(u)}</a></li>"
        for u in day_unique
    )
    unique_html = (
        f"<ul class='url-list'>{unique_items}</ul>"
        if unique_items
        else "<p class='prose-muted'>No new URLs.</p>"
    )

    return f"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Daily Report {html.escape(day)}</title>
  <style>{_base_styles()}</style>
</head>
<body>
  <main class='container stack'>
    <header class='card card-pad prose'>
      <h1>Daily URL Report · {html.escape(day)}</h1>
      <p class='prose-muted'>Latest run added: {latest_total}</p>
      <a class='link-back' href='../index.html'>← Back to index</a>
    </header>

    <section class='metrics'>
      <article class='metric'><p class='metric-label'>Runs</p><p class='metric-value'>{len(runs)}</p></article>
      <article class='metric'><p class='metric-label'>Unique Added (Day)</p><p class='metric-value'>{len(day_unique)}</p></article>
      <article class='metric'><p class='metric-label'>Latest Added</p><p class='metric-value'>{latest_total}</p></article>
      <article class='metric'><p class='metric-label'>Date</p><p class='metric-value'>{html.escape(day)}</p></article>
    </section>

    <section class='card card-pad prose'>
      <h2>Unique URLs · {len(day_unique)}</h2>
      {unique_html}
    </section>

    <section class='card card-pad'>
      {''.join(run_blocks) if run_blocks else '<div class="prose"><p>No runs.</p></div>'}
    </section>
  </main>
</body>
</html>
"""


def _render_index(days: list[dict[str, Any]]) -> str:
    rows = []
    mobile_items = []
    total_day_added = 0
    total_latest_added = 0

    for day in days:
        day_str = str(day["date"])
        latest_run_at = str(day.get("latest_run_at", ""))
        cache_bust = quote(latest_run_at) if latest_run_at else day_str
        day_href = f"daily/{day_str}.html?v={cache_bust}"
        day_total_new = int(day.get("day_total_new", 0))
        latest_new = int(day.get("latest_new", 0))
        total_day_added += day_total_new
        total_latest_added += latest_new

        rows.append(
            f"<tr>"
            f"<td><a href='{html.escape(day_href)}'>{html.escape(day_str)}</a></td>"
            f"<td>{html.escape(latest_run_at or '-')}</td>"
            f"<td><span class='badge badge-ok'>{day_total_new}</span></td>"
            f"<td><span class='badge'>{latest_new}</span></td>"
            f"</tr>"
        )
        mobile_items.append(
            "<article class='mobile-item'>"
            "<div class='mobile-item-top'>"
            f"<div><p class='mobile-date'><a href='{html.escape(day_href)}'>{html.escape(day_str)}</a></p>"
            f"<p class='mobile-time'>{html.escape(latest_run_at or '-')}</p></div>"
            f"<span class='badge'>{latest_new}</span>"
            "</div>"
            "<div class='mobile-metrics'>"
            "<div class='mobile-metric'>"
            "<p class='mobile-metric-label'>Unique Added (Day)</p>"
            f"<p class='mobile-metric-value'>{day_total_new}</p>"
            "</div>"
            "<div class='mobile-metric'>"
            "<p class='mobile-metric-label'>Added (Latest)</p>"
            f"<p class='mobile-metric-value'>{latest_new}</p>"
            "</div>"
            "</div>"
            "</article>"
        )

    rows_html = "".join(rows) if rows else "<tr><td colspan='4'>No data yet.</td></tr>"
    mobile_html = "".join(mobile_items) if mobile_items else "<p class='prose-muted'>No data yet.</p>"

    return f"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>URL Crawl Report</title>
  <style>{_base_styles()}</style>
</head>
<body>
  <main class='container stack'>
    <header class='card card-pad prose'>
      <h1>URL Crawl Report</h1>
      <p class='prose-muted'>Generated at: {html.escape(date.today().isoformat())}</p>
    </header>

    <section class='metrics'>
      <article class='metric'><p class='metric-label'>Days</p><p class='metric-value'>{len(days)}</p></article>
      <article class='metric'><p class='metric-label'>Unique Added (All Days)</p><p class='metric-value'>{total_day_added}</p></article>
      <article class='metric'><p class='metric-label'>Added (Latest Run Sum)</p><p class='metric-value'>{total_latest_added}</p></article>
      <article class='metric'><p class='metric-label'>Data Source</p><p class='metric-value'>data/daily</p></article>
    </section>

    <section class='card card-pad'>
      <div class='table-wrap'>
        <table>
          <thead>
            <tr><th>Date</th><th>Latest Run</th><th>Unique Added (Day)</th><th>Added (Latest Run)</th></tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
      <div class='mobile-list'>
        {mobile_html}
      </div>
    </section>
  </main>
</body>
</html>
"""


def build_report() -> tuple[Path, list[Path]]:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DAILY_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all day files sorted oldest-first for cross-day dedup
    all_files = sorted(DAILY_DIR.glob("*.json"))  # ascending date order
    all_day_data: list[tuple[Path, dict[str, Any]]] = []
    for day_file in all_files:
        all_day_data.append((day_file, _load_json(day_file)))

    # Build global_seen: for each day, record which URLs were shown on PRIOR days
    # We go oldest→newest, accumulate seen after each day's rendering
    global_seen: set = set()
    day_seen: dict[str, set] = {}  # day_str -> set of prior-seen URLs at that day
    for day_file, day_data in all_day_data:
        day_str = str(day_data.get("date", day_file.stem))
        day_seen[day_str] = set(global_seen)  # snapshot before this day
        # Add this day's unique URLs into global_seen for the next day
        for url in _collect_day_unique_urls(day_data):
            global_seen.add(url)

    daily_pages: list[Path] = []
    index_meta: list[dict[str, Any]] = []

    # Render in reverse-chronological order for index display, but use per-day seen sets
    for day_file, day_data in reversed(all_day_data):
        day = str(day_data.get("date", day_file.stem))
        runs = day_data.get("runs", [])
        latest = runs[-1] if runs else {}
        latest_run_at = str(latest.get("run_at", ""))

        seen_for_day = day_seen.get(day, set())
        deduped_urls = _collect_day_unique_urls(day_data, seen=seen_for_day)
        day_total_new = len(deduped_urls)

        # Latest run new count (deduplicated)
        latest_new = 0
        for page in latest.get("pages", []):
            raw = page.get("new_urls", [])
            latest_new += sum(1 for u in raw if isinstance(u, str) and u not in seen_for_day)

        index_meta.append(
            {
                "date": day,
                "latest_run_at": latest_run_at,
                "day_total_new": day_total_new,
                "latest_new": latest_new,
            }
        )

        daily_html = _render_day_page(day_data, day_file, seen=seen_for_day)
        daily_out = PUBLIC_DAILY_DIR / f"{day}.html"
        daily_out.write_text(daily_html, encoding="utf-8")
        daily_pages.append(daily_out)

    index_html = _render_index(index_meta)
    index_out = PUBLIC_DIR / "index.html"
    index_out.write_text(index_html, encoding="utf-8")
    return index_out, daily_pages


def main() -> int:
    index_out, daily_pages = build_report()
    print(f"report generated: {index_out}")
    print(f"daily pages: {len(daily_pages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
