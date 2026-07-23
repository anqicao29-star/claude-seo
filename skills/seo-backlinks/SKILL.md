---
name: seo-backlinks
description: "外链画像分析：引荐域名、锚文本分布、垃圾链接检测、竞品差距分析。支持免费 API（Moz、Bing Webmaster、Common Crawl）及 DataForSEO 扩展。当用户提到 backlinks、link profile、referring domains、anchor text、toxic links、link gap、link building、disavow 或 backlink audit 时使用本技能。Use when user says backlinks, link profile, referring domains, anchor text, toxic links, link gap, link building, disavow, or backlink audit."
user-invocable: true
argument-hint: "<url>"
license: MIT
compatibility: "Free: Common Crawl + verify always available. Optional: Moz API, Bing Webmaster (free signup). Premium: DataForSEO extension."
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 外链画像分析

## 数据源检测

分析前先检测可用的数据源：

1. **DataForSEO MCP**（付费）：检查 `dataforseo_backlinks_summary` 工具是否可用
2. **Moz API**（免费注册）：`python3 scripts/backlinks_auth.py --check moz --json`
3. **Bing Webmaster**（免费注册）：`python3 scripts/backlinks_auth.py --check bing --json`
4. **Common Crawl**（始终可用）：带 PageRank 的域名级链接图谱
5. **验证爬虫（Verification Crawler）**（始终可用）：核实已知外链是否仍然存在

运行 `python3 scripts/backlinks_auth.py --check --json` 可一次性检测所有数据源。

若除「始终可用」层级外未配置任何数据源：
- 仍应基于 Common Crawl 的域名指标产出报告
- 建议用户：「运行 `/seo backlinks setup` 添加免费的 Moz 和 Bing API 密钥以获取更丰富的数据」

## 快速参考

| 命令 | 用途 |
|---------|-------------|
| `/seo backlinks <url>` | 完整外链画像分析（使用所有可用数据源） |
| `/seo backlinks gap <url1> <url2>` | 竞品外链差距分析 |
| `/seo backlinks toxic <url>` | 垃圾链接检测与拒绝收录（disavow）建议 |
| `/seo backlinks new <url>` | 新增与流失的外链（仅 DataForSEO） |
| `/seo backlinks verify <url> --links <file>` | 核实已知外链是否仍然存在 |
| `/seo backlinks setup` | 展示免费外链 API 的配置说明 |

## 分析框架

按下方顺序产出全部 7 个章节。每个章节均按优先级列出数据来源。

### 1. 画像概览

**DataForSEO：** `dataforseo_backlinks_summary` → 外链总数、引荐域名数、域名评级、Follow 链接占比、趋势变化。

**Moz API：** `python3 scripts/moz_api.py metrics <url> --json` → Domain Authority、Page Authority、垃圾分数（Spam Score）、引荐根域名数、外部链接数。

**Common Crawl：** `python3 scripts/commoncrawl_graph.py <domain> --json` → 入度（引荐域名数量）、PageRank、调和中心性（harmonic centrality）。

**评分标准：**

| 指标 | 良好 | 警告 | 严重 |
|--------|------|---------|----------|
| 引荐域名数 | >100 | 20-100 | <20 |
| Follow 链接占比 | >60% | 40-60% | <40% |
| 域名多样性 | 无单一域名占比超过 5% | 有域名占比超过 10% | 有域名占比超过 25% |
| 趋势 | 增长或稳定 | 缓慢下滑 | 快速下滑（单季度降幅 >20%） |

### 2. 锚文本分布

**DataForSEO：** `dataforseo_backlinks_anchors`

**Moz API：** `python3 scripts/moz_api.py anchors <url> --json`

**Bing Webmaster：** `python3 scripts/bing_webmaster.py links <url> --json`（从链接详情中提取锚文本）

**健康分布基准：**

| 锚文本类型 | 目标区间 | 过度优化信号 |
|-------------|-------------|-------------------------|
| 品牌词（公司名/域名） | 30-50% | <15% |
| URL / 裸链接 | 15-25% | 不适用 |
| 泛化词（"click here"、"learn more"） | 10-20% | 不适用 |
| 精确匹配关键词 | 3-10% | >15% |
| 部分匹配关键词 | 5-15% | >25% |
| 长尾 / 自然锚文本 | 5-15% | 不适用 |

若精确匹配锚文本占比超过 15%，需标记——这是 Google Penguin 算法的风险信号。

### 3. 引荐域名质量

**DataForSEO：** `dataforseo_backlinks_referring_domains`

**Moz API：** `python3 scripts/moz_api.py domains <url> --json` → 带 DA 评分的域名列表

**Common Crawl：** `python3 scripts/commoncrawl_graph.py <domain> --json` → 主要引荐域名（域名级别，无权威度评分）

