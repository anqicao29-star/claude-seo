---
name: seo-firecrawl
description: >
  通过 Firecrawl MCP 实现全站爬取（full-site crawling）、抓取（scraping）与站点
  地图绘制（site mapping）。当用户说"爬取网站"、"crawl site"、"绘制站点地图"、
  "map site"、"全站爬取"、"full crawl"、"查找所有页面"、"find all pages"、
  "死链"、"broken links"、"网站结构"、"site structure"、"发现页面"、
  "discover pages"、"JS 渲染"、"JS rendering"，或需要进行全站分析时使用本技能。
user-invocable: true
argument-hint: "[command] <url>"
license: MIT
compatibility: "Requires Firecrawl MCP server"
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# Claude SEO 的 Firecrawl 扩展

本技能需要预先安装 Firecrawl 扩展：
```bash
./extensions/firecrawl/install.sh
```

**检查可用性：** 在使用任何 Firecrawl 工具之前，先确认 MCP 服务器已连接——
检查 `firecrawl_scrape` 或其他任意 Firecrawl 工具是否可用。如果工具不可用，
告知用户该扩展尚未安装，并提供安装说明。

## 速查表

| 命令 | 用途 |
|---------|---------|
| `/seo firecrawl crawl <url>` | 全站爬取，含内容提取 |
| `/seo firecrawl map <url>` | 发现站点结构（仅 URL，速度快） |
| `/seo firecrawl scrape <url>` | 单页抓取，支持 JS 渲染 |
| `/seo firecrawl search <query> <url>` | 在已爬取站点内进行搜索 |

## 命令详解

### crawl —— 全站爬取

从给定 URL 开始爬取整个网站，返回所有被发现页面的页面内容、元数据及链接。

**MCP 工具：** `firecrawl_crawl`

**参数：**
- `url`（必填）：起始爬取 URL
- `limit`：最大爬取页数（默认 100，最大 500）
- `maxDepth`：距起始 URL 的最大链接深度（默认 3）
- `includePaths`：需纳入的 glob 模式数组（如 `["/blog/*"]`）
- `excludePaths`：需排除的 glob 模式数组（如 `["/admin/*", "/api/*"]`）
- `scrapeOptions.formats`：输出格式 —— `["markdown", "html", "links"]`

**SEO 使用场景：**
1. **全面审计爬取**：爬取全站，提取全部页面供子 agent 分析
2. **分区爬取**：使用 `includePaths` 只审计 `/blog/*` 或 `/products/*`
3. **死链检测**：以 `["links"]` 格式爬取，检查所有链接是否 404
4. **内容清单**：批量提取全部页面的 title、meta description、H1
5. **SPA/JS 渲染站点**：Firecrawl 会执行 JavaScript 渲染，解决 Issue #11 提到的问题

**`/seo audit` 的编排示例：**
```
1. firecrawl_map(url) -> get all URLs (fast, no content)
2. Filter to top 50 most important pages (homepage, key sections)
3. firecrawl_crawl(url, limit=50) -> get full content
4. Feed content to seo-technical, seo-content, seo-schema agents
```

**成本提示：**
- 免费额度：每月 500 credits
- 1 credit = 抓取或爬取 1 个页面
- Map 操作更省额度（每发现 1 个 URL 消耗 0.5 credit）
- 大规模爬取前，务必提前告知用户预计消耗的额度

### map —— 站点结构发现

在不抓取内容的情况下发现网站上的所有 URL，速度快、省额度。

**MCP 工具：** `firecrawl_map`

**参数：**
- `url`（必填）：待映射的网站 URL
- `limit`：最大发现 URL 数（默认 5000）
- `search`：可选的搜索关键词，用于过滤 URL

**SEO 使用场景：**
1. **Sitemap 对比**：绘制站点地图后，与 XML sitemap 中的 URL 进行比对
2. **孤立页面检测**：出现在 sitemap 中但没有任何页面链接指向的 URL
3. **爬取预算分析**：可索引页面总数 vs. 首页可直接链接到的页面数
4. **URL 模式分析**：识别 URL 结构规律、重复项、参数膨胀问题
5. **审计前的预发现**：先运行 map，再对关键板块做针对性爬取

**输出：** URL 数组，展示形式如下：
```
Site: example.com
Pages discovered: 342

URL Pattern Breakdown:
  /blog/*          - 128 pages (37%)
  /products/*      - 89 pages (26%)
  /category/*      - 45 pages (13%)
  /pages/*         - 32 pages (9%)
  / (root pages)   - 48 pages (14%)
```

### scrape —— 单页深度抓取

对单个页面进行完整 JavaScript 渲染后再抓取，比 `fetch_page.py` 更彻底，
因为它会执行 JS 并等待动态内容加载完成。

