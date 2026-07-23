---
name: seo-sxo
description: >
  搜索体验优化（Search Experience Optimization，SXO）：反向拆解 Google SERP，
  识别页面类型与搜索意图不匹配的问题，从搜索意图信号中推导用户故事，并从多个
  用户角色（persona）视角为页面打分。通过分析 Google 针对每个关键词真正奖励
  什么内容，找出「明明优化到位却排名上不去」的根本原因。当用户提到"SXO"、
  "搜索体验优化"、"页面类型不匹配"、"SERP 分析"、"用户故事"、"角色打分"、
  "为什么排名上不去"、"意图不匹配"、"线框图"，或说 "SXO", "search experience",
  "page type mismatch", "SERP analysis", "user story", "persona scoring",
  "why isn't my page ranking", "intent mismatch", "wireframe" 时使用本技能。
user-invocable: true
argument-hint: "<url> [keyword]"
license: MIT
metadata:
  author: AgriciDaniel
  original_author: "Florian Schmitz (Pro Hub Challenge)"
  version: "2.2.0"
  category: seo
---

# 搜索体验优化（SXO）

SXO 弥合了 SEO（Google 奖励什么）与 UX（用户需要什么）之间的鸿沟。传统的 SEO
审查只检查技术健康度，而 SXO 追问的是："基于 Google 在 SERP 中实际奖励的内容，
这个页面配不配对这个关键词有排名？"

## 核心洞察

一个页面即便技术 SEO 得分高达 95/100，也可能因为它是这个关键词的**错误页面类型**
而排不上去。如果 Google 针对你的关键词展示了 8 个产品页和 2 个对比页，你的博客
文章无论优化得多好，都很难冲进去。

## 命令

| 命令 | 用途 |
|---------|---------|
| `/seo sxo <url>` | 完整 SXO 分析（自动从页面识别关键词） |
| `/seo sxo <url> <keyword>` | 针对指定关键词的完整 SXO 分析 |
| `/seo sxo wireframe <url>` | 生成带具体占位内容的 IST/SOLL 线框图 |
| `/seo sxo personas <url>` | 仅执行角色打分（跳过 SERP 分析） |

## 执行流程

### 第 1 步：目标获取

1. 通过 `scripts/render_page.py --mode auto` 抓取目标 URL（支持 SPA 感知，且具备 SSRF 防护）
2. 使用 `scripts/parse_html.py` 解析，提取：标题、H1、meta 描述、
   标题层级结构、字数、schema 标记、CTA、媒体元素
3. 若未提供关键词，从 title 标签与 H1 的重叠内容中提取主关键词
4. 继续之前先校验关键词非空

### 第 2 步：SERP 反向分析

阅读 `references/page-type-taxonomy.md` 了解分类规则。

1. 针对目标关键词做 Google 搜索（WebSearch）
2. 对自然搜索结果前 10 名中的每一条，记录：
   - URL 及域名权威度等级（品牌 / 细分领域权威站 / 未知）
   - 页面类型（依据分类体系判定）
   - 内容形式（长文、清单体、how-to、对比、工具、视频）
   - 字数估算（基于摘要长度与页面结构）
   - 出现的 schema 类型（来自 SERP 特性：评分、FAQ、HowTo）
   - 媒体信号（视频轮播、图片包、缩略图出现情况）
3. 记录 SERP 中出现的特性：
   - 精选摘要（Featured Snippet，段落 / 列表 / 表格 / 视频形式）
   - People Also Ask（提取所有可见问题）
   - 广告（顶部与底部——统计数量并分析广告文案主题）
   - 相关搜索（全部提取）
   - 知识图谱 / 本地结果包 / 购物结果
   - AI Overview 的出现情况及信息来源类型
4. 计算 SERP 共识：
   - 主导页面类型（占比 >60% 为强共识，40-60% 为混合型，<40% 为分散型）
   - 内容深度预期（平均字数区间）
   - schema 预期（最常见的结构化数据类型）
   - 媒体预期（是否必须有视频？图片是否关键？）