分析要点：
- **TLD 分布**：.edu、.gov、.org 属于高权威后缀；.xyz、.info 过多则属于低质量信号
- **国家分布**：应与目标市场匹配。若 80% 以上来自不相关国家/地区，属于 PBN（私有博客网络）信号
- **域名权重分布**：健康的外链画像应覆盖各个权威层级
- **各域名 Follow/Nofollow 比例**：仅有 Nofollow 链接的站点，SEO 价值有限

### 4. 垃圾链接检测

**DataForSEO：** `dataforseo_backlinks_bulk_spam_score` + 参考文档中的垃圾模式库

**Moz API：** `python3 scripts/moz_api.py metrics <url> --json` 中的垃圾分数（1-17% 量表，>11% 为高风险）

**验证爬虫：** `python3 scripts/verify_backlinks.py --target <url> --links <file> --json`（核实可疑链接是否仍然存在）

**高风险信号（需立即标记）：**
- 来自已知 PBN（私有博客网络）域名的链接
- 非自然的锚文本模式（某域名 100% 采用精确匹配锚文本）
- 来自被处罚或已被移除索引的域名的链接
- 大量目录提交（50+ 条目录链接）
- 链接农场（单页出站链接达 1 万+ 的站点）
- 付费链接特征（某域名所有页面的页脚/侧栏均出现相同链接）

**中风险信号（需人工复核）：**
- 来自不相关垂直领域的链接
- 互换链接模式
- 来自低质内容页面（<100 词）的链接
- 单一域名链接过多（同一域名贡献 50+ 条外链）

关于完整的 30 种垃圾链接模式及拒绝收录（disavow）判定标准，请阅读
`references/backlink-quality.md`。

### 5. 外链排名靠前的页面

**DataForSEO：** `dataforseo_backlinks_backlinks`，target type 设为 "page"

**Moz API：** `python3 scripts/moz_api.py pages <domain> --json`

需要找出：
- 哪些页面吸引的外链最多
- 拥有高权威度链接的页面（引链磁石）
- 零外链的页面（内链优化机会）
- 带有外链的 404 页面（可通过重定向找回链接权重的机会）

### 6. 竞品差距分析

**DataForSEO：** 分别对两个域名调用 `dataforseo_backlinks_referring_domains` 后对比

**Bing Webmaster（独家能力！）：** `python3 scripts/bing_webmaster.py compare <url1> <url2> --json` —— 唯一自带竞品对比功能的免费工具

**Moz API：** 通过 `python3 scripts/moz_api.py metrics <url> --json` 分别获取各域名的 DA/PA 后对比

输出内容：
- 链接指向竞品但未指向目标站点的域名 = 建站机会
- 同时链接到双方的域名 = 已建立的合作关系验证
- 仅链接到目标站点的域名 = 竞争优势
- Top 20 建链机会及其域名权威度

### 7. 新增与流失的外链

**仅限 DataForSEO：** `dataforseo_backlinks_backlinks`，配合日期过滤查看 30/60/90 天变化

**验证爬虫：** 对已知链接，用 `python3 scripts/verify_backlinks.py` 核实当前状态

**说明：** 免费数据源无法追踪链接随时间的新增/流失情况。若在未配置 DataForSEO
的情况下被要求提供该章节，需告知用户：「外链变化速度追踪需要 DataForSEO 扩展。
免费数据源仅能提供某一时间点的快照。」

**风险信号：**
- 新增链接突然激增（可能是负面 SEO 攻击）
- 大量链接突然流失（站点被处罚或内容被下架）
- 链接增速连续 3 个月以上下滑（内容不再具备吸引外链的能力）

## 外链健康分

计算 0-100 分。混合使用多个数据源时，按置信度加权：

| 因素 | 权重 | 数据来源（按优先级） | 置信度 |
|--------|--------|---------------------------|------------|
| 引荐域名数量 | 20% | DataForSEO > Moz > CC 入度 | 1.0 / 0.85 / 0.50 |
| 域名质量分布 | 20% | DataForSEO > Moz DA 分布 | 1.0 / 0.85 |
| 锚文本自然度 | 15% | DataForSEO > Moz > Bing 锚文本 | 1.0 / 0.85 / 0.70 |
| 垃圾链接占比 | 20% | DataForSEO > Moz 垃圾分数 | 1.0 / 0.85 |
| 链接增速趋势 | 10% | 仅 DataForSEO | 1.0 |
| Follow/Nofollow 比例 | 5% | DataForSEO > Bing 详情 | 1.0 / 0.70 |
| 地域相关性 | 10% | DataForSEO > Bing 国家数据 | 1.0 / 0.70 |

**数据充分性门槛：** 统计上述 7 个因素中有数据支撑的项数。
- **4 项及以上有数据：** 产出 0-100 的数值评分（缺失权重按比例重新分配）
- **不足 4 项：** 不产出数值评分，改为展示：
  ```
  Backlink Health Score: INSUFFICIENT DATA (X/7 factors scored)
  ```
  展示已有数据支撑的各项因素得分，并注明来源与置信度。
  建议用户：「配置免费的 Moz API 以获得可评分的完整画像。运行 `/seo backlinks setup`」