**MCP 工具：** `firecrawl_scrape`

**参数：**
- `url`（必填）：待抓取的页面 URL
- `formats`：输出格式 —— `["markdown", "html", "links", "screenshot"]`
- `onlyMainContent`：是否去除导航栏/页脚/侧边栏（默认 true）
- `waitFor`：CSS 选择器或等待内容加载的毫秒数
- `timeout`：请求超时时间，单位毫秒（默认 30000）
- `actions`：抓取前执行的浏览器操作（点击、滚动、等待）

**SEO 使用场景：**
1. **SPA 内容提取**：抓取 JS 渲染的 React/Vue/Angular 页面
2. **动态内容审计**：折叠内容中存在懒加载（lazy-loaded）的页面
3. **付费墙/登录墙检测**：识别位于登录验证之后的内容
4. **主体内容提取**：使用 `onlyMainContent` 获取干净内容用于 E-E-A-T 分析
5. **截图采集**：使用 `screenshot` 格式进行视觉分析

**何时用 scrape，何时用 fetch_page.py：**
| 场景 | 使用工具 |
|----------|-----|
| 静态 HTML 页面 | `fetch_page.py`（无 API 成本） |
| JS 渲染的 SPA | `firecrawl_scrape`（可执行 JS 渲染） |
| 需要响应头信息 | `fetch_page.py`（返回响应头） |
| 需要干净的 markdown | `firecrawl_scrape`（提取效果更好） |
| 被限流/屏蔽 | `firecrawl_scrape`（可处理反爬机制） |

### search —— 站内定向搜索

在网站内搜索特定内容，无需爬取整站即可找到与某个主题相关的页面。

**MCP 工具：** `firecrawl_search`

**参数：**
- `query`（必填）：搜索关键词
- `url`（必填）：待搜索的网站
- `limit`：最大结果数（默认 10）
- `scrapeOptions.formats`：匹配页面的输出格式

**SEO 使用场景：**
1. **内容缺口验证**：搜索某关键词，检查站内是否已有相关内容
2. **内链机会挖掘**：找到提及某主题、可互相链接的页面
3. **重复内容检测**：搜索关键短语，找出近似重复页面
4. **竞品内容调研**：在竞品站点内搜索特定主题

## 跨技能协同

### 与 seo-audit（全站审计）配合
在 `/seo audit` 过程中，如 Firecrawl 可用：
1. 用 `firecrawl_map` 发现全站 URL
2. 与 XML sitemap（seo-sitemap）比对，找出孤立/缺失页面
3. 挑选重点页面做深度分析
4. 将爬取内容提供给全部子 agent（technical、content、schema、geo）
5. 报告可爬取页面总数、URL 模式与爬取深度

### 与 seo-technical 配合
- 死链检测：爬取所有内部链接，检查是否 404
- 重定向链映射：追踪所有重定向，标记超过 2 跳的跳转链
- 混合内容检测：检查 HTTPS 页面上是否引用了 HTTP 资源
- Canonical 校验：对比 canonical URL 与实际 URL

### 与 seo-sitemap 配合
- Sitemap 覆盖率：已爬取页面中出现在 sitemap 里的比例
- 孤立页面：爬取发现但未出现在 sitemap 中的页面
- 过期 sitemap 条目：sitemap 中返回 404/410 的 URL

### 与 seo-content 配合
- 内容提取：将干净的 markdown 提供给 E-E-A-T 分析
- 内容单薄检测：批量识别少于 300 字的页面
- 重复内容：跨页面比对内容，找出近似重复项

### 与 seo-schema 配合
- 结构化数据提取：从所有已爬取页面中提取 JSON-LD
- 结构化数据覆盖率：含结构化数据的页面占比
- 结构化数据校验：批量校验提取到的结构化数据

## 错误处理

| 错误 | 原因 | 解决方法 |
|-------|-------|-----------|
| `FIRECRAWL_API_KEY not set` | MCP 未配置 | 运行 `./extensions/firecrawl/install.sh` |
| `402 Payment Required` | 额度已耗尽 | 前往 firecrawl.dev/app 查看用量，升级套餐 |
| `429 Too Many Requests` | 触发限流 | 等待 60 秒，降低爬取并发数 |
| `408 Timeout` | 页面渲染过慢 | 增加 `timeout`，或尝试关闭 JS 渲染 |
| `403 Forbidden` | 站点屏蔽爬取 | 检查 robots.txt，可能需要跳过该站点 |

**优雅降级：** 如果 Firecrawl 不可用，告知用户并建议：
1. 使用 `fetch_page.py` 做单页分析（无 API 成本）
2. 使用 `WebFetch` 工具做基础 HTML 抓取
3. 安装 Firecrawl：`./extensions/firecrawl/install.sh`
