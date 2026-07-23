---
name: seo-google
description: >
  Google SEO 相关 API 集成：Search Console（搜索控制台，含搜索分析、URL 检查、
  站点地图）、PageSpeed Insights v5、带 25 周历史数据的 CrUX 现场数据、
  Indexing API v3，以及 GA4 自然流量数据。为 Core Web Vitals、索引状态、
  搜索表现和自然流量趋势提供真实的 Google 现场数据（field data）。Use when
  user says "search console", "GSC", "PageSpeed", "CrUX", "field data",
  "indexing API", "GA4 organic", "URL inspection", "google api setup",
  "real CWV data", "impressions", "clicks", "CTR", "position data",
  "LCP", "INP", "CLS", "FCP", "TTFB", or "Lighthouse scores".
user-invocable: true
argument-hint: "[command] [url|property]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# Google SEO API 集成

直接对接 Google 官方的 SEO 数据。填补了基于抓取的分析（现有 claude-seo 技能）与 Google 实时现场数据之间的空白：真实的 Chrome 用户指标、真实的索引状态、搜索表现和自然流量。

所有 API 均为免费。配置需要一个带有 API key 和/或服务账号的 Google Cloud 项目 -- 运行 `/seo google setup` 获取分步说明。

## 前置条件

执行任何命令前，先检查凭证：
```bash
python3 scripts/google_auth.py --check --json
```

配置文件：`~/.config/claude-seo/google-api.json`
```json
{
  "service_account_path": "/path/to/service_account.json",
  "api_key": "<GOOGLE_API_KEY>",
  "default_property": "sc-domain:example.com",
  "ga4_property_id": "properties/123456789"
}
```

如果配置文件不存在，阅读 `references/auth-setup.md` 并引导用户完成配置。

### 凭证等级

| 等级 | 检测方式 | 可用命令 |
|------|-----------|-------------------|
| **0**（API Key） | 存在 `api_key` | `pagespeed`, `crux`, `crux-history`, `youtube`, `nlp` |
| **1**（OAuth/服务账号） | 加上 OAuth token 或服务账号 | 等级 0 + `gsc`, `inspect`, `sitemaps`, `index` |
| **2**（完整） | 加上已配置 `ga4_property_id` | 等级 1 + `ga4`, `ga4-pages` |
| **3**（广告） | 加上 `ads_developer_token` + `ads_customer_id` | 等级 2 + `keywords`, `volume` |

运行命令前，始终先告知用户检测到的凭证等级。

## 快速参考

| 命令 | 作用 | 等级 |
|---------|-------------|------|
| `/seo google setup` | 检查/配置 API 凭证 | -- |
| `/seo google pagespeed <url>` | PSI Lighthouse + CrUX 现场数据 | 0 |
| `/seo google crux <url>` | 仅 CrUX 现场数据（p75 指标） | 0 |
| `/seo google crux-history <url>` | 25 周 CWV 趋势分析 | 0 |
| `/seo google gsc <property>` | Search Console：点击量、展现次数、点击率、排名 | 1 |
| `/seo google inspect <url>` | URL 检查：索引状态、canonical、抓取信息 | 1 |
| `/seo google inspect-batch <file>` | 从文件批量执行 URL 检查 | 1 |
| `/seo google sitemaps <property>` | GSC 站点地图状态 | 1 |
| `/seo google index <url>` | 向 Indexing API 提交 URL | 1 |
| `/seo google index-batch <file>` | 批量提交最多 200 个 URL | 1 |
| `/seo google ga4 [property-id]` | GA4 自然流量报告 | 2 |
| `/seo google ga4-pages [property-id]` | 自然流量落地页 Top 排行 | 2 |
| `/seo google youtube <query>` | YouTube 视频搜索（播放量、点赞数、时长） | 0 |
| `/seo google youtube-video <id>` | YouTube 视频详情 + 热门评论 | 0 |
| `/seo google nlp <url-or-text>` | NLP 实体提取 + 情感分析 + 内容分类 | 0 |
| `/seo google entities <url-or-text>` | 仅实体分析（用于 E-E-A-T） | 0 |
| `/seo google keywords <seed>` | 来自 Google Ads 关键词规划师的关键词创意 | 3 |
| `/seo google volume <keywords>` | 从关键词规划师查询搜索量 | 3 |
| `/seo google entity <query>` | Knowledge Graph 实体检测 | 0 |
| `/seo google safety <url>` | Web Risk URL 安全检测 | 0 |
| `/seo google quotas` | 显示所有 API 的速率限制 | -- |

---

## PageSpeed + CrUX

### `/seo google pagespeed <url>`

结合 Lighthouse 实验室数据与 CrUX 现场数据。

**脚本：** `python3 scripts/pagespeed_check.py <url> --json`
**参考文档：** `references/pagespeed-crux-api.md`
**默认设置：** 同时输出移动端 + 桌面端两种策略，包含所有 Lighthouse 类别。

