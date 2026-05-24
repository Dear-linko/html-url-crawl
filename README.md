# html-url-crawl

抓取配置页面中的 `<a href>`，仅保留外链（域名与页面不同），支持增量检测，并可生成静态报表 + Telegram 通知。

## 快速开始

```bash
make install
make init
make check
```

## 配置

主配置文件：`config.json`

```json
{
  "source_urls": [
    "https://example.com/page-1",
    "https://example.com/page-2"
  ]
}
```

模板：`config.example.json`

通知配置文件：`.env`（可由 `.env.example` 复制）

```bash
cp .env.example .env
```

`.env` 字段：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `REPORT_BASE_URL`（GitHub Pages 地址，例如 `https://dear-linko.github.io/html-url-crawl`）

## 常用命令

```bash
make install          # 创建 .venv 并安装依赖
make init             # 初始化 baseline
make check            # 增量检测并写入 data/daily/YYYY-MM-DD.json
make check-update     # 检测后更新 baseline
make report           # 生成静态报表到 public/
make notify           # 检查最新 run 并按需发送 Telegram
make run-and-notify   # check -> report -> notify（用于定时任务）
make test             # 运行测试
```

## 输出文件

- 基线：`data/baseline.json`
- 每日增量：`data/daily/YYYY-MM-DD.json`
- 报表总览：`public/index.html`
- 报表详情：`public/daily/YYYY-MM-DD.html`

说明：同一天多次 `check` 会追加到同一 JSON 的 `runs` 数组。

## 定时运行（cron）

示例：每小时第 5 分钟执行一次

```cron
5 * * * * cd /path/to/html-url-crawl && /bin/bash scripts/run_and_notify.sh
```

## 报表发布（GitHub Pages）

报表通过本仓库的 `gh-pages` 分支发布，无需独立的 reports 仓库。

`sync-reports.sh` 会：

1. 运行 `render_report.py` 生成 `public/`；
2. 在 `.gh-pages/`（git worktree）检出 `gh-pages` 分支；
3. 复制 `index.html`、`daily/*.html`，提交并推送到 `gh-pages`。

首次需在 GitHub 仓库的 **Settings → Pages** 中把发布源设为 `gh-pages` 分支根目录，
站点地址即 `https://dear-linko.github.io/html-url-crawl`（同 `REPORT_BASE_URL`）。

可选环境变量：`PAGES_BRANCH`、`WORKTREE_DIR`、`GH_BIN`（`gh` 可执行文件路径，用于
headless/cron 下获取 token）。
