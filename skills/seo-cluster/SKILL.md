---
name: seo-cluster
description: >
  基于 SERP 实际重合度的语义主题聚类（topic clustering），用于内容架构规划。
  依据 Google SERP 的真实重合情况（而非文本相似度）对关键词分组，设计
  hub-and-spoke（枢纽-辐射式）内容集群及内部链接矩阵，并生成交互式可视化图表。
  若已安装 claude-blog，还可选择自动执行内容创作。
  Use when user says "topic cluster", "content cluster", "semantic clustering",
  "pillar page", "hub and spoke", "content architecture", "keyword grouping",
  or "cluster plan".
user-invocable: true
argument-hint: "<seed-keyword or url>"
license: MIT
metadata:
  author: AgriciDaniel
  original_author: "Lutfiya Miller (Pro Hub Challenge Winner)"
  version: "2.2.0"
  category: seo
---

# 语义主题聚类（Semantic Topic Clustering）（v1.9.0）

基于 SERP 重合度驱动的关键词聚类，用于内容架构规划。依据 Google 的实际排名情况（即共享的 Top 10 结果）对关键词分组，而非按文本相似度分组。设计带内部链接矩阵的 hub-and-spoke（枢纽-辐射式）内容集群，并生成交互式集群地图可视化。

**脚本：** 位于插件根目录的 `scripts/` 目录下。

---

## 快速参考

| 命令 | 作用 |
|---------|-------------|
| `/seo cluster plan <seed-keyword>` | 完整规划流程：扩展、聚类、架构设计、可视化 |
| `/seo cluster plan --from strategy` | 从已有的 `/seo plan` 输出导入 |
| `/seo cluster execute` | 执行计划：通过 claude-blog 创建内容，或输出内容简报 |
| `/seo cluster map` | 重新生成交互式集群可视化图 |

---

## 规划流程

### 第一步：种子关键词扩展

使用 WebSearch 将种子关键词扩展为 30-50 个变体：

1. **相关搜索** — 搜索种子词，提取"相关搜索"和"用户还搜索了"内容
2. **People Also Ask（PAA，用户还想问）** — 从 SERP 结果中提取所有 PAA 问题
3. **长尾修饰词** — 附加常见修饰词："best"、"how to"、"vs"、"for beginners"、"tools"、"examples"、"guide"、"template"、"mistakes"、"checklist"
4. **疑问词挖掘** — 生成 who/what/when/where/why/how 各类变体
5. **意图修饰词** — 增加商业类修饰词："pricing"、"review"、"alternative"、"comparison"、"free"、"top"

**去重：** 对变体做归一化处理（小写、去除冠词），去除完全重复项。目标：30-50 个不重复的关键词变体。若不足 30 个，以排名靠前的 PAA 问题为种子再做一轮扩展。

### 第二步：SERP 重合度聚类

这是本技能的核心差异化能力。完整算法参见 `references/serp-overlap-methodology.md`。

**流程：**
1. 先按初步的意图判断给关键词分组（减少两两对比的次数）
2. 对同组内的每一对候选关键词，用 WebSearch 分别搜索
3. 统计前 10 条自然搜索结果中的重合 URL 数量（忽略广告、精选摘要、PAA）
4. 应用以下阈值：

| 重合结果数 | 关系判定 | 处理方式 |
|---------------|-------------|--------|
| 7-10 | 同一篇文章 | 合并为单一目标页面 |
| 4-6 | 同一集群 | 归入同一辐射（spoke）集群 |
| 2-3 | 需互相链接 | 放入相邻集群，添加交叉链接 |
| 0-1 | 各自独立 | 分配到不同集群或排除 |

**优化建议：** 40 个关键词时，全量两两对比需 780 次比较。可采取以下方式简化：
- 先按意图预分组（4 组，每组约 10 个 = 4 x 45 = 180 次比较）
- 只对跨组边界的关键词做交叉核对
- 若两个关键词都是同一核心词的长尾变体，可跳过比较（默认视为同一集群）

