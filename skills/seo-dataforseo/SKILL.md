---
name: seo-dataforseo
description: >
  通过 DataForSEO MCP 服务获取实时 SEO 数据。涵盖 SERP 分析（Google、Bing、Yahoo、
  YouTube、Google Images）、关键词研究（搜索量、难度、意图、趋势）、外链画像、
  页面分析（Lighthouse、内容解析）、竞品分析、内容分析、商家信息，以及 AI 可见度
  （ChatGPT 抓取器、LLM 提及追踪）和域名数据分析。需要先安装 DataForSEO 扩展。
  当用户说"dataforseo"、"实时 SERP"、"live SERP"、"关键词搜索量"、
  "keyword volume"、"外链数据"、"backlink data"、"竞品数据"、"competitor data"、
  "AI 可见度检查"、"AI visibility check"、"LLM 提及"、"LLM mentions"、
  "图片 SERP"、"image SERP"、"google images"、"图片排名"、"image rankings"，或
  "真实搜索数据"、"real search data" 时使用本技能。
user-invocable: true
argument-hint: "[command] [query]"
license: MIT
compatibility: "Requires DataForSEO MCP server"
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# DataForSEO：实时 SEO 数据（扩展）

通过 DataForSEO MCP 服务获取实时搜索数据。提供实时的 SERP 结果
（自然排名 + 图片）、关键词指标、外链画像、页面分析、内容
分析、商家信息、AI 可见度检查以及 LLM 提及追踪，覆盖 10 个 API 模块、
79+ 个 MCP 工具。

## 前置条件

使用本技能前需先安装 DataForSEO 扩展：
```bash
./extensions/dataforseo/install.sh
```

**检查可用性：**在使用任何 DataForSEO 工具前，先确认 MCP 服务是否已连接——
检查 `serp_organic_live_advanced` 或任意 DataForSEO 工具是否可用。若工具不可用，
应告知用户该扩展尚未安装，并提供安装说明。

## API 用量意识

DataForSEO 按 API 调用计费，务必注意节省成本：
- 优先使用批量端点，而非多次单独调用
- 除非用户另有指定，否则使用默认参数（美国、英语）
- 在同一会话内于脑中缓存已获取的结果，避免重复拉取同一数据
- 在执行高开销操作（完整外链爬取、大批量关键词列表）前先提醒用户

## 成本护栏

**每次调用 DataForSEO MCP 前**，先运行成本预估：
```
python3 scripts/dataforseo_costs.py check <endpoint> [--count N]
```

- 若 `"status": "approved"` → 直接执行 API 调用
- 若 `"status": "needs_approval"` → 向用户展示成本预估，征得确认后再执行
- 若 `"status": "blocked"` → 告知用户已超出每日预算上限，不得继续执行

**每次 API 调用完成后**，记录成本：
```
python3 scripts/dataforseo_costs.py log <endpoint> <actual_cost>
```

**用户可用的成本管理命令：**
- `/seo dataforseo costs today` → 查看今日消费明细
- `/seo dataforseo costs summary` → 查看近 7 天的消费历史
- `/seo dataforseo costs config --mode threshold --threshold 0.50` → 配置审批模式

加载 `references/cost-tiers.md` 可获取完整的定价表、预算预设方案和降本技巧。

## 快速参考

| 命令 | 功能 |
|---------|-------------|
| `/seo dataforseo serp <keyword>` | Google 自然搜索 SERP 结果 |
| `/seo dataforseo serp-images <keyword>` | Google Images SERP 结果 |
| `/seo dataforseo serp-youtube <keyword>` | YouTube 搜索结果 |
| `/seo dataforseo youtube <video_id>` | YouTube 视频深度分析 |
| `/seo dataforseo keywords <seed>` | 关键词创意与建议 |
| `/seo dataforseo volume <keywords>` | 关键词搜索量 |
| `/seo dataforseo difficulty <keywords>` | 关键词难度评分 |
| `/seo dataforseo intent <keywords>` | 搜索意图分类 |
| `/seo dataforseo trends <keyword>` | Google Trends 趋势数据 |
| `/seo dataforseo backlinks <domain>` | 完整外链画像 |
| `/seo dataforseo competitors <domain>` | 竞品域名分析 |
| `/seo dataforseo ranked <domain>` | 域名的排名关键词列表 |
| `/seo dataforseo intersection <domains>` | 关键词/外链重叠分析 |
| `/seo dataforseo traffic <domains>` | 批量流量估算 |
| `/seo dataforseo subdomains <domain>` | 子域名及其排名数据 |
| `/seo dataforseo top-searches <domain>` | 提及该域名的热门搜索词 |
| `/seo dataforseo onpage <url>` | 页面分析（Lighthouse + 解析） |
| `/seo dataforseo tech <domain>` | 技术栈检测 |
| `/seo dataforseo whois <domain>` | WHOIS 注册信息 |
| `/seo dataforseo content <keyword/url>` | 内容分析与趋势 |
| `/seo dataforseo listings <keyword>` | 商家信息搜索 |
| `/seo dataforseo ai-scrape <query>` | 面向 GEO 的 ChatGPT 网页抓取 |
| `/seo dataforseo ai-mentions <keyword>` | 面向 GEO 的 LLM 提及追踪 |