输出会将实验室评分（某一时刻的 Lighthouse 快照）与现场数据（28 天 Chrome 用户指标）合并展示。CrUX 优先尝试 URL 级别数据，若不足则回退到 origin 级别。

### `/seo google crux <url>`

仅返回 CrUX 现场数据（不运行 Lighthouse），速度更快。

**脚本：** `python3 scripts/pagespeed_check.py <url> --crux-only --json`

### `/seo google crux-history <url>`

25 周 CrUX History 趋势。展示 CWV 指标是在改善、持平还是恶化。

**脚本：** `python3 scripts/crux_history.py <url> --json`
**参考文档：** `references/pagespeed-crux-api.md`

输出包含每项指标的趋势方向、变化百分比以及每周的 p75 数值。

---

## Search Console

### `/seo google gsc <property>`

搜索分析（Search Analytics）：过去 28 天的点击量、展现次数、点击率（CTR）、排名。

**脚本：** `python3 scripts/gsc_query.py --property <property> --json`
**参考文档：** `references/search-console-api.md`
**默认设置：** 28 天，维度为 query,page，类型为 web，条数上限 1000。

内置快速增长机会检测：找出排名在 4-10 名、展现次数较高的查询词。

### `/seo google inspect <url>`

URL 检查：来自 Google 的真实索引状态。

**脚本：** `python3 scripts/gsc_inspect.py <url> --json`

返回内容包括：结论（PASS/FAIL）、覆盖状态、robots.txt 状态、索引状态、页面抓取状态、canonical 选择结果、移动端可用性、富媒体结果（rich results）。

### `/seo google inspect-batch <file>`

从文件批量检测（每行一个 URL）。速率限制为每个站点每天 2000 次。

**脚本：** `python3 scripts/gsc_inspect.py --batch <file> --json`

### `/seo google sitemaps <property>`

列出已提交的站点地图及其状态、错误和警告。站点地图内容报告只反映提交的数量；具体 URL 是否被索引，以 URL 检查 API 的结果为准。

**脚本：** `python3 scripts/gsc_query.py sitemaps --property <property> --json`

---

## Indexing API

### `/seo google index <url>`

通知 Google 某个 URL 已更新。

**脚本：** `python3 scripts/indexing_notify.py <url> --json`
**参考文档：** `references/indexing-api.md`

Indexing API 官方仅适用于 JobPosting 和 BroadcastEvent/VideoObject 类型的页面。务必向用户说明这一限制。每日配额：200 次提交请求。

### `/seo google index-batch <file>`

从文件批量提交 URL，并跟踪配额使用情况。

**脚本：** `python3 scripts/indexing_notify.py --batch <file> --json`

---

## GA4 流量

### `/seo google ga4 [property-id]`

自然流量报告：每日会话数、用户数、页面浏览量、跳出率、互动指标。

**脚本：** `python3 scripts/ga4_report.py --property <id> --json`
**参考文档：** `references/ga4-data-api.md`
**默认设置：** 28 天，仅筛选 Organic Search 渠道分组。

### `/seo google ga4-pages [property-id]`

按会话数排序的自然流量落地页 Top 排行。

**脚本：** `python3 scripts/ga4_report.py --property <id> --report top-pages --json`

---

## YouTube（视频 SEO）

YouTube 提及与 AI 可见度的相关性最强（相关系数 0.737）。免费，仅需 API key。

### `/seo google youtube <query>`

在 YouTube 上搜索视频，返回标题、频道、播放量、点赞数、时长。

**脚本：** `python3 scripts/youtube_search.py search "<query>" --json`
**参考文档：** `references/youtube-api.md`
**配额：** 每次搜索消耗 100 单位（每天免费额度 10,000 单位）。

### `/seo google youtube-video <video_id>`

视频详细信息 + 标签 + 热门 10 条评论。

**脚本：** `python3 scripts/youtube_search.py video <video_id> --json`
**配额：** 2 单位（视频详情 + 评论）。

---

## NLP 内容分析

Google 自家的实体/情感分析能力，可增强 E-E-A-T 评分。

### `/seo google nlp <url-or-text>`

完整 NLP 分析：实体、情感、内容分类。

**脚本：** `python3 scripts/nlp_analyze.py --url <url> --json` 或 `--text "..."`
**参考文档：** `references/nlp-api.md`
**免费额度：** 每月 5,000 单位。需在 GCP 项目中启用结算。

### `/seo google entities <url-or-text>`

仅提取实体（更快，消耗配额更少）。

**脚本：** `python3 scripts/nlp_analyze.py --url <url> --features entities --json`

---

## 关键词研究（Google Ads）

黄金标准的关键词搜索量数据，需要 Google Ads 账号。

### `/seo google keywords <seed>`

基于种子词生成关键词创意。

**脚本：** `python3 scripts/keyword_planner.py ideas "<seed>" --json`
**参考文档：** `references/keyword-planner-api.md`
**要求：** 配置中需有 Ads developer token + customer ID（等级 3）。

