---
name: seo-geo
description: >
  为 AI Overviews（原 SGE）、ChatGPT 网页搜索、Perplexity 等 AI 驱动搜索体验优化内容。
  提供生成式引擎优化（Generative Engine Optimization, GEO）分析，涵盖品牌提及信号、AI 爬虫
  可访问性、llms.txt 合规性、段落级可引用性评分，以及平台专属优化建议。当用户提到
  "AI 概述"、"SGE"、"GEO 优化"、"AI 搜索"、"大模型优化"、"Perplexity"、"AI 引用"、
  "ChatGPT 搜索" 或 "AI 可见性" 时使用本技能 — Use when user says "AI Overviews", "SGE",
  "GEO", "AI search", "LLM optimization", "Perplexity", "AI citations",
  "ChatGPT search", or "AI visibility".
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# AI 搜索 / GEO 优化（2026 年 5 月）

## 权威来源：Google 的 AI 优化指南

Google 在 Search Central 官方文档中给出的立场：

> "从 Google 的角度看，为生成式 AI 搜索做优化**本质上仍然是 SEO**。
> AEO 和 GEO 不过是同一件事换了个包装。"

完整解读、误区澄清清单（`llms.txt`、内容切块、AI 改写、提及刷量——均已被
Google 判定为无效手段）以及内容质量的 Who/How/Why 检验法，请阅读
`references/google-ai-optimization-guide.md`。

审计报告应将 GEO 相关发现定位为**应用于 AI 搜索场景的 SEO 基本功**，而不是一门
独立的优化学科。当社区流传的建议与 Google 的权威来源相矛盾时，以 Google 为准，
并在报告中注明这一矛盾点。

## 关键数据

| 指标 | 数值 | 来源 |
|--------|-------|--------|
| AI Overviews 覆盖用户 | 覆盖 200+ 国家，月活 15 亿 | Google |
| AI Overviews 查询覆盖率 | 超过全部查询量的 50% | 行业数据 |
| AI Mode 月活用户 | 超 10 亿（2026 年 5 月超越） | Google |
| AI Mode 使用的模型 | Gemini 3.5 Flash（自 2026 年 I/O 大会起全球默认） | Google |
| AI 引荐会话增长 | 527%（2025 年 1 月至 5 月） | SparkToro |
| ChatGPT 周活用户 | 9 亿 | OpenAI |
| Perplexity 月查询量 | 超 5 亿次 | Perplexity |

## 关键洞察：品牌提及 > 外链

**品牌提及（Brand Mentions）与 AI 可见度的相关性是外链的 3 倍。**
（Ahrefs 于 2025 年 12 月对 75,000 个品牌的研究）

| 信号 | 与 AI 引用的相关性 |
|--------|------------------------------|
| YouTube 提及 | 约 0.737（最强） |
| Reddit 提及 | 高 |
| Wikipedia 收录 | 高 |
| LinkedIn 曝光 | 中等 |
| Domain Rating（外链权重） | 约 0.266（较弱） |

**同时被 ChatGPT 和 Google AI Overviews 引用的域名仅占 11%**，因此针对不同平台
分别优化至关重要。

---

## GEO 分析维度（已更新）

### 1. 可引用性评分（Citability Score，占比 25%）

**AI 引用的最佳段落长度为 134-167 词**。此外，**约 44% 的 AI 引用来自页面前
30% 的内容**（SE Ranking 研究）——应把最具可引用性、自成一体的答案前置，
而不是埋在页面靠后的位置。

**强信号：**
- 句子清晰、可直接引用，带有具体事实/数据
- 独立成段的答案区块（脱离上下文也能被单独摘录）
- 段落开头 40-60 词内即给出直接答案
- 引用有明确来源出处的观点
- 采用「X 是……」或「X 指的是……」句式的定义段
- 独家、别处找不到的数据点

**弱信号：**
- 泛泛而谈、缺乏具体信息
- 只有观点、没有证据支撑
- 结论埋得很深
- 没有具体数据点

### 2. 结构化可读性（占比 20%）

**92% 的 AI Overview 引用来自排名前 10 的页面**，但仍有 47% 来自排名 5 名开外
的页面，说明二者的筛选逻辑并不完全相同。

**强信号：**
- 清晰的 H1→H2→H3 标题层级
- 问句式标题（贴合用户搜索的提问方式）
- 短段落（2-4 句一段）
- 用表格呈现对比类数据
- 用有序/无序列表呈现步骤或多条目内容
- 结构清晰的 FAQ 问答区块