**DataForSEO 集成：** 若 DataForSEO MCP 可用，用 `serp_organic_live_advanced` 替代 WebSearch 获取 SERP 数据。每批处理前先运行 `python3 scripts/dataforseo_costs.py check serp_organic_live_advanced --count N`。若返回 `"status": "needs_approval"`，展示费用估算并征询用户意见；若返回 `"status": "blocked"`，回退使用 WebSearch。

### 第三步：意图分类

将每个关键词归入以下四种意图类别之一：

| 意图 | 信号词 | 是否纳入集群 |
|--------|---------|---------------------|
| 信息型（Informational） | how, what, why, guide, tutorial, learn | 是 |
| 商业型（Commercial） | best, top, review, comparison, vs, alternative | 是 |
| 交易型（Transactional） | buy, price, discount, coupon, order, sign up | 是 |
| 导航型（Navigational） | 品牌名、特定产品名、login | 否（排除） |

聚类时移除导航型关键词。对临界情况标记出来供人工复核。关键词可能存在混合意图（例如 "best CRM software" 兼具商业型和信息型），此时按主导意图分类。

### 第四步：Hub-and-Spoke（枢纽-辐射式）架构

完整规范参见 `references/hub-spoke-architecture.md`。

**设计集群结构：**

1. **选定枢纽关键词（pillar keyword）** — 搜索量最高、意图最宽泛、与其他关键词的 SERP 重合度最高
2. **将辐射词（spoke）分组为多个集群** — 每个集群对应一个子话题领域（每个枢纽下 2-5 个集群）
3. **为每个集群分配文章** — 每个集群包含 2-4 篇辐射文章
4. **为每篇文章选择模板** — 依据意图分类：

| 意图模式 | 可选模板 |
|---------------|-----------------|
| 信息型（宽泛） | ultimate-guide（终极指南） |
| 信息型（how） | how-to（操作指南） |
| 信息型（列表） | listicle（清单体） |
| 信息型（概念） | explainer（概念解析） |
| 商业型（对比） | comparison（对比） |
| 商业型（评测） | review（评测） |
| 商业型（排行） | best-of（榜单） |
| 交易型 | landing-page（落地页） |

5. **设定字数目标：**
   - 枢纽页面：2500-4000 字
   - 辐射文章：1200-1800 字

6. **同质化检测（Cannibalization check）** — 不允许两篇文章共享同一主关键词。若 SERP 重合度达到 7 以上，将这些关键词合并进同一篇覆盖两者的文章。

### 第五步：内部链接矩阵

设计双向链接结构：

| 链接类型 | 方向 | 要求 |
|-----------|-----------|-------------|
| 辐射 → 枢纽 | spoke -> pillar | 强制（每篇辐射文章都需要） |
| 枢纽 → 辐射 | pillar -> spoke | 强制（每篇辐射文章都需要） |
| 辐射 ↔ 辐射（同集群内） | spoke <-> spoke | 每篇 2-3 条链接 |
| 跨集群 | spoke -> spoke（其他集群） | 每篇 0-1 条链接 |

**规则：**
- 每篇文章至少需要 3 条入站内部链接
- 不允许孤立页面（每篇文章从枢纽页出发，2 次点击内必须可达）
- 锚文本必须使用目标关键词或其近义变体（不能用"点击这里"之类）
- 链接需嵌入正文内容中，而非仅出现在导航栏/侧边栏

将链接矩阵生成为 JSON 邻接表：
```json
{
  "links": [
    { "from": "pillar", "to": "cluster-0-post-0", "type": "mandatory", "anchor": "keyword" },
    { "from": "cluster-0-post-0", "to": "pillar", "type": "mandatory", "anchor": "keyword" }
  ]
}
```

### 第六步：交互式集群地图

