![Claude SEO cover: a Claude Code command palette with /seo audit, schema, geo, content, and backlinks commands over a dark CRT panel](assets/cover.svg)

# Claude SEO：面向 Claude Code 的 SEO 技能

> 本文档基于 [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)（MIT License）汉化增强，供中文用户（尤其是跨境电商 / 独立站运营者）参考使用。原始英文文档见 [README.md](README.md)，本仓库的行为以英文原版为准，中文版仅作阅读辅助。

**Claude SEO 是一款面向 [Claude Code](https://claude.ai/claude-code) 的开源 SEO 分析插件。** 它可以并行运行 25 个子技能（sub-skills）和 18 个专项子代理（specialist agents），覆盖技术 SEO、内容质量（E-E-A-T）、Schema.org 结构化数据、AI 搜索优化（GEO）、本地 SEO、电商 SEO 以及国际化 SEO。每次审计都会产出一份带优先级的行动计划，每条建议都有可验证的依据，并参考 Google 的一手指南。

[![CI](https://github.com/AgriciDaniel/claude-seo/actions/workflows/ci.yml/badge.svg)](https://github.com/AgriciDaniel/claude-seo/actions/workflows/ci.yml)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://claude.ai/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/AgriciDaniel/claude-seo)](https://github.com/AgriciDaniel/claude-seo/releases)
[![Tests](https://img.shields.io/badge/tests-326%20passing-brightgreen)](tests/)
[![Community](https://img.shields.io/badge/AI%20Marketing%20Hub-Pro%20community-purple)](https://www.skool.com/ai-marketing-hub-pro)

> **本技能有两个版本。**
> - 🌐 **公开开源版** → [`AgriciDaniel/claude-seo`](https://github.com/AgriciDaniel/claude-seo)：MIT 协议，公开发布，无需付费会员。如果你想要稳定可下载的版本，请使用这个。
> - 🔒 **社区私有镜像版** → [`AI-Marketing-Hub/claude-seo`](https://github.com/AI-Marketing-Hub/claude-seo)：可提前体验即将上线的功能，并与 [AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro) 社区直接协作。需要付费会员资格。

### 为什么选择 Claude SEO

- **AI 搜索优先。** 与 [Google 的 AI Optimization Guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) 保持一致。基于问题的可引用性评分，llms.txt 的一手证据分析，面向 AI 生成商品图片的 IPTC `TrainedAlgorithmicMedia` 标注，以及依据 [web.dev](https://web.dev/) 标准的智能体友好页面检测。
- **并行执行。** 全站审计可同时启动多达 15 个专项子代理。站点级审计几分钟内即可完成，而不是数小时。
- **可证伪，而非营销话术。** 每条建议都附带其所依据的第一性原理观察、依赖关系、明确的"如何判断它失败了"检验方法，以及一个先行指标。详见 [方法论](#方法论)。

### 真实效果

![Google Search Console clicks and impressions for a three-month-old site climbing from launch to steady organic growth between 23 March and 12 June 2026](assets/growth-3-months.png)

某站点于 2026 年 3 月 23 日上线，并按本工作流运营：图中展示了其上线后前三个月（截至 2026 年 6 月 12 日）的总点击量和展现量。

> 如果你用的是 Codex 而非 Claude Code？可以使用 [Codex SEO](https://github.com/AgriciDaniel/codex-seo)，这是面向 Codex 的移植版本，采用 TOML 代理、插件化打包、确定性执行器，并保留了相同的 SEO 工作流。

## 适合谁使用

- **管理 5 个以上客户站点的 SEO 代理机构。** 用每周自动化审计取代季度深度审计。团队规模不变，审计频率提升 4 倍，每条建议都附带客户可自行验证的可证伪性检验。
- **SaaS / 内容媒体 / 电商公司的内部 SEO 负责人。** 在高管评审前多一双眼睛把关。能发现 GSC 和 Lighthouse 无法察觉的问题：schema 被弃用、AI 可引用性缺口、过期域名的历史风险、寄生 SEO 暴露、机器翻译漂移。
- **自由职业 SEO 顾问。** 用 15 分钟审计和真实的 0-100 分打分，在第一天就锚定客户项目范围。在花一小时写提案之前，就用具体的价值证明拿下合作。

![Claude SEO /seo command demo in Claude Code terminal](screenshots/seo-command-demo.gif)

运行一次全站审计，看并行代理如何在站点内展开分析：

![Claude SEO /seo audit demo: parallel subagents producing a prioritized action plan](screenshots/seo-audit-demo.gif)

[在 YouTube 观看完整演示](https://www.youtube.com/watch?v=COMnNlUakQk)

## 目录

- [适合谁使用](#适合谁使用)
- [安装](#安装)
- [快速开始](#快速开始)
- [命令](#命令)
- [功能特性](#功能特性)
- [与人工/代理机构/商业工具的对比](#与人工代理机构商业工具的对比)
- [使用场景](#使用场景)
- [示例输出](#示例输出)
- [架构](#架构)
- [方法论](#方法论)
- [v2 版本新增内容](#v2-版本新增内容)
- [局限性](#局限性)
- [环境要求](#环境要求)
- [卸载](#卸载)
- [扩展](#扩展)
- [生态系统](#生态系统)
- [文档](#文档)
- [常见问题](#常见问题)
- [社区贡献者](#社区贡献者)
- [许可证](#许可证)
- [贡献指南](#贡献指南)
- [作者](#作者)

## 安装

> ℹ️ **你要安装的是哪个版本？**
>
> - **公开开源版（默认）。** 下方命令默认从 [`AgriciDaniel/claude-seo`](https://github.com/AgriciDaniel/claude-seo) 安装——MIT 协议，公开发布，无需会员资格。
> - **AI Marketing Hub Pro 会员？** 改为安装可提前体验新功能的社区版：将 `AgriciDaniel/claude-seo` 替换为 `AI-Marketing-Hub/claude-seo`，插件标识 `claude-seo@agricidaniel-claude-seo` 替换为 `claude-seo@ai-marketing-hub-claude-seo`。需要 `gh auth login`（或 PAT）并拥有 `AI-Marketing-Hub` 组织的访问权限。如果 `/plugin marketplace add` 返回 404，请在 [Skool 社区](https://www.skool.com/ai-marketing-hub-pro) 私信申请加入。

> 🇨🇳 **中国大陆网络环境提示：** 如果 `git clone`、`npm`/`npx` 或 Playwright 浏览器下载速度慢或超时，可考虑：
> - pip 安装依赖时使用清华源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
> - Playwright 浏览器下载使用 npmmirror 镜像：在安装前设置环境变量 `export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/`（Windows PowerShell 下用 `$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright/"`），再执行安装脚本。
> - 如需要，也可为 `git`/`npm` 配置可用的镜像或代理后再执行下方命令。

### 插件安装（Claude Code 1.0.33 及以上版本）

最快的方式。一次性添加 marketplace，然后安装插件：

```bash
/plugin marketplace add AgriciDaniel/claude-seo
/plugin install claude-seo@agricidaniel-claude-seo
```

### 手动安装（Unix / macOS / Linux）

```bash
git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git
bash claude-seo/install.sh
```

<details>
<summary>一行命令安装（curl，建议先审阅脚本再运行）</summary>

```bash
curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/install.sh > install.sh
cat install.sh        # 运行前先审阅脚本内容
bash install.sh
rm install.sh
```

</details>

### Windows（PowerShell）

```powershell
git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git
powershell -ExecutionPolicy Bypass -File claude-seo\install.ps1
```

> **为什么用 `git clone` 而不是 `irm | iex`？** Claude Code 自身的安全护栏会将 `irm ... | iex` 标记为供应链风险：未经验证就下载并执行远程代码。而 `git clone` 方式可以让你在运行之前先检查 `claude-seo\install.ps1` 的内容。

## 快速开始

```bash
# 启动 Claude Code
claude

# 全站审计：并行子代理产出带优先级的行动计划
/seo audit https://example.com

# 深度单页分析：页面元素、内容质量、schema
/seo page https://example.com/about

# Schema 结构化数据审计：检测、验证、生成
/seo schema https://example.com

# AI 搜索优化：段落可引用性 + 基于一手来源的建议
/seo geo https://example.com

# 使用行业模板生成站点地图
/seo sitemap generate
```

## 命令

![Claude SEO sub-skill ecosystem: 25 modules grouped into 8 categories (audit, content, schema, technical, AI search, local + maps, commerce + intl, extensions) around the central orchestrator](assets/sub-skills.svg)

围绕中央编排器（orchestrator）及其子技能，共有 25 个可由用户直接调用的 `/seo` 命令。完整参考见 [docs/COMMANDS.md](docs/COMMANDS.md)。

| 命令 | 说明 |
|---------|-------------|
| `/seo audit <url>` | 全站审计，带并行子代理委派 |
| `/seo page <url>` | 深度单页分析 |
| `/seo technical <url>` | 覆盖 9 个类别的技术 SEO 审计 |
| `/seo content <url>` | E-E-A-T 与内容质量分析 |
| `/seo content-brief <topic>` | 详细内容简报：目标关键词、大纲、内部链接 |
| `/seo schema <url>` | 检测、验证并生成 Schema.org 标记 |
| `/seo geo <url>` | AI Overviews / 生成式引擎优化（GEO） |
| `/seo sitemap <url \| generate>` | 分析或生成 XML 站点地图 |
| `/seo images <url>` | 图片优化分析 |
| `/seo plan <type>` | 战略性 SEO 规划（saas、local、ecommerce、publisher、agency） |
| `/seo programmatic <url>` | 规模化（程序化）SEO 分析与规划 |
| `/seo competitor-pages <url>` | 生成竞品对比页面 |
| `/seo local <url>` | 本地 SEO 分析（GBP、引用、评论、地图包） |
| `/seo maps [command]` | 地图智能分析（地理网格排名追踪、GBP 审计、评论、竞争对手） |
| `/seo hreflang <url>` | Hreflang / 国际化 SEO 审计与生成 |
| `/seo google [command]` | Google SEO API（GSC、PageSpeed、CrUX、Indexing、GA4、PDF 报告） |
| `/seo backlinks <url>` | 外链画像分析（Moz、Bing、Common Crawl） |
| `/seo cluster <keyword>` | 基于 SERP 的语义聚类 |
| `/seo sxo <url>` | 搜索体验优化（页面类型、用户故事、人物画像） |
| `/seo drift baseline \| compare \| history <url>` | 基于 SQLite 快照的 SEO 变化监控 |
| `/seo ecommerce <url>` | 电商 SEO 与市场情报 |
| `/seo flow [stage]` | FLOW 框架提示词（CC BY 4.0，证据驱动） |
| `/seo firecrawl [command] <url>` | 全站爬取（扩展） |
| `/seo dataforseo [command]` | 实时 SEO 数据（扩展） |
| `/seo image-gen [use-case]` | 面向 SEO 素材的 AI 图片生成（扩展） |

## 功能特性

### Claude SEO 检测哪些 Core Web Vitals 指标？

Claude SEO 测量当前的三项 Core Web Vitals 指标：**LCP**（最大内容绘制，目标低于 2.5 秒）、**INP**（下次绘制交互，目标低于 200 毫秒）、**CLS**（累积布局偏移，目标低于 0.1）。[INP 于 2024 年 3 月 12 日取代了 FID](https://web.dev/articles/inp)；FID 已于 2024 年 9 月 9 日从所有 Chrome 工具（CrUX API、PageSpeed Insights、Lighthouse）中移除，Claude SEO 不再引用 FID。现场数据（field data）在可用时来自 Chrome User Experience Report（CrUX）；实验室数据（lab data）则通过 PageSpeed Insights 的 Lighthouse 兜底。LCP 可通过 `/seo google` 的 CrUX 集成拆解为多个子阶段（TTFB、加载延迟、加载时长、渲染延迟），以定位瓶颈所在。移动端和桌面端分别测量。CrUX History（25 周趋势）已包含在 Tier 0 免费凭证集中。

### Claude SEO 如何评估 E-E-A-T？

E-E-A-T（经验、专业性、权威性、可信度）依据 Search Quality Rater Guidelines 评估，该指南最近一次更新于 2025 年 9 月，将 YMYL 范围扩展到政治和社会议题。经验信号：原创研究、案例研究、第一手照片。专业性：作者资历和话题深度。权威性：外部引用和品牌提及。可信度是四项中权重最高的：联系方式、安全的 HTTPS、透明的更正记录、日期标注。在为各子因素打分之前，Claude SEO 会先应用 Google 自身在 [helpful-content 指南](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)中提出的 Who / How / Why 启发式方法。生成式 AI 内容只要满足 Search Essentials 就没有问题；一旦被用来批量生产低价值页面就会越界成为垃圾内容，这正是 `seo-content humanize` 和 `seo-content verify` 设计用来检测的对象。

### Claude SEO 支持哪些 Schema.org 类型？

JSON-LD 是首选格式（这也是 Google 明确表态的偏好）。Claude SEO 能检测、验证并生成的活跃类型包括：Organization、LocalBusiness、Article、BlogPosting、NewsArticle、Product、ProductGroup、Offer、Review、AggregateRating、BreadcrumbList、WebSite、WebPage、Person、ProfilePage、ContactPage、VideoObject、ImageObject、Event、JobPosting、Course、DiscussionForumPosting、Reservation、OrderAction，以及视频和专用类型（BroadcastEvent、Clip、SeekToAction、SoftwareSourceCode）。FAQPage：Google 已于 2026 年 5 月 7 日停止为所有站点展示 FAQ 富结果；它仍可作为辅助性的 AI/实体信号存在，但不再用于富结果展示。已弃用且不再推荐的类型：HowTo（富结果已于 2023 年 9 月移除）、SpecialAnnouncement（2025 年 7 月）、ClaimReview、VehicleListing、EstimatedSalary、LearningVideo、CourseInfo 轮播（均已于 2025 年 6 月退役）。替代方案指南见：[skills/seo-schema/references/deprecated-types-2024-2026.md](skills/seo-schema/references/deprecated-types-2024-2026.md)。

### Claude SEO 如何为 AI 搜索做优化？

与 [Google 的 AI Optimization Guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) 保持一致，该指南指出 "AEO" 和 "GEO" 只是 SEO 的改名标签。AI Overviews 和 AI Mode 都建立在与经典搜索相同的排名系统之上；页面必须被索引并具备摘要展示资格，才能出现在任何 AI 功能中。Claude SEO 为段落可引用性（最佳为 134-167 词的自足式答案块）、基于问题的标题层级结构、引用密度、结构化数据覆盖率，以及在 Wikipedia、Reddit、YouTube、LinkedIn 上的实体存在度打分。`seo-geo` 技能针对三个流行的"网红"迷思提供了基于证据的重新解读：llms.txt 目前并非引用杠杆（[一手证据](skills/seo-geo/references/llmstxt-evidence.md)）、内容分块（content chunking）并非必需、以及针对 AI 的关键词重写没有必要，因为同义词理解已经足够。

### Claude SEO 集成了哪些 Google SEO API？

一套 4 层凭证体系让你可以从零密钥开始，按需逐步添加数据。每一层都能在其对应层级提供真实价值：

| 层级 | 所需凭证 | 解锁的 API |
|------|------|------|
| 0 | API key | PageSpeed Insights、CrUX、CrUX History（25 周趋势） |
| 1 | + OAuth 或服务账号 | + Search Console（查询、URL 检查、站点地图状态）、Indexing API |
| 2 | + GA4 属性配置 | + GA4 自然流量、热门落地页、设备/国家细分 |
| 3 | + Ads 开发者令牌 | + Keyword Planner 搜索量与竞争度数据 |

PDF 报告通过 [WeasyPrint](https://weasyprint.org/) 生成（A4 排版），图表由 matplotlib 以 200 DPI 绘制。运行 `/seo google setup` 启动凭证配置向导。所有凭证都保存在 `~/.config/claude-seo/` 下，权限为 `0o600`；不会有任何凭证被提交进仓库。

### Claude SEO 如何处理本地 SEO？

分为三层。**Google Business Profile 信号**：分类、营业时间、照片、动态、商品、属性。**跨引用的 NAP 一致性**：名称、地址、电话与主要目录做比对并标记差异。**评论情报**：评分趋势、情感分析、回复覆盖率。对于多门店企业，Claude SEO 会强制执行 30 页警告阈值和 50 页硬性上限，以防止入口页（doorway page）违规（可配置）。`/seo maps` 工作流增加了地理网格排名追踪、GBP 资料审计和竞争对手半径映射。本地 schema 生成覆盖 `LocalBusiness` 的全部必需及推荐属性（地理坐标、营业时间、areaServed）。Phase F（v2）新增了 GBP 弃用检测器，用于检测已退役的聊天字段引用和 `.business.site` 网址。

## 与人工/代理机构/商业工具的对比

| | 人工审计 | 代理机构服务 | 商业 SEO 审计工具 | **Claude SEO** |
|---|---|---|---|---|
| **单次审计耗时** | 资深 SEO 4-8 小时 | 1-3 周交付周期 | 10-45 分钟爬取 + 生成报告 | **10-15 分钟** |
| **成本** | 高（按小时计费） | 2000-15000+ 美元/项目 | 99-999 美元/月订阅 | **免费技能 + Claude Code 订阅** |
| **可重复性** | 不同分析师结果不一致 | 不同项目之间不一致 | 是 | **是，确定性且可脚本化** |
| **输出格式** | 一堆发现的 PDF | 品牌化的幻灯片 | 网页仪表盘、CSV 导出 | **Markdown + PDF + JSON，本地文件** |
| **自定义基准** | 因分析师而异 | 代理机构专属框架 | 供应商固定 | **可编辑本地 SKILL.md** |
| **数据是否离开本机？** | 否（你自己的表格） | 是（发送给代理机构） | 是（上传给供应商） | **否，默认完全本地** |
| **锁定风险** | 无 | 高 | 高（数据迁出成本高） | **无。MIT 协议，数据都是你的文件。** |
| **AI 搜索认知** | 视分析师而定 | 视代理机构资历而定 | 滞后（通常落后 6-12 个月） | **Google AI Optimization Guide（2026 年 5 月）、2025 年 9 月 QRG、INP 取代 FID、GEO/AEO=SEO 的重新定位、基于证据的 llms.txt 立场** |
| **每条建议的可证伪性** | 无 | 无 | 无 | **有。每条建议都附带"如何判断它失败了"的检验方法 + 先行指标** |

> 成本基准说明：人工审计按资深 SEO 顾问在典型代理机构计费费率估算；代理机构服务基于常见的发现/审计交付范围；商业工具订阅费反映 SEO 审计类目下已公开的中端定价（Ahrefs、Semrush、Sitebulb、Screaming Frog）。你的实际数字可能有所不同。

## 使用场景

**管理 10 个客户站点的 SEO 代理机构负责人。** 用每周一早上的 `/seo audit` 运行取代季度"深度审计"仪式。生成客户健康评分邮件的耗时从 4 小时降到 12 分钟；覆盖频率从季度变为每周，且无需增加计费工时。变化监控（drift baseline）能在两次审计之间捕获回归问题，让与客户的对话从"看看这份快照"变成"这是本周发生的变化"。

**50 人规模 SaaS 公司的内部 SEO 负责人。** 在每次季度业务评审前 24 小时运行 `/seo audit`。能在 CMO 在董事会上被问及自然流量为何下滑之前，发现平台界面掩盖的问题（程序化页面上损坏的规范链接链、Google 2025 年 6 月退役潮之后的 schema 弃用、侵蚀 SERP 到 AI Overview 转化的 AI 可引用性缺口、收购博客资产上的过期域名历史问题）。

**为新客户提供服务的自由职业 SEO 顾问。** 在首次沟通电话中就运行 `/seo audit`。用真实的 0-100 分评分、3 项优先级最高的关键发现，以及每条建议附带的可证伪性检验来锚定项目范围，而不是含糊地说"我看看再回复你"。因为价值证明发生在通话过程中而非提案之后，成交率更高。

## 示例输出

Claude SEO 的主要交付物是真实的 markdown 报告。以下是一次 `/seo schema https://rankenstein.pro/about` 审计的原文前约 50 行。实际结构、标题和评级格式与插件产出的一致。

<details>
<summary><code>SCHEMA-REPORT.md</code>：一次真实审计的前 50 行</summary>

```markdown
# Schema Markup Report: rankenstein.pro/about

**URL:** https://rankenstein.pro/about
**Date:** 2026-02-09
**Format Detected:** JSON-LD (3 blocks) | No Microdata | No RDFa

---

## Summary

| Metric | Value |
|--------|-------|
| **JSON-LD Blocks** | 3 |
| **Schema Types** | Organization, WebSite, SoftwareApplication |
| **Critical Issues** | 2 |
| **Warnings** | 5 |
| **Passed Checks** | 18 |
| **Overall Grade** | B+ (solid foundation, actionable gaps) |

---

## Existing Schema Validation

### 1. Organization (`@id: #organization`)

| Property | Value | Status | Notes |
|----------|-------|--------|-------|
| `@context` | https://schema.org | Valid | |
| `@type` | Organization | Valid | Active type |
| `@id` | https://rankenstein.pro#organization | Good | Enables cross-referencing |
| `name` | Rankenstein | Valid | |
| `description` | Present, 200+ chars | Good | Descriptive and keyword-rich |
| `url` | https://rankenstein.pro | Valid | Absolute URL |
| `logo` | ImageObject with @id, url, width, height, caption | Excellent | Well-structured |
| `foundingDate` | "2024" | Imprecise | Year-only accepted but ISO 8601 preferred |
| `areaServed` | "Worldwide" | Text | Works but `GeoShape` is more semantic |
| `contactPoint` | email + contactType | Valid | Consider adding `telephone` |
| `founder` | 1 Person (Daniel Agrici) | Incomplete | Page describes two co-founders; second missing |
| `sameAs` | 5 social profiles | Good | GitHub, X, LinkedIn, YouTube, Reddit |
| `knowsAbout` | 6 topics | Good | Relevant topical signals |

**Critical Issue:** The `founder` property only includes Daniel Agrici. Benjamin Samar (Co-Founder & Technical Director) is displayed on the page but absent from the schema. This creates a content-schema mismatch that can confuse search engines.
```

</details>

其他审计输出遵循相同的结构：`FULL-AUDIT-REPORT.md`（综合审计）、`GEO-ANALYSIS.md`（AI 搜索就绪度）、`LOCAL-SEO-ANALYSIS.md`（GBP 与引用），以及一份通过 WeasyPrint + matplotlib 生成的正式 PDF（封面、目录、执行摘要、数据章节、建议、方法论，一次全站审计约 32 页 A4）。

## 架构

![Claude SEO audit signal flow: /seo audit enters the orchestrator, fans out to 25 sub-skills and 6 parallel audit agents, and converges through the scoring engine into a prioritized report](assets/signal-flow.svg)

该插件遵循 [Agent Skills 标准](https://docs.claude.com/en/docs/claude-code/skills)，采用三层架构（指令层、编排层、执行层）。技能和代理会从 `skills/seo-*/` 和 `agents/seo-*.md` 自动发现。编排器（`skills/seo/SKILL.md`）负责行业检测（SaaS、本地、电商、内容媒体、代理机构）、最多同时调度 15 个并行子代理，并通过 [10 原则框架](#方法论) 完成综合分析，最终输出行动计划。完整架构见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 方法论

![Claude SEO 10-principle methodology: PERCEIVE, ANALYZE, VALIDATE, and ACT phases with 10 principles arranged by quadrant](assets/framework.svg)

每次审计都遵循分为四个阶段的 10 条原则。每条产出的建议都携带四个字段：所依据的第一性原理观察、与其他建议的依赖关系、"如何判断它失败了"的检验方法，以及需要监控的先行指标。

| 阶段 | 原则 | 作用 |
|---|---|---|
| **感知（PERCEIVE）** | 观察（外部）· 观察（内部）· 倾听 | 收集原始信号；审视自身假设；解读 SERP、品牌声音和社区实际在说什么 |
| **分析（ANALYZE）** | 思考 · 横向连接 · 系统连接 | 归纳为第一性原理；发现非显而易见的跨技能关联；排列成依赖关系图 |
| **验证（VALIDATE）** | 感受 · 接受 | 用用户体验、品牌调性、运营方能力做压力测试；呈现可证伪性 |
| **行动（ACT）** | 创造 · 增长 | 交付成果物；为下一次审计设置反馈闭环 |

完整方法论见：[skills/seo/references/thinking-framework.md](skills/seo/references/thinking-framework.md)。

## v2 版本新增内容

v2.0.0 是该插件历史上规模最大的一次发版，包含六个已全部交付的构建阶段：

- **Phase A：无头渲染全面覆盖。** 共享的 `scripts/render_page.py`，使用 Playwright Chromium，配合 [trafilatura](https://github.com/adbar/trafilatura) 和 [htmldate](https://github.com/adbar/htmldate)。每个审计子代理都通过 `--render auto`（自动检测 Next.js、React、Vue、Nuxt、Astro islands）获得对 SPA 友好的抓取能力，解决了 v1.x 中限制单页应用支持的问题。
- **Phase B：符合 QRG 的内容质量关卡。** 填充内容检测器和 AI 痕迹去除器，对应 QRG §4.6.5 和 §4.6.6；断言核实扫描器；通过 WHOIS 进行的过期域名历史检查；一手来源的 Google 更新日志。
- **Phase C：技术与 CWV 深度分析。** 通过 CrUX 拆解 LCP 子阶段（TTFB、加载延迟、加载时长、渲染延迟）；Speculation Rules 与 bfcache 检测；面向 Bing / Yandex / Seznam / Naver 的 IndexNow 提交器；Unlighthouse 多页 Lighthouse 包装器。
- **Phase D：schema 完整性。** 四个显式生成器（Reservation、OrderAction、DiscussionForumPosting、ProfilePage）；电商 schema 验证器（`hasMerchantReturnPolicy`、`shippingDetails`、`MemberProgram`、欧盟 `energyEfficiencyClass`、ProductGroup 变体）；双重验证器（Rich Results Test 加上 Schema Markup Validator）。
- **Phase E：AI 搜索重新定位与 5 个新增 MCP 扩展。** Ahrefs、SE Ranking（AI Share-of-Voice）、Profound（LLM 引用追踪器）、Bing Webmaster 加 IndexNow、Unlighthouse。此外还新增了依据 Google 2024 年 11 月[站点信誉滥用政策](https://developers.google.com/search/blog/2024/11/site-reputation-abuse-update)的寄生 SEO 风险扫描器。
- **Phase F：本地化、国际化及隐私打磨。** Google Business Profile 弃用检测器（聊天字段、`.business.site` 网址、问答）；DMA 同意模式 v2 点击穿透诊断；依据 2025 年 1 月 QRG 的机器翻译质检标记。

测试覆盖率：从 248 提升到 271（相比 v1.9.9 基线增长 5.4 倍）。83 个 SSRF 与 DNS 重绑定绕过测试，涵盖了完整的混淆 IPv4、FQDN 尾部句点，以及重定向重绑定绕过场景。完整迁移说明与破坏性变更见：[docs/MIGRATION-v1-to-v2.md](docs/MIGRATION-v1-to-v2.md)。

## 局限性

有两个真实存在、值得坦诚说明的边界。

**重度客户端渲染时机问题。** Phase A 的无头渲染器开箱即可处理大多数 SPA（`--render auto` 会检测空的 `<div id="root">` 壳体并切换到 Playwright）。仍会产生噪声结果的边界情况包括：渲染依赖滚动到首屏以下位置的页面、需要用户交互后才加载关键内容的页面（弹窗打开、标签点击）、存在竞态条件的第三方组件挂载的页面。对于这些情况，推荐的工作流是手动触发 `seo-visual` 子代理，并将其 Playwright 快照与原始 HTML 子代理的发现进行对比。

**默认无外部数据增强，纯本地运行。** 免费层不会调用任何外部 API，产生零网络请求的输出。添加 Google API 凭证（Tier 0 到 Tier 3）可解锁真实的现场数据和实时索引状态；不添加时，Core Web Vitals 仅为实验室估算值，索引状态则依据页面级信号推断。添加 MCP 扩展（Ahrefs、DataForSEO、SE Ranking、Profound）同样可解锁竞争情报和 AI 引用数据，但需要各自的账号。

## 环境要求

- Python 3.10+
- Claude Code CLI
- 可选：Playwright Chromium（由 `install.sh` 自动安装），用于 SPA 渲染和截图
- 可选：Google API 凭证，用于增强版 CWV / GSC / GA4 数据（见 `/seo google setup`）

## 卸载

```bash
git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git
bash claude-seo/uninstall.sh
```

<details>
<summary>一行命令（curl）</summary>

```bash
curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/uninstall.sh | bash
```

</details>

## 扩展

可选的 MCP 服务器可为审计流程增加实时数据。Claude SEO 为 8 个服务器提供了扩展；插件核心功能无需依赖任何一个即可正常工作。

### DataForSEO

实时 SERP 数据、关键词研究、外链、页面分析、内容分析、商家列表、AI 可见度检测和 LLM 提及追踪。9 个 API 模块共 22 个命令。

```bash
./extensions/dataforseo/install.sh   # 需要 DataForSEO 账号
/seo dataforseo serp best coffee shops
/seo dataforseo ai-mentions your brand
```

完整 DataForSEO 文档见：[extensions/dataforseo/README.md](extensions/dataforseo/README.md)。

### Firecrawl

通过 [Firecrawl](https://www.firecrawl.dev/) MCP 服务器实现全站爬取和 URL 发现。

```bash
./extensions/firecrawl/install.sh
/seo firecrawl crawl https://example.com
```

完整 Firecrawl 文档见：[extensions/firecrawl/README.md](extensions/firecrawl/README.md)。

### Banana：AI 图片生成

通过 [Claude Banana](https://github.com/AgriciDaniel/banana-claude) Creative Director 流水线生成 SEO 图片素材（OG 预览图、博客首图、商品照片、信息图）。

```bash
./extensions/banana/install.sh
/seo image-gen og "Professional SaaS dashboard"
```

完整 Banana 文档见：[extensions/banana/README.md](extensions/banana/README.md)。

### Ahrefs、SE Ranking、Profound、Bing Webmaster、Unlighthouse（v2 新增）

Phase E 新增的五个扩展：

- **Ahrefs：** 官方 `@ahrefs/mcp` 服务器，提供外链和自然流量数据
- **SE Ranking：** 覆盖 ChatGPT、Gemini、Perplexity、AI Overviews、AI Mode 的 AI Share-of-Voice
- **Profound：** 带时间序列数据的 LLM 引用追踪器
- **Bing Webmaster：** Bing Webmaster Tools 加 IndexNow 一体化
- **Unlighthouse：** MIT 许可的多页 Lighthouse 运行器

配置指南见：[docs/MCP-INTEGRATION.md](docs/MCP-INTEGRATION.md)。

## 生态系统

Claude SEO 是一系列可无缝协作的 Claude Code 技能家族的一员：

| 技能 | 功能 | 如何衔接 |
|-------|-------------|-----------------|
| [Claude SEO](https://github.com/AgriciDaniel/claude-seo) | SEO 分析、审计、schema、GEO | 核心。分析站点并生成行动计划。 |
| [Claude Blog](https://github.com/AgriciDaniel/claude-blog) | 博客撰写、优化、打分 | 配套工具。撰写经 SEO 发现优化过的内容。 |
| [Claude Banana](https://github.com/AgriciDaniel/banana-claude) | 通过 Gemini 生成 AI 图片 | 共享工具。为 SEO 素材和博客文章生成图片。 |
| [Codex SEO](https://github.com/AgriciDaniel/codex-seo) | 面向 Codex 的 SEO 技能套件 | 移植版本。同一套 SEO 系统适配为 Codex 技能、TOML 代理、确定性执行器。 |
| [AI Marketing Claude](https://github.com/zubair-trabzada/ai-marketing-claude) | 文案、邮件、社交、广告、转化漏斗、CRO | 社区项目。根据 SEO 发现执行后续营销动作。 |
| [FLOW](https://github.com/AgriciDaniel/flow) | 证据驱动的 SEO 框架（41 条 AI 提示词，CC BY 4.0） | 知识库。为 `seo-flow` 提示词提供支撑。 |

**工作流示例：**

1. `/seo audit https://example.com`：识别内容缺口和技术问题
2. `/seo backlinks https://example.com`：分析外链画像和竞争对手差距
3. `/seo geo https://example.com/blog/post`：为 AI 引用就绪度打分
4. `/blog write "target keyword"`：创作 SEO 优化的博客文章（Claude Blog）
5. `/seo image-gen hero "blog topic"`：生成首图（Banana 扩展）

## 文档

- [安装指南](docs/INSTALLATION.md)
- [命令参考](docs/COMMANDS.md)：每个 `/seo` 命令的详细说明
- [架构](docs/ARCHITECTURE.md)：三层设计、自动发现、并行调度
- [v1 → v2 迁移指南](docs/MIGRATION-v1-to-v2.md)：破坏性变更、六个开发阶段
- [MCP 集成](docs/MCP-INTEGRATION.md)：全部 8 个服务器的扩展配置
- [故障排查](docs/TROUBLESHOOTING.md)
- [贡献者名单](CONTRIBUTORS.md)：社区致谢

## 常见问题

### Claude SEO 是什么？

Claude SEO 是一款面向 Claude Code 的开源 SEO 分析插件。它可以并行运行 25 个子技能和 18 个专项代理，覆盖技术 SEO、内容质量、Schema.org 结构化数据、AI 搜索优化、本地 SEO、电商以及国际化 SEO。审计会产出带优先级的行动计划，其中每条建议都附带其所依据的第一性原理观察、与其他建议的依赖关系、"如何判断它失败了"的检验方法，以及一个先行指标。该插件采用 MIT 协议，不含任何专有追踪代码，如果跳过可选的 Google API 和 MCP 扩展增强功能，可完全离线运行。与 [Google 的 AI Optimization Guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) 及 2025 年 9 月版 Quality Rater Guidelines 保持一致。

### Claude SEO 与 Screaming Frog 或 Ahrefs Site Audit 有什么不同？

覆盖面不同，取舍也不同。**Screaming Frog** 在链接图谱层面爬取得更深更快；它本身就是为爬虫而生的专用工具，Claude SEO 无意取代它。**Ahrefs Site Audit** 拥有专有的外链索引和链接情报；Claude SEO 通过其 MCP 扩展与 Ahrefs 集成，而不是与之竞争。Claude SEO 的优势在于：对话式的 LLM 原生工作流、建议的可证伪性（每条发现都附带明确的失败模式检验）、开源 MIT 协议且无按域名收费、与 Google 一手指南保持一致的 AI 搜索优化，以及基于一手来源的 schema 弃用追踪。该用 Screaming Frog 或 Ahrefs 的场景就用它们最擅长的地方；想要 LLM 驱动的综合分析、对话式迭代，以及与你其他 Claude Code 工作流处于同一环境的 AI 搜索优先审计时，就用 Claude SEO。

### Claude SEO 支持单页应用（Next.js、React、Vue）吗？

支持。v2 的 Phase A 交付了一个由 Playwright Chromium 驱动的共享无头渲染器（`scripts/render_page.py`）。每个抓取子代理都支持 `--render auto`（默认选项），它会自动检测 SPA 特征（空的 `<div id="root">` 壳体、单一打包脚本、hydration 标记）并切换到渲染后抓取模式。设置 `--render always` 可强制渲染，或 `--render never` 仅使用原始 HTML。内容提取使用 [trafilatura](https://github.com/adbar/trafilatura) 去除模板样板内容。发布日期来自 [htmldate](https://github.com/adbar/htmldate)。已知的细微差异：渲染依赖滚动位置或交互后内容加载的页面仍会产生噪声结果；这些边界情况下推荐的 `seo-visual` 交叉核查工作流见[局限性](#局限性)一节。

### Claude SEO 用到了哪些 Google API？是否必需？

都不是必需的。Claude SEO 在零 API 密钥的情况下也能完全正常使用。一套 4 层凭证体系可以让你逐步升级：Tier 0（仅需 API key）解锁 PageSpeed Insights、CrUX 以及 CrUX History（25 周趋势数据）。Tier 1（+ OAuth 或服务账号）新增带查询、URL 检查、站点地图状态的 Search Console，以及 Indexing API。Tier 2（+ GA4 属性配置）新增自然流量、热门落地页、设备/国家细分。Tier 3（+ Ads 开发者令牌）新增 Keyword Planner 搜索量与竞争度数据。凭证配置向导通过 `/seo google setup` 运行。所有凭证保存在 `~/.config/claude-seo/` 下，文件权限为 `0o600`；不会有任何凭证被提交进仓库，也不会有数据被传输到 Google 自身端点之外的地方。

### Claude SEO 是免费的吗？

是的。MIT 协议，完全开源，无按域名收费，无遥测数据收集，插件本身不设置任何 API 配额限制。核心插件及全部 25 个子技能均无需任何付费服务即可运行。部分可选的 MCP 扩展会封装付费服务（DataForSEO、Ahrefs、Profound、SE Ranking），需要你自备账号凭证；使用这些扩展是可选的，插件在没有它们的情况下也能完全正常工作。Google API（PageSpeed Insights、Search Console、Indexing、GA4）由 Google 免费提供，受常规账号配额限制，需要你自己的凭证。如果你需要本开源插件之外的商业支持或企业级功能，这不在本项目范围之内。

### 在 AI 搜索方面，Claude SEO 与常规 SEO 工具有何不同？

大多数 SEO 工具把 AI 搜索当作一个独立的优化门类来处理。Claude SEO 遵循 [Google 自身的立场](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)：AEO 和 GEO 只是 SEO 的改名标签。AI Overviews 和 AI Mode 建立在与经典搜索相同的排名系统之上；进入这些功能的资格门槛就是正常的索引收录。Claude SEO 为段落可引用性（134-167 词的自足式答案块）、基于问题的标题层级结构、引用密度，以及在 Wikipedia、Reddit、YouTube、LinkedIn 上的实体存在度打分。它明确拒绝三个网红迷思：llms.txt 作为引用杠杆、为 AI 做内容分块、以及针对 AI 的专门关键词重写。对于电商站点，Claude SEO 依据 Google Merchant Center 政策，审计 AI 生成商品图片上的 IPTC `TrainedAlgorithmicMedia` 要求。

## 社区贡献者

v1.9.0 包含了来自 [AI Marketing Hub](https://www.skool.com/ai-marketing-hub) Pro Hub Challenge 的贡献：

| 贡献者 | 贡献内容 |
|------------|-------------|
| **Lutfiya Miller**（获胜者） | 语义聚类引擎 → `seo-cluster` |
| **Florian Schmitz** | SXO 技能 → `seo-sxo` |
| **Dan Colta** | SEO 变化监控 → `seo-drift` |
| **Chris Muller** | 多语言 SEO → `seo-hreflang` 增强 |
| **Matej Marjanovic** | 电商 + DataForSEO 成本配置 → `seo-ecommerce` + 成本护栏 |

完整详情及原始仓库链接见 [CONTRIBUTORS.md](CONTRIBUTORS.md)。

## 许可证

MIT License。详见 [LICENSE](LICENSE)。

## 贡献指南

欢迎贡献。提交 PR 前请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。项目在合入 `main` 分支之前，会对每个 PR 强制执行审计关卡，涵盖清单一致性检查（14 项断言）、测试套件（326 项通过）以及 8 个维度的安全审查。

---

## 作者

由 **[Agrici Daniel](https://agricidaniel.com/about)** 打造，AI 工作流架构师。单人维护，欢迎通过 [Pro Skool 社区](https://www.skool.com/ai-marketing-hub-pro) 参与社区贡献。背景涉及营销自动化、AI 辅助内容工作流，以及面向 Claude Code 的开源工具开发。

- [Blog](https://agricidaniel.com/blog)：AI 营销自动化深度文章
- [AI Marketing Hub（免费）](https://www.skool.com/ai-marketing-hub)：开放社区
- [AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro)：Pro 社区，可提前体验本技能
- [YouTube](https://www.youtube.com/@AgriciDaniel)：教程与演示
- [GitHub](https://github.com/AgriciDaniel)：全部开源工具

---

## 中文版说明

本中文文档（`README.zh-CN.md`）由社区/使用者基于原始英文 [README.md](README.md) 翻译整理，方便中国大陆用户（尤其是跨境电商、独立站运营者）理解和使用本项目，内容遵循原项目的 [MIT License](LICENSE)。如中英文内容存在出入，以英文原版为准；原始 `README.md` 未做任何修改。