### `/seo google volume <keywords>`

查询指定关键词（逗号分隔）的搜索量。

**脚本：** `python3 scripts/keyword_planner.py volume "<kw1>,<kw2>" --json`

---

## 补充功能

### `/seo google entity <query>`

Knowledge Graph 实体检测，验证品牌的知识图谱收录情况。

**参考文档：** `references/supplementary-apis.md`
使用 API key 调用 Knowledge Graph Search API。

### `/seo google safety <url>`

Web Risk API 检测，识别恶意软件/社交工程风险标记。

**参考文档：** `references/supplementary-apis.md`

### `/seo google quotas`

展示速率限制表。阅读 `references/rate-limits-quotas.md`。

---

## 报告

在任意分析命令执行完成后，主动提示是否生成 PDF/HTML 报告。

### `/seo google report <type>`

生成带图表和数据分析的专业 PDF 报告。

**脚本：** `python3 scripts/google_report.py --type <type> --data <json> --domain <domain> --format pdf`

| 类型 | 输入 | 输出 |
|------|-------|--------|
| `cwv-audit` | PSI + CrUX + CrUX History 数据 | 包含仪表盘、时间线、分布图的 Core Web Vitals 审计报告 |
| `gsc-performance` | GSC 查询数据 | 含查询词表格、快速增长机会的 Search Console 报告 |
| `indexation` | 批量检测数据 | 带覆盖率环形图的索引状态报告 |
| `full` | 所有数据汇总 | 完整的 Google SEO 综合报告（全部章节） |

**工作流程：**
1. 运行数据采集命令（pagespeed、gsc、inspect-batch 等）
2. 将 JSON 输出保存到文件：`python3 scripts/pagespeed_check.py <url> --json > data.json`
3. 生成报告：`python3 scripts/google_report.py --type cwv-audit --data data.json --domain <domain>`

**约定：** 分析完成后，建议用户："生成一份报告？使用 `/seo google report <type>`"

---

## 速率限制

| API | 每分钟 | 每天 | 认证方式 |
|-----|-----------|---------|------|
| PSI v5 | 240 QPM | 25,000 QPD | API Key |
| CrUX + History | 150 QPM（共享） | 无限制 | API Key |
| GSC Search Analytics | 每站点 1,200 QPM | 30M QPD | 服务账号 |
| GSC URL Inspection | 600 QPM | 每站点每天 2,000 次 | 服务账号 |
| Indexing API | 380 RPM | 每天 200 次提交 | 服务账号 |
| GA4 Data API | 10 并发 | 每天约 25K tokens | 服务账号 |

## 跨技能协同

- **seo-audit**：为获取实时 CWV + 索引数据而调用 `seo-google` agent（按条件触发）
- **seo-technical**：使用 pagespeed_check.py 获取真实 CWV 现场数据
- **seo-performance**：CrUX 现场数据可补充 Lighthouse 实验室数据
- **seo-sitemap**：GSC 站点地图状态仅展示提交数量、错误和警告；索引真相需以 URL Inspection 为准
- **seo-content**：GSC 查询数据可用于指导关键词选题
- **seo-geo**：GSC 搜索外观数据包含 AI Overview 引用信息

## 输出格式

- CWV 指标：采用交通灯式评级（良好 / 待改进 / 较差）
- 表现类报告：使用可排序列的表格
- 始终标注数据的新鲜度说明
- 报告保存为 `GOOGLE-API-REPORT-{domain}.md`
- 使用 `assets/templates/` 中的模板输出结构化内容

## 技术说明

- INP 已于 2024 年 3 月 12 日取代 FID，请勿再引用 FID。
- CrUX 返回的 CLS 数值为字符串编码（如 "0.05"），脚本已处理解析逻辑。
- CrUX 返回 404 表示流量不足，并非认证错误。
- Search Analytics 数据存在 2-3 天的延迟。
- CrUX 中 `round_trip_time` 已取代 `effectiveConnectionType`（2025 年 2 月）。
- Custom Search JSON API 已于 2025 年停止面向新客户开放。

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| 未配置任何凭证 | 运行 `/seo google setup`。列出仅需 API key 即可使用的等级 0 命令。 |
| 服务账号缺少 GSC 访问权限 | 报告错误。指导用户将 `client_email` 添加到 GSC > 设置 > 用户 > 添加。 |
| CrUX 数据不可用（404） | 报告 Chrome 流量不足。建议以 PSI 实验室数据作为备选方案。 |
| GA4 媒体资源未找到 | 报告错误。展示如何在 GA4 管理后台 > 媒体资源详情 中找到 property ID。 |
| Indexing API 配额超限 | 报告每日 200 次的限制。建议优先提交最重要的 URL。 |
| 触发速率限制（429） | 等待后按指数退避重试。报告是哪个 API 触发了限制。 |
</content>