---

## SERP 分析

### `/seo dataforseo serp <keyword>`

获取实时 Google 自然搜索结果。

**MCP 工具：** `serp_organic_live_advanced`

**默认参数：**location_code=2840（美国），language_code=en，device=desktop，depth=100

**同时支持：**`serp_organic_live_advanced` 工具通过 `se` 参数支持 Google、Bing、Yahoo。指定 "bing" 或 "yahoo" 即可切换搜索引擎。

**输出：**排名、URL、标题、描述、域名、精选摘要、AI 概览引用、People Also Ask。

### `/seo dataforseo serp-youtube <keyword>`

获取 YouTube 搜索结果。对 GEO 很有价值——YouTube 提及与 AI 引用的相关性最强。

**MCP 工具：** `serp_youtube_organic_live_advanced`

**输出：**视频标题、频道、播放量、发布日期、描述、URL。

### `/seo dataforseo youtube <video_id>`

对指定 YouTube 视频的深度分析：信息、评论、字幕。YouTube 提及与 AI 可见度的相关性最强（0.737），是 GEO 分析中的关键信号。

**MCP 工具：** `serp_youtube_video_info_live_advanced`、`serp_youtube_video_comments_live_advanced`、`serp_youtube_video_subtitles_live_advanced`

**参数：**video_id（YouTube 视频 ID，例如 "dQw4w9WgXcQ"）

**输出：**视频元数据（标题、频道、播放量、点赞数、描述）、高互动评论、字幕/文字稿。

### `/seo dataforseo serp-images <keyword>`

获取实时 Google Images 搜索结果。查看哪些图片针对该关键词排名靠前、
哪些域名主导图片结果，识别视觉内容的机会点。

**MCP 工具：** `serp_google_images_live_advanced`

**默认参数：**location_code=2840（美国），language_code=en，device=desktop，depth=100

**参数：**keyword（必填）、depth（可选，最大 700，按每 100 条结果为一个计费单位）、search_param（可选，例如 "site:example.com"）

**成本提示：**使用 `site:` 或 `filetype:` 操作符会产生 **5 倍 API 成本**。执行带筛选条件的查询前应提醒用户。

**输出：**排名位置、标题、alt text、来源页面 URL、图片直链 URL、域名、编码后的 URL。

**应提供的分析：**
- 域名占位统计：哪些站点占据了最多的图片位置（按数量取前 10 个域名）
- Alt text 规律：排名靠前图片中常见的标题/alt text 写法
- 格式分布：排名靠前的结果中 WebP、JPEG、PNG 的占比（从 image_url 后缀推断）
- 机会识别：用户已有自然排名但没有图片曝光的关键词

---

## 关键词研究

### `/seo dataforseo keywords <seed>`

基于种子关键词生成关键词创意、建议和相关词。

**MCP 工具：** `dataforseo_labs_google_keyword_ideas`、`dataforseo_labs_google_keyword_suggestions`、`dataforseo_labs_google_related_keywords`

**默认参数：**location_code=2840（美国），language_code=en，limit=50

**输出：**关键词、搜索量、CPC、竞争程度、关键词难度、趋势。

### `/seo dataforseo volume <keywords>`

获取一批关键词的搜索量和相关指标。

**MCP 工具：** `kw_data_google_ads_search_volume`

**参数：**keywords（数组，逗号分隔）、location_code、language_code

**输出：**关键词、月搜索量、CPC、竞争度、月度趋势数据。

### `/seo dataforseo difficulty <keywords>`

计算关键词的排名难度评分。

**MCP 工具：** `dataforseo_labs_bulk_keyword_difficulty`

**参数：**keywords（数组）、location_code、language_code

**输出：**关键词、难度评分（0-100）、难度解读（简单/中等/困难/极难）。

### `/seo dataforseo intent <keywords>`

按用户搜索意图对关键词分类。

**MCP 工具：** `dataforseo_labs_search_intent`

**参数：**keywords（数组）、location_code、language_code

**输出：**关键词、意图类型（信息型、导航型、商业型、交易型）、置信度评分。

### `/seo dataforseo trends <keyword>`

使用 Google Trends 数据分析关键词的时间趋势。