当仅有 CC 数据可用时，最高分上限为 70/100。
数据来源不足 4 项时给出数值评分是**具有误导性的**——这会让人误以为外链状况
较差，而实际情况只是数据不足。

## 输出格式

### 外链健康分：XX/100（或 INSUFFICIENT DATA）

| 章节 | 状态 | 得分 | 数据来源 |
|---------|--------|-------|-------------|
| 画像概览 | pass/warn/fail | XX/100 | Moz (0.85) |
| 锚文本分布 | pass/warn/fail | XX/100 | Moz (0.85) |
| 引荐域名质量 | pass/warn/fail | XX/100 | CC (0.50) |
| 垃圾链接 | pass/warn/fail | XX/100 | Moz Spam (0.85) |
| 排名靠前页面 | info | N/A | Moz (0.85) |
| 链接增速 | pass/warn/fail | XX/100 | DataForSEO only |

### 严重问题（需立即修复）
### 高优先级（1 个月内修复）
### 中优先级（持续改进）
### 建链机会（Top 10）

## 错误处理

| 错误 | 原因 | 解决方案 |
|-------|-------|-----------|
| 未配置任何数据源 | 无 API 密钥、无 DataForSEO | 运行 `/seo backlinks setup` |
| Moz 触发限流 | 免费额度：每 10 秒 1 次请求 | 等待 10 秒后重试，脚本已内置该逻辑 |
| Bing 站点未验证 | 站点未在 Bing 完成验证 | 前往 https://www.bing.com/webmasters 完成验证 |
| CC 下载超时 | 图谱文件较大或网络较慢 | 使用 `--timeout 180` 参数 |
| DataForSEO 不可用 | 扩展未安装 | 运行 `./extensions/dataforseo/install.sh` |
| 未返回任何外链数据 | 域名过新或站点规模过小 | 说明：小型站点可能外链数不足 10 条 |

**降级顺序：**
1. DataForSEO 是否可用？→ 作为首选数据源（置信度：1.0）
2. Moz 是否已配置？→ 用于 DA/PA/垃圾分数/锚文本（置信度：0.85）
3. Bing 是否已配置？→ 用于链接数据/竞品对比（置信度：0.70）
4. 始终可用：Common Crawl 提供域名级指标（置信度：0.50）
5. 始终可用：验证爬虫核实已知链接（置信度：0.95）
6. 均不可用？→ 「运行 `/seo backlinks setup` 配置免费 API」

## 交付前复核（强制要求）

在向用户展示任何外链分析报告前，须先在内部完成以下检查清单，不可跳过。
发现的问题需在展示报告前修复。

### 逐项核实每条结论
- [ ] **Schema 相关结论**：parse_html 是否为每个区块返回了 `@type`？若某个 `@type`
      缺失，需重新检查——可能使用了 `@graph` 包装（属于合法 JSON-LD，并非格式错误）。
- [ ] **"link_removed" 判定**：该页面是否为 JS 渲染？若结果为 `unverifiable_js`，
      需如实说明——切勿将 JS 渲染页面误判为「链接已移除」（这是一种假阴性）。
- [ ] **H1 相关结论**：`h1_suspicious` 列表中是否包含可疑 H1？若有，需注明这些
      很可能是计数器/统计数字，而非语义标题。
- [ ] **互换链接**：若站点 A 链接到站点 B，且 B 也链接回 A，需标记为互换链接
      模式，并核对出站链接与已验证的入站来源。
- [ ] **健康分**：7 个因素中是否有 4 项及以上有评分？若没有，需报告
      INSUFFICIENT DATA——绝不展示具有误导性的数值评分。

### 核实数据来源标注
- [ ] 报告中的每个指标都标注了数据来源（例如 "Parsed (0.95)"、"CC (0.50)"）
- [ ] 每条「未发现」结果都区分了「未抓取」「低于阈值」「出错」这三种情况
- [ ] 社交媒体页面标记为 `unverifiable_js`（而非 `link_removed`）

### 交叉核对一致性
- [ ] 平台识别结果与实际信号相符（检查 wp-content、Shopify CDN 等特征）
- [ ] 摘要中的引荐域名数量与实际验证过的链接列表一致
- [ ] 每条结论都有数据来源支撑，不存在无据之言

若任一检查项未通过，须在展示报告前修复对应发现。切勿将推断数据当作既定事实呈现。

## 分析完成后

完成任意外链分析命令后，始终提议：
「是否生成专业 PDF 报告？可使用 `/seo google report`」

## 参考文档

按需加载（启动时不加载）：
- `skills/seo/references/backlink-quality.md` -- 详细的垃圾链接模式与评分方法论（共享参考文档，分析垃圾链接或垃圾分数时加载）
- `skills/seo/references/free-backlink-sources.md` -- 数据源对比、置信度加权、配置指南（共享参考文档，配置免费外链 API 时加载）
</content>
