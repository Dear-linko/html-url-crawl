#!/bin/bash
# Sync html-url-crawl reports to public GitHub Pages
set -euo pipefail
shopt -s nullglob

REPO_DIR="$HOME/Projects/html-url-crawl-reports"
CRAWL_DIR="$HOME/Projects/html-url-crawl"

push_with_retry() {
    local attempt=1
    local max_attempts=3
    local delay=30

    while true; do
        if git push "$PUSH_URL" main; then
            return 0
        fi

        if [ "$attempt" -ge "$max_attempts" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] [error] git push failed after ${max_attempts} attempts"
            return 1
        fi

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [warn] git push failed, retrying in ${delay}s (attempt ${attempt}/${max_attempts})"
        sleep "$delay"
        attempt=$((attempt + 1))
        delay=$((delay * 2))
    done
}

cd "$CRAWL_DIR" || exit 1

# Rebuild report (in case new daily data exists)
.venv/bin/python scripts/render_report.py

# Copy to reports repo
cp -f public/index.html "$REPO_DIR/"
daily_pages=(public/daily/*.html)
if [ "${#daily_pages[@]}" -gt 0 ]; then
    cp -f "${daily_pages[@]}" "$REPO_DIR/daily/"
fi

# Commit and push (embed token in URL for cron/headless compatibility)
cd "$REPO_DIR"
GH_TOKEN=$(GH_CONFIG_DIR=~/.config/gh-file /Users/liike/.local/bin/gh auth token 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
    echo "[error] Failed to get GitHub token"
    exit 1
fi
PUSH_URL="https://Dear-linko:${GH_TOKEN}@github.com/Dear-linko/html-url-crawl-reports.git"
git add daily/ index.html
if ! git diff --cached --quiet; then
    git commit -m "Auto-update: $(date +%Y-%m-%d)"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] no report changes to commit"
fi
push_with_retry