**MCP 工具：** `kw_data_google_trends_explore`

**参数：**keywords（数组）、location_code、date_from、date_to、language_code

**输出：**关键词、时间序列数据、趋势方向、季节性信号。

---

## 域名与竞品分析

### `/seo dataforseo backlinks <domain>`

全面的外链画像分析。

**MCP 工具：** `backlinks_summary`、`backlinks_backlinks`、`backlinks_anchors`、`backlinks_referring_domains`、`backlinks_bulk_spam_score`、`backlinks_timeseries_summary`

**默认参数：**每次子调用 limit=100

**输出：**外链总数、引荐域名数、域名权重、垃圾分数、主要锚文本、新增/流失外链的时间趋势、dofollow 比例、主要引荐域名。

### `/seo dataforseo competitors <domain>`

识别竞品域名并估算其流量。

**MCP 工具：** `dataforseo_labs_google_competitors_domain`、`dataforseo_labs_google_domain_rank_overview`、`dataforseo_labs_bulk_traffic_estimation`

**输出：**竞品域名、关键词重叠率、预估流量、域名权重、共同关键词。

### `/seo dataforseo ranked <domain>`

列出某域名的排名关键词，包含排名位置和页面数据。

**MCP 工具：** `dataforseo_labs_google_ranked_keywords`、`dataforseo_labs_google_relevant_pages`

**默认参数：**limit=100，location_code=2840

**输出：**关键词、排名、URL、搜索量、流量占比、SERP 特性。

### `/seo dataforseo intersection <domain1> <domain2> [...]`

查找 2-20 个域名之间共同的关键词和外链来源。

**MCP 工具：** `dataforseo_labs_google_domain_intersection`、`backlinks_domain_intersection`

**参数：**domains（2-20 个域名的数组）

**输出：**各域名的共同关键词及排名、共同外链来源、各域名独有关键词。

### `/seo dataforseo traffic <domains>`

估算一个或多个域名的自然搜索流量。

**MCP 工具：** `dataforseo_labs_bulk_traffic_estimation`

**参数：**domains（数组）

**输出：**域名、预估自然流量、预估流量价值、主要关键词。

### `/seo dataforseo subdomains <domain>`

枚举子域名，并给出其排名数据和流量估算。

**MCP 工具：** `dataforseo_labs_google_subdomains`

**参数：**target（域名）、location_code、language_code

**输出：**子域名、已排名关键词数、预估流量、自然流量价值。

### `/seo dataforseo top-searches <domain>`

查找搜索结果中提及特定域名的热门搜索词。

**MCP 工具：** `dataforseo_labs_google_top_searches`

**参数：**target（域名）、location_code、language_code

**输出：**查询词、搜索量、域名排名位置、SERP 特性、流量占比。

---

## 技术 / 页面分析

### `/seo dataforseo onpage <url>`

执行页面分析，包括 Lighthouse 审计和内容解析。

**MCP 工具：** `on_page_instant_pages`、`on_page_content_parsing`、`on_page_lighthouse`

**用途说明：**
- `on_page_instant_pages`：快速页面分析（状态码、meta 标签、内容体积、页面耗时、失效链接、页面检查项）
- `on_page_content_parsing`：提取并解析页面内容（纯文本、字数、结构）
- `on_page_lighthouse`：完整 Lighthouse 审计（性能得分、无障碍性、最佳实践、SEO、Core Web Vitals）

**输出：**已抓取页面、状态码、meta 标签、标题、内容体积、加载耗时、Lighthouse 分数、失效链接、资源分析。

### `/seo dataforseo tech <domain>`

检测域名所使用的技术栈。

**MCP 工具：** `domain_analytics_technologies_domain_technologies`

**输出：**技术名称、版本、类别（CMS、分析工具、CDN、框架等）。

### `/seo dataforseo whois <domain>`

获取 WHOIS 注册信息。

**MCP 工具：** `domain_analytics_whois_overview`

**输出：**注册商、创建日期、到期日期、域名服务器、注册人信息（如公开）。

---

## 内容与商家数据

### `/seo dataforseo content <keyword/url>`

分析内容质量、按主题搜索内容，并追踪短语趋势。

**MCP 工具：** `content_analysis_search`、`content_analysis_summary`、`content_analysis_phrase_trends`

**参数：**keyword（用于搜索/趋势）或 URL（用于摘要）

**输出：**带质量评分的内容匹配结果、情感分析、可读性指标、随时间变化的短语趋势数据。

### `/seo dataforseo listings <keyword>`

搜索商家信息，用于本地 SEO 的竞品分析。

**MCP 工具：** `business_data_business_listings_search`

**参数：**keyword、location（可选）

**输出：**商家名称、描述、类别、地址、电话、域名、评分、评论数、认领状态。

