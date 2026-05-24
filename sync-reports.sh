#!/bin/bash
# Sync html-url-crawl reports to the gh-pages branch of THIS repo (GitHub Pages source).
set -euo pipefail
shopt -s nullglob

CRAWL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAGES_BRANCH="${PAGES_BRANCH:-gh-pages}"
WORKTREE_DIR="${WORKTREE_DIR:-$CRAWL_DIR/.gh-pages}"
GH_BIN="${GH_BIN:-gh}"

push_with_retry() {
    local attempt=1
    local max_attempts=3
    local delay=30

    while true; do
        if git push "$@"; then
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

# Ensure a worktree checked out on the gh-pages branch.
if [ ! -d "$WORKTREE_DIR" ]; then
    git fetch origin "$PAGES_BRANCH" || true
    if git show-ref --verify --quiet "refs/remotes/origin/$PAGES_BRANCH"; then
        git worktree add -B "$PAGES_BRANCH" "$WORKTREE_DIR" "origin/$PAGES_BRANCH"
    else
        git worktree add -B "$PAGES_BRANCH" "$WORKTREE_DIR"
    fi
fi

cd "$WORKTREE_DIR"
git pull --ff-only origin "$PAGES_BRANCH" 2>/dev/null || true

# Copy rendered output into the gh-pages worktree.
cp -f "$CRAWL_DIR/public/index.html" ./
mkdir -p daily
daily_pages=("$CRAWL_DIR"/public/daily/*.html)
if [ "${#daily_pages[@]}" -gt 0 ]; then
    cp -f "${daily_pages[@]}" daily/
fi
touch .nojekyll

git add index.html daily/ .nojekyll
if git diff --cached --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] no report changes to commit"
    exit 0
fi
git commit -m "Auto-update: $(date +%Y-%m-%d)"

# Prefer the remote's configured credentials; fall back to an embedded token
# (via gh) for headless/cron environments without a credential helper.
GH_TOKEN="$("$GH_BIN" auth token 2>/dev/null || true)"
if [ -n "$GH_TOKEN" ]; then
    PUSH_URL="https://x-access-token:${GH_TOKEN}@github.com/Dear-linko/html-url-crawl.git"
    push_with_retry "$PUSH_URL" "HEAD:$PAGES_BRANCH"
else
    push_with_retry origin "HEAD:$PAGES_BRANCH"
fi