**弱信号：**
- 通篇大段文字、缺乏结构
- 标题层级混乱不统一
- 没有列表或表格
- 信息埋没在段落文字中

### 3. 多模态内容（占比 15%）

带有多模态元素的内容被选中引用的概率**高出 156%**。

**检查要点：**
- 文字配合相关图片
- 视频内容（内嵌或外链）
- 信息图与图表
- 交互元素（计算器、工具类功能）
- 支撑多媒体内容的结构化数据

### 4. 权威性与品牌信号（占比 20%）

**强信号：**
- 作者署名及资质信息
- 发布日期与最后更新日期
- **内容新鲜度（Recency）**——3 个月以内更新的内容被 AI 引用的概率约高 3 倍；
  超过 6 个月未更新的页面会逐渐失去被引用资格（SE Ranking，130 万次引用样本
  研究）。建立一套定期内容刷新机制，是 GEO 优化中投入产出比最高的举措之一。
- 引用一手来源（研究报告、官方文档、原始数据）
- 机构资质与所属背景说明
- 带署名的专家观点引述
- 在 Wikipedia、Wikidata 上有条目
- 在 Reddit、YouTube、LinkedIn 上被提及

**弱信号：**
- 匿名撰稿，无作者信息
- 没有任何日期标注
- 不引用任何来源
- 品牌在其他平台上没有曝光

### 5. 技术可访问性（占比 20%）

**AI 爬虫不会执行 JavaScript。** 服务端渲染（Server-Side Rendering）至关重要。

**检查要点：**
- 内容是服务端渲染（SSR）还是纯客户端渲染
- robots.txt 中是否允许 AI 爬虫抓取
- llms.txt 文件是否存在及其配置情况
- RSL 1.0 许可条款

---

## AI 爬虫识别

在 `robots.txt` 中检查以下 AI 爬虫：

| 爬虫 | 所属公司 | 用途 |
|---------|-------|---------|
| GPTBot | OpenAI | ChatGPT 网页搜索 |
| OAI-SearchBot | OpenAI | OpenAI 搜索功能 |
| ChatGPT-User | OpenAI | ChatGPT 浏览功能 |
| ClaudeBot | Anthropic | Claude 网页功能 |
| PerplexityBot | Perplexity | Perplexity AI 搜索 |
| CCBot | Common Crawl | 训练数据抓取（常被屏蔽） |
| anthropic-ai | Anthropic | Claude 模型训练 |
| Bytespider | 字节跳动 | TikTok/抖音 AI |
| cohere-ai | Cohere | Cohere 模型 |

**建议：** 为提升 AI 搜索可见度，放行 GPTBot、OAI-SearchBot、ClaudeBot、
PerplexityBot；如有需要，可屏蔽 CCBot 及其他训练类爬虫。

---

## llms.txt 标准

关于为何 `/llms.txt` 目前对主流 AI 搜索系统而言并非有效的引用加权因素，
请阅读 `references/llmstxt-evidence.md` 获取一手证据（Mueller、Illyes 的表态，
SE Ranking 对 30 万域名的研究，以及 OtterlyAI 的服务器日志审计）。claude-seo
会在报告中呈现该文件是否存在，但不会将其纳入引用排名权重。

新兴的 **llms.txt** 标准旨在为 AI 爬虫提供结构化的内容导览。

**位置：** `/llms.txt`（域名根目录）

**格式：**
```
# Title of site
> Brief description

## Main sections
- [Page title](url): Description
- [Another page](url): Description

## Optional: Key facts
- Fact 1
- Fact 2
```

**检查要点：**
- `/llms.txt` 是否存在
- 是否有结构化的内容导览
- 是否突出核心页面
- 是否包含联系方式/权威信息

---

## RSL 1.0（Really Simple Licensing）

面向机器可读 AI 授权条款的新标准（2025 年 12 月推出）。

**支持方：** Reddit、Yahoo、Medium、Quora、Cloudflare、Akamai、Creative Commons

**检查要点：** 是否实现了 RSL，以及授权条款是否设置得当。

---

## 平台专属优化

