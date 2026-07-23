---
name: seo-content-brief
description: >
  生成有竞争力的 SEO 内容简报（Content Brief），包含分章节字数分配、竞品评分、
  关键词密度指导，以及分页面类型的模板。同时支持全新页面的写作简报和现有页面
  的优化简报。当用户提到"内容简报"、"写一份 brief"、"内容大纲"、"博客简报"、
  "服务页简报"、"给……写个 brief"、"写作提纲"、"内容规划"、"给……做个大纲"，
  或说 "content brief", "write a brief", "content outline", "blog brief",
  "service page brief", "brief for", "writing brief", "content plan",
  "outline for" 时使用本技能。
user-invocable: true
argument-hint: "[url-or-keyword] [page-type]"
license: MIT
metadata:
  author: puneetindersingh
  original_author: puneetindersingh
  version: "1.0.0"
  category: seo
---

# SEO 内容简报生成器

生成有研究依据的内容简报，帮助撰稿人写出能够超越当前排名前列结果的页面。简报
涵盖带差距评分的竞品分析、分章节字数拆解、关键词布局规则，以及按页面类型定制
的模板。

## 处理流程

### 1. 确定简报模式

**优化模式**（提供了现有页面 URL）：
- 抓取现有页面的内容与结构
- 找出已经做得好的地方（予以保留）
- 找出缺失、单薄或过时的章节
- 在大纲中明确区分「保留/加强」与「新增」的章节
- 如果针对性改进就能取胜，不要建议整体重写

**新建模式**（提供了关键词或主题，没有现有页面）：
- 仅将目标站点的首页或站点地图用作了解业务背景的参考
- 从零开始搭建这份新页面的简报
- 聚焦新页面能够填补的竞争差距

### 2. 获取背景信息

- 抓取目标 URL 或首页以了解该业务
- 抓取站点地图，梳理出所有现有页面、分类与服务
- 这些背景信息对下文的「站点相关性规则」至关重要

### 3. 分析 SERP

- 找出目标关键词排名前 5 的页面
- 过滤掉非真正竞品的结果（Wikipedia、Reddit、Pinterest、Amazon、YouTube、政府网站、
  SEO 工具页面、招聘网站、目录站、新闻聚合站、社交平台）。完整名单见
  `references/excluded-domains.md`。
- 对每个真实竞品打分：内容深度（1-10）、排版（1-10）、SEO（1-10）、体验（1-10）
- 识别三类差距：
  - **话题差距：** 竞品完全没有覆盖的子话题
  - **深度差距：** 有覆盖但写得浅
  - **质量差距：** 信息过时、缺少专家视角、排版差
- 计算差距优先级：`影响力 x 竞争优势 / 实施难度`

### 4. 判定搜索意图

- **信息型：** 用户想学习（指南、how-to、定义解释）
- **商业型：** 用户在购买前做研究（对比、评测、"最好的 X"）
- **交易型：** 用户已准备行动（购买、预订、咨询、注册）
- **导航型：** 用户在找特定网站或页面

判断 Google 针对该查询词奖励的 SERP 格式：长文指南、清单体、对比表格、落地页、
FAQ、视频、本地结果包。

### 5. 搭建简报

先套用 `references/page-type-templates.md` 中对应的页面类型模板，再根据竞品差
距与搜索意图做定制化调整。

## 核心规则

### 站点相关性规则

你建议的每一个标题、子话题、关键词和 FAQ，都必须是目标网站基于其实际业务或
产品能够言之有物地写出来的内容。

- 阅读该站点的首页和站点地图，了解它实际提供什么
- 如果竞品的某些章节涉及本站点不提供的内容，不要照搬那套结构
- 每提一条建议前先自问："这个网站真的能兑现这部分内容吗？"如果不能，就去掉它。

### 站点结构覆盖规则

在为枢纽页、总览页、分类页或"类型汇总"页写简报时：
- 大纲必须涵盖站点上所有相关的产品分类、服务或子页面
- 不要臆造网站上不存在的分类，也不要遗漏已经存在的分类
- 每个分类都应作为独立章节出现，并附带内链建议
- 这样能确保该页面真正发挥枢纽作用，链接到所有子页面

对于非枢纽页面（单个服务页、博客文章），可以利用站点结构给出相关内链建议，
但不必强行把每个分类都塞进大纲。

### 输出语言规则

- 输出中绝不提及研究者姓名、框架名称或工具名称（例如不要出现 "Ben Goodey
  method"、"Frase.io formula"、"Princeton GEO"、"Clearscope"、"Backlinko"）
- 这些只是内部的思考工具，不应出现在交付内容中。输出必须读起来像专业、朴实
  的建议
- 面向的读者是企业主或内容撰稿人，而不是 SEO 学术研究者

## 关键词密度与布局

完整规则见 `references/keyword-density.md`。要点摘要：

**主关键词密度：** 占总字数的 0.5% 到 2.0%。
- 超过 2% 需要复核。超过 3% 有关键词堆砌被惩罚的风险。
- 前 1-2 次出现承载的 SEO 权重最大，之后收益递减。
- 以 1,000 字文章、密度 1-2% 计：标题、正文、alt 文本加起来大约共出现 10-20 次。

**主关键词必须出现在：**
1. Title 标签中（靠前位置）
2. H1 标签中（靠前位置）
3. URL slug 中
4. Meta 描述中
5. 首段/前 100 字内
6. 至少一处图片 alt 文本中