---

## AI 可见度 / GEO

### `/seo dataforseo ai-scrape <query>`

抓取 ChatGPT 网页搜索针对某查询返回的内容。真实的 GEO 可见度检测：查看 ChatGPT 针对目标关键词引用了哪些来源。

**MCP 工具：** `ai_optimization_chat_gpt_scraper`

**参数：**query、location_code（可选）、language_code（可选）。使用 `ai_optimization_chat_gpt_scraper_locations` 查询可用的地区。

**输出：**ChatGPT 回复内容、被引用的来源/URL、被引用的域名。

### `/seo dataforseo ai-mentions <keyword>`

追踪各类 LLM 如何提及品牌、域名和话题。对 GEO 至关重要——衡量在多个 LLM 平台上的真实 AI 可见度。

**MCP 工具：** `ai_opt_llm_ment_search`、`ai_opt_llm_ment_top_domains`、`ai_opt_llm_ment_top_pages`、`ai_opt_llm_ment_agg_metrics`

**参数：**keyword、location_code（可选）、language_code（可选）。使用 `ai_opt_llm_ment_loc_and_lang` 查询可用的地区/语言，使用 `ai_optimization_llm_models` 查询支持的 LLM 模型。

**工作流程：**
1. 用 `ai_opt_llm_ment_search` 搜索 LLM 提及情况（在 LLM 回复中查找品牌/关键词的提及）
2. 用 `ai_opt_llm_ment_top_domains` 获取被引用最多的域名（该主题下哪些域名被引用最频繁）
3. 用 `ai_opt_llm_ment_top_pages` 获取被引用最多的页面（哪些具体页面被引用最频繁）
4. 用 `ai_opt_llm_ment_agg_metrics` 获取汇总指标（整体提及量、趋势）

**输出：**LLM 提及次数、按频次排列的主要引用域名、主要引用页面、随时间变化的提及趋势、跨平台可见度评分。

**进阶用法：**使用 `ai_opt_llm_ment_cross_agg_metrics` 进行跨模型对比（提及情况在 ChatGPT、Claude、Perplexity 等平台间的差异）。

---

## 可用的其他工具

DataForSEO MCP 还提供了一些没有对应专属命令、供内部调用的工具。当需要查找特定的工具（地区查询、批量操作、历史数据、筛选选项）时，加载 `references/tool-catalog.md`。

## 跨技能集成

当 DataForSEO MCP 工具可用时，claude-seo 中的其他技能也可以利用实时数据：

- **seo-audit**：调用 `seo-dataforseo` 子代理获取真实的 SERP、外链、页面分析和商家信息数据
- **seo-technical**：使用 `on_page_instant_pages` / `on_page_lighthouse` 获取真实抓取数据，使用 `domain_analytics_technologies_domain_technologies` 进行技术栈检测
- **seo-content**：使用 `kw_data_google_ads_search_volume`、`dataforseo_labs_bulk_keyword_difficulty`、`dataforseo_labs_search_intent` 获取真实关键词指标，使用 `content_analysis_summary` 评估内容质量
- **seo-page**：使用 `serp_organic_live_advanced` 获取真实 SERP 排名，使用 `backlinks_summary` 获取外链数据
- **seo-images**：使用 `serp_google_images_live_advanced` 获取竞品图片 SERP 数据，与站内图片审计交叉对比
- **seo-geo**：使用 `ai_optimization_chat_gpt_scraper` 获取真实 ChatGPT 可见度，使用 `ai_opt_llm_ment_search` 追踪 LLM 提及情况
- **seo-plan**：使用 `dataforseo_labs_google_competitors_domain`、`dataforseo_labs_google_domain_intersection`、`dataforseo_labs_bulk_traffic_estimation` 获取真实竞争情报

## 错误处理

- **MCP 服务未连接**：报告 DataForSEO 扩展未安装或 MCP 服务不可达，建议运行 `./extensions/dataforseo/install.sh`
- **API 身份验证失败**：报告凭证无效，建议检查 MCP 配置中的 DataForSEO API 账号/密码
- **超出速率限制**：报告已触发限流，建议稍后重试
- **未返回结果**：如实报告该查询"未找到数据"，不要臆测，建议放宽查询范围或检查地区/语言代码
- **地区代码无效**：报告该错误，建议使用地区查询工具获取正确的代码

## 输出格式

保持与 claude-seo 现有输出风格一致：
- 对比数据使用表格呈现
- 按 Critical（严重）> High（高）> Medium（中）> Low（低）对问题分级
- 提供具体、可执行的建议
- 分数统一以 XX/100 的形式展示
- 注明数据来源为 "DataForSEO (live)"，以区别于静态分析结果