使用 `templates/cluster-map.html` 模板生成 `cluster-map.html`。

1. 读取模板文件
2. 根据集群规划构建 `CLUSTER_DATA` JSON 对象：
   ```javascript
   {
     pillar: { title, keyword, volume, template, wordCount, url },
     clusters: [{ name, color, posts: [{ title, keyword, volume, template, wordCount, url, status }] }],
     links: [{ from, to, type }],
     meta: { totalPosts, totalClusters, totalLinks, estimatedWords }
   }
   ```
3. 将模板中的 `CLUSTER_DATA` 占位符替换为实际 JSON 数据
4. 将生成好的 HTML 文件写入输出目录
5. 提示用户："在浏览器中打开 `cluster-map.html` 即可查看交互式集群地图。"

---

## 策略导入

当以 `--from strategy` 方式调用时：

1. 在当前目录下查找最近一次 `/seo plan` 的输出（匹配 `*SEO*Plan*`、`*strategy*`、`*content-strategy*` 等文件名）
2. 解析 markdown 表格中的关键词、页面类型、内容枢纽、URL 结构
3. 校验提取到的数据：检查重复项、缺失关键词、不完整条目
4. 用 SERP 数据丰富信息：对提取的关键词运行 SERP 重合度分析
5. 以导入的关键词作为初始集合构建集群方案（跳过第一步）

若未找到策略文件，提示用户："当前目录未找到已有的 SEO plan。请先运行 `/seo plan`，或直接提供一个种子关键词以开始全新聚类。"

---

## 执行流程

调用 `/seo cluster execute` 时：

### 检测 claude-blog 是否已安装

```
检测项：~/.claude/skills/blog/SKILL.md 是否存在？
```

**若已安装 claude-blog：**

1. 完整算法参见 `references/execution-workflow.md`
2. 从当前目录读取 `cluster-plan.json`
3. 检查断点续跑状态：扫描输出目录中已写好的文章
4. 按优先级顺序执行：先枢纽文章，再按搜索量从高到低执行辐射文章
5. 针对每篇文章，携带以下集群上下文调用 `blog-write` 技能：
   - 集群角色（枢纽或辐射）
   - 在集群中的位置（集群索引、文章索引）
   - 目标关键词与次要关键词
   - 模板类型与字数目标
   - 需要包含的内部链接（附锚文本）
   - 需要从后续文章接收的链接（占位标记）
6. 每篇文章写完后，扫描此前文章中的回链占位标记，注入新文章的 URL
7. 全部文章写完后，生成集群评分卡

**若未安装 claude-blog：**

1. 为集群规划中的每篇文章生成详细内容简报
2. 每份简报包含：
   - 标题与元描述
   - 主关键词与次要关键词
   - 模板类型与建议结构（H2/H3 大纲）
   - 字数目标
   - 需包含的内部链接（附锚文本）
   - 需覆盖的关键要点
   - 需做出差异化的竞品页面
3. 将简报以独立 markdown 文件的形式写入 `cluster-briefs/` 目录
4. 提示用户："安装 [claude-blog](https://github.com/AgriciDaniel/claude-blog) 可实现内容自动创建。简报已保存至 `cluster-briefs/`。"

---

## 集群评分卡

执行完成后的质量报告。在 `/seo cluster execute` 后自动运行，也可通过分析输出目录按需触发。

| 指标 | 目标值 | 度量方式 |
|--------|--------|-------------|
| 覆盖率 | 100% | 已写文章数 / 计划文章数 |
| 链接密度 | 每篇 3+ | 统计每篇文章的内部链接数 |
| 孤立页面 | 0 | 入站链接数 < 1 的文章数 |
| 同质化冲突 | 0 处冲突 | 检查是否存在重复主关键词 |
| 图片数量 | 每篇 1+ | 至少包含一张图片的文章数 |
| 枢纽链接 | 100% | 所有辐射文章均与枢纽互链 |
| 交叉链接 | 80%+ | 建议的辐射间链接实现比例 |
| 内容缺口 | 0 | 被跳过或未完成的计划文章数 |