**主关键词不需要出现在：**
- 每一个 H2 或 H3 中（只要 H1 覆盖了，子话题自然带出上下文）
- 每一段或每个小节中

**次级关键词：**
- 5-8 个密切相关的支撑词，分布在正文各处
- 10-15 个覆盖相关概念的更宽泛语义词
- 在 H2-H6 副标题中自然使用
- 同义词有助于提升可读性，且不计入关键词密度

**分章节关键词指导：** 针对大纲中的每个章节，注明：
- 标题里应放主关键词还是次级关键词
- 正文是应包含主关键词原词还是变体形式
- 示例："在 H2 中使用次级关键词『structural drafting services』。正文中提及
  一次主关键词。"

**分布原则：** 让主关键词均匀分布，不要前置堆积或集中在某一个章节。

## Meta 标签规则

**Title 标签：**
- 50-60 字符（不少于 50，不超过 60）
- 主关键词在前，品牌名放最后
- 用竖线或短横线隔开品牌名（与站点现有格式保持一致）
- 尽量以结果、数字或具体信息开头

**Meta 描述：**
- 130-150 字符（不少于 130，不超过 150）
- 使用主动语态，围绕标题展开卖点和具体信息
- 以行动号召结尾
- 末尾不要重复品牌名（标题里已经有了）
- 不要使用引号（Google 会在引号处截断）

## 信息增量（不可妥协）

每份简报都必须明确说明：相比当前所有排名页面，这篇内容能带来什么当前市面上
没有的新价值。必须具体：
- 独家数据或原创调研
- 带真实结果的案例研究
- 专家引语或一手经验
- 原创的整合观点或独特框架
- 不能写"更详细"或"排版更好"这种空泛说法

## E-E-A-T 要求

列出这篇内容需要的具体信任信号：
- 与主题相关的作者资质与简介
- 来自权威来源的专家引语或引用
- 带日期的引用研究、数据或统计
- 最后更新日期
- 对于 YMYL 话题（健康、金融、法律、安全）尤其关键

## 内链建议

- 给出 3-5 个具体的内链机会，附锚文本
- 说明该页面是枢纽页（链接到集群页面）还是子页面（链接到支柱页面）
- 利用站点地图中的站点结构找到真实可用的链接目标

## 输出格式

始终按以下结构输出：

```
## Content Brief: [Primary Keyword]

### Search Intent
[Intent type, SERP format rewarded, target audience and knowledge level. 3-4 lines.]

### Competitor Analysis
| # | URL | Key H2 Sections | Est. Words | Score | Main Gap |
|---|-----|-----------------|------------|-------|----------|
| 1 | ... | ...             | ...        | X/40  | ...      |

### Content Gaps and Opportunities
[Bullet list: topic gaps, depth gaps, quality gaps with specifics]

### Winning Outline

**H1:** [H1 with primary keyword]
**URL Slug:** /[slug]
**Target Word Count:** ~[X] words (competitor avg: ~[X] words)

[Full H2/H3 outline with:
- Word count per section
- Content format notes (bullet list, table, definition box, etc.)
- Featured Snippet targets marked with "FS target"
- Per-section keyword guidance]

### Recommended Meta Tags

**Title**
[title, 60 chars max]

**Meta Description**
[description, 150 chars max]

### Unique Angle and Information Gain
[Specific paragraph: what exact new value this piece adds]

### E-E-A-T Requirements
[Bullet list of exact trust signals needed]

### Internal Linking Opportunities
[3-5 suggestions with anchor text and target URL]
```

## 仅大纲模式

当用户要求"只要大纲"或"内容大纲"而非完整简报时，跳过竞品分析表格、内容差距
章节、信息增量章节和 E-E-A-T 章节。仅输出：

```
## Content Outline: [Primary Keyword]

**H1:** [H1 with primary keyword]
**URL Slug:** /[slug]
**Target Word Count:** ~[X] words (competitor avg: ~[X] words)

[Full H2/H3 outline with word counts, format notes, FS targets, keyword guidance, and a 1-2 sentence writing note per section]
```

## DataForSEO 集成（可选）

若 DataForSEO MCP 工具可用，可使用 `serp_google_organic_live_advanced` 获取真实
SERP 数据与竞品分析，`kw_data_google_ads_search_volume` 获取关键词搜索量，
`dataforseo_labs_bulk_keyword_difficulty` 获取难度分数，
`dataforseo_labs_search_intent` 做意图分类，以及
`on_page_content_parsing_live` 提取竞品内容。

## Ahrefs 集成（可选）

若 Ahrefs MCP 工具可用，可使用 `keywords-explorer-overview` 获取关键词搜索量与
难度，`serp-overview` 做 SERP 分析，`site-explorer-organic-keywords` 查看现有
关键词排名，`site-explorer-top-pages` 分析竞品页面表现。

## 错误处理

| 场景 | 处理方式 |
|------|--------|
| 目标 URL 无法访问 | 报告错误，不要臆测页面内容，请用户核实 URL |
| 过滤后没有找到竞品 | 放宽范围，纳入部分匹配的竞品，并在简报中注明该赛道竞争样本稀薄 |
| 未找到站点地图 | 在没有站点结构背景的情况下继续，注明内链建议可能不完整 |
| 未指定页面类型 | 根据关键词意图和 SERP 格式自动判断，在简报中说明识别出的类型 |
| 未指定目标字数 | 以竞品平均字数为基准，并在大纲中注明 |