| 平台 | 主要引用来源 | 优化重点 |
|----------|---------------------|-------------------|
| **Google AI Overviews** | 与自然排名高度相关——倾向引用本身排名靠前的页面 | 传统 SEO + 段落级优化 |
| **Google AI Mode**（Gemini 3.5 Flash） | 与排名相关性较弱；引用池更广（Ahrefs 数据显示每次查询约引用 9 个域名） | 独立的内容面：内容新鲜度、实体权威性、排名 5 名开外也能被引用的可引用段落 |
| **ChatGPT** | Wikipedia（47.9%）、Reddit（11.3%） | 实体曝光、权威信息来源 |
| **Perplexity** | Reddit（46.7%）、Wikipedia | 社区验证、讨论区内容 |
| **Bing Copilot** | Bing 索引、权威站点 | Bing SEO、IndexNow |

> **Google 其实有两套引用引擎，而非一套。** AI Mode 和 AI Overviews 大约
> 86% 的情况下会给出相同结论，但引用同一 URL 的比例只有 **13.7%**
> （Ahrefs 研究，540K 查询对样本）。应把二者当作两个独立的内容面来对待：
> 在经典搜索中排名靠前有助于被 AI Overviews 采纳，但 AI Mode 的引用池更广，
> 内容新鲜度和实体权威性的权重超过单纯的排名位置。两者都要评估。

---

## 输出

生成 `GEO-ANALYSIS.md`，包含以下内容：

1. **GEO 就绪度评分：XX/100**
2. **平台细分得分**（Google AIO、ChatGPT、Perplexity 各自的得分）
3. **AI 爬虫访问状态**（哪些爬虫被允许/被屏蔽）
4. **llms.txt 状态**（是否存在、缺失情况、改进建议）
5. **品牌提及分析**（在 Wikipedia、Reddit、YouTube、LinkedIn 上的曝光情况）
6. **段落级可引用性**（识别出的 134-167 词最佳区块）
7. **服务端渲染检查**（JavaScript 依赖情况分析）
8. **影响力最高的 5 项改进建议**
9. **Schema 建议**（提升 AI 可发现性）
10. **内容重排建议**（指出需要重写的具体段落）

---

## 速赢清单（Quick Wins）

1. 在前 60 词内加入「什么是 [主题]？」的定义句
2. 打造 134-167 词、可独立成段的答案区块
3. 加入问句式的 H2/H3 标题
4. 引用带来源出处的具体统计数据
5. 补充发布/更新日期
6. 为作者实现 Person schema
7. 在 robots.txt 中放行关键 AI 爬虫

## 中等投入项

1. 创建 `/llms.txt` 文件
2. 补充作者简介、资质说明及 Wikipedia/LinkedIn 链接
3. 确保核心内容采用服务端渲染
4. 在 Reddit、YouTube 上建立实体曝光
5. 加入带数据支撑的对比表格
6. 实现 FAQ 区块（面向商业站点时用结构化排版，而非 schema）

## 高影响力项

1. 产出原创研究/调研数据（独特可引用性）
2. 为品牌或核心人物建立 Wikipedia 词条
3. 建立 YouTube 频道并积累内容提及
4. 完善全面的实体关联（跨平台 sameAs）
5. 开发独具特色的工具或计算器

## DataForSEO 集成（可选）

如已配置 DataForSEO MCP 工具，可用 `ai_optimization_chat_gpt_scraper` 查看
ChatGPT 网页搜索对目标查询词的实际返回内容（真实 GEO 可见度检测），并结合
`ai_opt_llm_ment_search` 与 `ai_opt_llm_ment_top_domains` 跟踪各 AI 平台上的
提及情况。

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| URL 无法访问（DNS 失败、连接被拒） | 清楚报告错误信息，不要臆测站点内容，建议用户核实 URL 后重试 |
| robots.txt 屏蔽了 AI 爬虫 | 明确列出哪些爬虫被屏蔽、哪些被允许，并给出开放 AI 搜索可见度所需的具体 robots.txt 指令 |
| 未发现 llms.txt | 说明该文件缺失，并根据站点内容结构提供一份可直接使用的 llms.txt 模板 |
| 未检测到结构化数据 | 报告这一缺口，并给出具体的 schema 建议（Article、Organization、Person）以提升 AI 可发现性 |

## FLOW 框架集成

如需借助提示词引导 AI 内容优化，可使用 `/seo flow optimize <url>`——FLOW 框架
中面向优化阶段的 21 条提示词，可与 GEO 的可引用性与结构化分析形成互补，
提供证据驱动的 AI 优化建议。
</content>