### 第 3 步：页面类型不匹配检测

这是 SXO 的核心洞察。将目标页面类型与 SERP 共识进行对比。

**不匹配的严重程度分级：**

| 目标页面类型 | SERP 期望类型 | 严重程度 | 建议 |
|-------------|-------------|----------|----------------|
| 博客文章 | 产品页 | 严重 | 创建专门的产品页 |
| 博客文章 | 对比内容 | 高 | 改造为带对比矩阵的对比页 |
| 产品页 | 信息型内容 | 高 | 增加教育性内容层 |
| 落地页 | 工具/计算器 | 高 | 构建交互式工具组件 |
| 服务页 | 本地结果 | 中 | 增加位置信号与本地 schema |
| 类型匹配 | - | 一致 | 聚焦内容深度与用户体验 |

**分类规则：**
- 依据 `references/page-type-taxonomy.md` 对目标页面进行分类
- 使用同一套分类体系对每个 SERP 结果进行分类
- 若目标类型与 SERP 主导类型不同，则标记为不匹配
- 若 SERP 呈分散型（没有主导类型），记录这是差异化的机会

### 第 4 步：用户故事推导

阅读 `references/user-story-framework.md` 了解完整框架。

从 SERP 信号中推导用户故事：

1. **PAA 问题**揭示知识盲区与顾虑
2. **广告文案主题**揭示商业触发点与价值主张
3. **相关搜索**揭示搜索路径（用户在此之前/之后会搜什么）
4. **精选摘要格式**揭示预期的答案结构
5. **AI Overview** 揭示 Google 认定的权威答案

针对每组信号簇，生成一条用户故事：
```
As a [persona derived from signal],
I want to [goal derived from query intent],
because [emotional driver from ad copy / PAA tone],
but I'm blocked by [barrier derived from PAA questions / related searches].
```

生成 3-5 条覆盖主要意图角度的用户故事。

### 第 5 步：差距分析

从 7 个维度将目标页面与 SERP 预期进行对比：

| 维度 | 对比内容 | 分值 |
|-----------|----------------|-------|
| 页面类型 | 目标类型 vs SERP 主导类型 | 0-15 |
| 内容深度 | 字数、标题层级深度、话题覆盖度 | 0-15 |
| UX 信号 | CTA 清晰度、首屏内容、移动端布局 | 0-15 |
| Schema 标记 | 现有 vs 预期的结构化数据类型 | 0-15 |
| 媒体丰富度 | 图片、视频、交互元素相对 SERP 常态的水平 | 0-15 |
| 权威信号 | E-E-A-T 标记、社会认同、资质证明 | 0-15 |
| 时效性 | 最近更新时间、日期信号、内容新鲜度 | 0-10 |

**总分：0-100 SXO 差距分**（分数越低差距越大，分数越高说明与 SERP 预期越契合）

### 第 6 步：角色打分（Persona-Based Scoring）

阅读 `references/persona-scoring.md` 了解方法论。

1. 从 SERP 意图信号中提炼 4-7 个用户角色（persona）：
   - 按主题对 PAA 问题分组
   - 按目标受众细分广告文案
   - 将相关搜索映射到搜索旅程的各个阶段
2. 针对每个角色，从 4 个维度为目标页面打分（每项 25 分）：
   - **相关性（Relevance）**：页面是否解决了该角色的需求？
   - **清晰度（Clarity）**：该角色能否在 10 秒内找到答案？
   - **信任度（Trust）**：是否有足够的信任信号让该角色安心？
   - **行动指引（Action）**：该角色是否有清晰的下一步？
3. 输出角色卡片，附分值及具体改进建议
4. 建议按最弱角色优先排序（机会最大的先处理）

### 第 7 步：线框图生成（可选）

仅在调用 `/seo sxo wireframe` 时执行。

阅读 `references/wireframe-templates.md` 了解模板。