---

## 地图重新生成

调用 `/seo cluster map` 时：

1. 从当前目录读取 `cluster-plan.json`
2. 扫描输出目录并更新文章状态（已计划 vs 已写完）
3. 用更新后的状态重新生成 `cluster-map.html`
4. 报告：已写文章数 vs 计划文章数、链接完成百分比

---

## 输出文件

所有输出均写入当前工作目录：

| 文件 | 说明 |
|------|------|
| `cluster-plan.json` | 机器可读的完整集群方案数据 |
| `cluster-plan.md` | 人类可读的集群方案摘要 |
| `cluster-map.html` | 交互式 SVG 可视化图 |
| `cluster-briefs/` | 内容简报（未安装 claude-blog 时生成） |
| `cluster-scorecard.md` | 执行完成后的质量报告 |

---

## 跨技能协同

| 技能 | 关系 |
|-------|-------------|
| `seo-plan` | 导入来源：策略导入功能读取 seo-plan 的输出 |
| `seo-content` | 质量校验：对生成内容做 E-E-A-T 校验 |
| `seo-schema` | Schema 标记：为集群页面生成 Article、BreadcrumbList、ItemList |
| `seo-dataforseo` | 数据来源：当 DataForSEO MCP 可用时提供 SERP 数据 |
| `seo-google` | 报告生成：为集群方案和评分卡生成 PDF 报告 |

集群规划或执行完成后，主动提示："生成一份 PDF 报告？使用 `/seo google report`"

---

## 错误处理

| 错误 | 原因 | 解决方式 |
|-------|-------|--------|
| "No seed keyword provided"（未提供种子关键词） | 缺少参数 | 提示用户提供种子关键词或 URL |
| "Insufficient keyword variants"（关键词变体不足） | 扩展结果少于 15 个 | 以 PAA 问题为种子再执行一轮扩展 |
| "SERP data unavailable"（SERP 数据不可用） | WebSearch 与 DataForSEO 均失败 | 30 秒后重试；若持续失败，改用仅按意图聚类并给出警告 |
| "No strategy file found"（未找到策略文件） | 使用了 `--from strategy` 但无既有方案 | 提示用户先运行 `/seo plan` |
| "cluster-plan.json not found"（未找到 cluster-plan.json） | 未规划即执行 | 提示用户先运行 `/seo cluster plan` |
| "claude-blog not installed"（未安装 claude-blog） | 在无 blog 技能的情况下尝试执行 | 改为生成内容简报；建议安装 claude-blog |
| "DataForSEO budget exceeded"（DataForSEO 预算超限） | 费用检测返回 "blocked" | 回退使用 WebSearch，并告知用户 |
| "Duplicate primary keywords"（主关键词重复） | 检测到同质化冲突 | 合并受影响的文章，或重新分配关键词 |
| "Orphan page detected"（检测到孤立页面） | 文章缺少入站链接 | 从最邻近的集群同级文章添加链接 |
| "Resume state corrupted"（续跑状态损坏） | 方案与输出不匹配 | 通过扫描输出目录重建状态 |

---

## 安全性

- 所有 URL 均通过 `python3 scripts/render_page.py --mode auto` 抓取（具备 SPA 感知能力的 SSRF 防护，基于 `url_safety`）
- 不存储或传输任何凭证
- 输出文件不包含任何个人信息或 API 密钥
- 每次调用 API 前都会执行 DataForSEO 费用检测

## FLOW 框架集成

如需借助提示词完成关键词研究与内容缺口分析，可使用 `/seo flow find [url|topic]` —— FLOW 框架的 5 个 find 阶段提示词，可与 SERP 重合度聚类方法形成互补，提供结构化的选题发现流程。
</content>
