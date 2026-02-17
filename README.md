# html-url-crawl

按页面抓取 `<a href>` URL，**仅保留外链**（与页面域名不同），支持基线对比并把“新增 URL”按运行日期追加写入 JSON。

## 推荐方式（Makefile + 虚拟环境）

安装依赖

```bash
make install
```

初始化基线：

```bash
make init
```

检测新增外链 URL（写入当日文件）：

```bash
make check
```

检测并更新基线：

```bash
make check-update
```

运行测试：

```bash
make test
```

清理虚拟环境和缓存：

```bash
make clean
```

## 手动方式（不使用 Makefile）

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py init
python main.py check
```

## 配置

编辑 `config.json`，格式如下：

```json
{
  "source_urls": [
    "https://example.com/page-1",
    "https://example.com/page-2"
  ]
}
```

你也可以复制 `config.example.json` 作为模板。

## 输出文件

- 基线：`data/baseline.json`
- 每日新增：`data/daily/YYYY-MM-DD.json`

同一天执行多次 `check` 会在同一文件的 `runs` 数组追加记录。