1. 基于解析出的页面结构生成 IST（现状）线框图
2. 基于以下内容生成 SOLL（目标状态）线框图：
   - SERP 共识页面类型
   - 差距分析发现
   - 角色打分中的薄弱点
3. 使用极具体的占位内容：
   - 不要写："这里加一个 CTA"
   - 应该写："在首屏下方加一个带年付节省徽章的定价 CTA，链接到 /pricing#enterprise"
4. 以带注释的语义化 HTML 章节大纲形式输出

## DataForSEO 集成

若 DataForSEO MCP 工具可用：

1. **调用任何 API 前**，先做成本预估并与用户确认
2. 使用 `google_organic_serp` 获取精确的 SERP 数据（排名、特性、摘要）
3. 使用 `keyword_data` 获取搜索量与竞争度指标
4. 若 DataForSEO 不可用则回退到 WebSearch——并在输出中注明精度有所下降

## SXO 分数 vs SEO 健康分

SXO 分数与主 SEO 健康分是**相互独立**的。

- SEO 健康分 = 技术合规性（可爬取性、速度、schema 等）
- SXO 差距分 = 页面与 SERP 预期之间的契合度
- 一个页面可能是 95 分 SEO + 30 分 SXO——技术层面完美，但战略方向跑偏
- 两个分数若都可用，应一并呈现

## 跨技能引用

| 发现问题 | 交由处理 |
|---------|-------------|
| 角色打分中发现 E-E-A-T 缺口 | `/seo content` 做深度 E-E-A-T 审查 |
| 缺少 schema 类型 | `/seo schema` 生成对应标记 |
| SERP 中检测到本地意图 | `/seo local` 做 GBP 分析 |
| 内容深度存在差距 | `/seo page` 做深度页面分析 |
| 抓取时发现技术问题 | `/seo technical` 做完整审查 |
| 图片/媒体存在缺口 | `/seo images` 做优化分析 |

## 输出格式

### 完整 SXO 分析

```
## SXO Analysis: [URL]
### Target Keyword: [keyword]

### 1. SERP Landscape
- Dominant page type: [type] ([confidence]% consensus)
- SERP features: [list]
- Content depth norm: [word count range]
- Schema expectation: [types]

### 2. Page-Type Alignment
- Your page type: [type]
- SERP expects: [type]
- Verdict: [ALIGNED | MISMATCH (severity)]
- Impact: [explanation]

### 3. User Stories (derived from SERP signals)
[3-5 user stories with source signals]

### 4. Gap Analysis (SXO Score: XX/100)
[7-dimension breakdown table]

### 5. Persona Scores
[4-7 persona cards with 4-dimension scores]

### 6. Priority Actions
[Ranked list: fix mismatch first, then weakest persona gaps]

### 7. Limitations
[What could not be assessed, data source notes]
```

## 错误处理

| 错误 | 处理方式 |
|-------|--------|
| URL 抓取失败 | 报告错误，建议检查 URL 可访问性 |
| 未提供或未识别出关键词 | 请用户提供目标关键词 |
| WebSearch 返回结果少于 5 条 | 用现有数据继续分析，并注明样本量有限 |
| SERP 没有自然搜索结果（全是广告） | 注明这是高商业化 SERP，仅分析广告文案 |
| 目标页面为 JavaScript 渲染 | 注明该限制，使用可获取到的 HTML 内容 |
| DataForSEO 成本超过阈值 | 回退到 WebSearch，并通知用户 |

## 质量检查清单

交付结果前请确认：
- [ ] 目标 URL 已通过 `scripts/render_page.py --mode auto` 抓取（而非直接用 curl/fetch）
- [ ] 页面类型分类使用了参考文件中的分类体系
- [ ] 已分析至少 5 条 SERP 结果
- [ ] 用户故事引用了具体的 SERP 信号作为依据
- [ ] 角色打分包含具体的改进建议
- [ ] SXO 分数已明确标注为独立于 SEO 健康分
- [ ] 已包含诚实、完整的「局限性」章节
- [ ] 已在相关处给出跨技能建议
