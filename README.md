# html-url-crawl

抓取配置页面中的 `<a href>`，仅保留**外链**（主机名 hostname 与页面不同，不同子域视为外链），
支持增量检测，并可生成静态报表（GitHub Pages）+ Telegram 通知。

## 工作原理

```
config.json (source_urls)
        │
        ▼
  fetch → 提取 <a href> → 解析(支持 <base href>) → 规范化去重 → 过滤外链
        │
        ▼
  与 baseline 对比，得出"新增 URL"
        │
        ├─ data/daily/YYYY-MM-DD.json   每日增量（同一天多次 check 追加到 runs[]）
        ├─ public/                       渲染出的静态报表
        └─ Telegram                      可选通知
```

- **外链判定**：按主机名比较，`blog.example.com` 与 `www.example.com` 视为不同（都算外链）。
- **相对链接**：若页面声明了 `<base href>`，相对链接按 base 解析，否则按最终 URL 解析。
- **请求头**：抓取时发送描述性 User-Agent，降低被站点拦截的概率。

## 快速开始

```bash
make install     # 创建 .venv 并安装依赖
make init        # 抓取 source_urls，建立 baseline
make check       # 增量检测，写入 data/daily/YYYY-MM-DD.json
```

## 配置

### 主配置 `config.json`（可由 `config.example.json` 复制）

```json
{
  "source_urls": [
    "https://example.com/page-1",
    "https://example.com/page-2"
  ]
}
```

### 通知配置 `.env`（可由 `.env.example` 复制）

```bash
cp .env.example .env
```

| 字段 | 说明 |
|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人 token（留空则跳过通知） |
| `TELEGRAM_CHAT_ID`   | 接收通知的 user / group / channel id |
| `REPORT_BASE_URL`    | 报表公开地址，例如 `https://dear-linko.github.io/html-url-crawl` |

> 二者均为本地文件，已在 `.gitignore` 中忽略，不会提交。

## 常用命令

```bash
make install          # 创建 .venv 并安装依赖
make init             # 初始化 baseline
make check            # 增量检测并写入 data/daily/YYYY-MM-DD.json
make check-update     # 检测后更新 baseline（推荐用于定时任务）
make report           # 生成静态报表到 public/
make notify           # 检查最新 run 并按需发送 Telegram
make run-and-notify   # check-update -> report -> sync -> notify（定时任务一条龙）
make test             # 运行测试
```

> `make` 默认用 `PYTHON ?= /opt/homebrew/bin/python3.11`。其他环境可覆盖，例如
> `make install PYTHON=python3`。

## 输出文件

| 路径 | 内容 |
|------|------|
| `data/baseline.json`        | 基线（每个 source_url 的已知外链集合） |
| `data/daily/YYYY-MM-DD.json`| 每日增量；同一天多次 `check` 追加到 `runs[]` |
| `public/index.html`         | 报表总览（按日期汇总） |
| `public/daily/YYYY-MM-DD.html` | 单日详情；**顶部含当日去重后的新增 URL 列表** |

> `data/` 与 `public/` 均被 `.gitignore` 忽略——它们是运行时产物，不进版本库。
> 报表去重逻辑：单日详情会排除**前序日期**已出现过的 URL，使各天列表互不重复。

## 报表发布（GitHub Pages）

报表通过本仓库的 `gh-pages` 分支发布，无需独立的 reports 仓库。

**首次配置（只需一次）**：在 GitHub 仓库 **Settings → Pages** 把发布源设为
`gh-pages` 分支、根目录 `/`。站点地址即 `https://dear-linko.github.io/html-url-crawl`
（与 `REPORT_BASE_URL` 一致）。

**发布 / 更新页面**：

```bash
bash sync-reports.sh
```

该脚本会：

1. 运行 `render_report.py` 重新生成 `public/`；
2. 在 `.gh-pages/`（git worktree）检出 `gh-pages` 分支；
3. 复制 `index.html`、`daily/*.html`，提交并推送到 `gh-pages`。

> ⚠️ **改了渲染模板或升级了代码后，页面不会自动更新**——已发布的是静态 HTML。
> 需重新跑 `bash sync-reports.sh` 重渲染并推送，GitHub Pages 再构建约 1 分钟后生效
> （浏览器记得强制刷新）。

可选环境变量：`PAGES_BRANCH`（默认 `gh-pages`）、`WORKTREE_DIR`（默认 `.gh-pages/`）、
`GH_BIN`（`gh` 可执行文件路径，用于 headless/cron 下获取 push token）。

## 定时运行（cron）

示例：每小时第 5 分钟执行一次完整流程（检测 → 渲染 → 发布 → 通知）：

```cron
5 * * * * cd /path/to/html-url-crawl && /bin/bash scripts/run_and_notify.sh
```

`scripts/run_and_notify.sh` 带文件锁（避免重叠运行），日志写入 `logs/run_and_notify.log`，
并会自动 `source .env`。

## 项目结构

```
main.py                    入口：init / check 子命令
crawler/
  fetcher.py               抓取（重试 + User-Agent）
  extractor.py             提取 <a href> 与 <base href>
  normalize.py             规范化、去重、外链过滤
  diff.py                  与 baseline 对比，计算新增 URL
  storage.py               配置读取 + 原子写 JSON
scripts/
  render_report.py         生成静态报表
  notify_telegram.py       Telegram 通知
  run_and_notify.sh        定时任务一条龙
sync-reports.sh            渲染并发布到 gh-pages
tests/                     pytest 测试
```

## 测试

```bash
make test          # 等价于 .venv/bin/python -m pytest -q
```
