---
name: seo-local
description: >
  本地 SEO 分析，涵盖 Google Business Profile（GBP，谷歌商家资料）优化、NAP
  （名称/地址/电话）一致性、引用（citation）健康度、评论信号、本地 schema
  标记、地区页面质量、多门店本地 SEO，以及行业专属建议。可自动识别商家类型
  （实体门店、上门服务型、混合型）和行业垂类（餐饮、医疗、法律、家政服务、
  房地产、汽车）。Use when user says "local SEO", "Google
  Business Profile", "GBP", "map pack", "local pack", "citations",
  "NAP consistency", "local rankings", "service area", "multi-location",
  or "local search".
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 本地 SEO 分析（2026 年 3 月）

## 关键数据

| 指标 | 数值 | 来源 |
|--------|-------|--------|
| GBP 信号在本地内容包（local pack）权重中的占比 | 32% | Whitespark 2026 |
| 邻近度（proximity）对排名差异的贡献占比 | 55.2% | Search Atlas 机器学习研究 |
| 评论信号占比（较此前 16% 上升） | 约 20% | Whitespark 2026 |
| 带有本地查询意图的谷歌搜索占比 | 46% | 行业数据 |
| 移动端"附近"搜索在 24 小时内转化为到店的比例 | 76% | Google 确认数据 |
| 使用 ChatGPT/AI 获取本地推荐的比例（较此前 6% 上升） | 45% | BrightLocal LCRS 2026 |
| ChatGPT 本地转化率 | 15.9% | Seer Interactive |
| Google 自然搜索本地转化率 | 1.76% | Seer Interactive |
| 本地内容包广告增长（2025 年 1 月至 2026 年 1 月） | 从 1% 增至 22% | Sterling Sky |

---

## 商家类型识别

在分析前先根据页面信号进行判定，这将决定适用哪些检查项。

### 实体门店（Brick-and-Mortar）
- 页面内容或页脚中出现可见的实体街道地址
- 内嵌 Google 地图，带有定位标记/导航功能
- 出现"欢迎光临"、"店铺地址位于"、"欢迎莅临"等表述
- LocalBusiness schema 中有结构化地址

### 上门服务型商家（Service Area Business, SAB）
- 页面中无可见实体地址
- 出现服务范围相关表述："服务覆盖 [城市/地区]"、"服务范围包括"
- "我们上门服务"、"现场服务"、"移动式 [服务]"等表述
- schema 中有 `areaServed` 但无 `address.streetAddress`

### 混合型（Hybrid）
- 同时出现实体地址与服务范围相关表述
- 例如"欢迎参观我们的展厅"同时配有"我们同样服务于 [地区]"

**对检查项的影响**：上门服务型商家（SAB）跳过内嵌地图验证和实体地址一致性检查；实体门店则需完整执行 NAP 及地图相关检查。

---

## 行业垂类识别

依据页面信号和 GBP 类目模式进行判定，并据此路由到 `../seo/references/local-schema-types.md` 中的行业专属检查项。

| 垂类 | 识别信号 |
|----------|------------------|
| **餐饮** | /menu、菜单项、订座、菜系类型、在线点餐、"堂食"、"外带" |
| **医疗** | 支持的保险类型、患者、预约挂号、NPI、医学术语、"医生（Dr.）"、HIPAA 声明 |
| **法律** | 律师、律所业务范围、执业资格、案例成果、"免费咨询" |
| **家政服务** | 服务范围、紧急服务、"免费报价"、持证/投保/担保、"24/7" |
| **房地产** | 房源、MLS、待售/待租房产、经纪人简介、经纪公司、"开放日看房" |
| **汽车** | 库存车辆、VIN 车架号、试驾、经销商、售后服务部门、"新车/二手车/认证车" |

若未识别出具体垂类，采用通用的 `LocalBusiness` 分析路径。

---

## 分析维度

### 1. GBP 信号（占比 25%）

主要类目是**本地内容包排名中最重要的单一因素**（Whitespark 排名第一，得分 193）。类目设置错误是**头号负面因素**（得分 176）。

**检查项：**
- 页面上是否能检测到 GBP 嵌入或引用（地图 iframe、place ID、评论小组件）
- 主要类目的匹配度（结合页面内容与可见的 GBP 数据进行推断）
- 是否有次要类目的证据（据 BrightLocal 建议，最佳数量为额外 4 个）
- 是否存在 GBP 动态（Posts）（据 WebFX，对排名无直接影响，但会触发 Post Justifications 展示）
- 照片/视频证据（有照片的商家，导航请求量提升 45%，Agency Jet 数据）
- 问答（Q&A）内容（已于 2025 年 12 月弃用，被 Ask Maps Gemini AI 取代 -- 建议将原有 Q&A 内容改写为网站上的 FAQ 版块；GBP 已移除原有 Q&A 且不提供导出功能）
- Google 认证徽章（Google Verified badge）资格（2025 年 10 月取代了原 Guaranteed/Screened 徽章）
- GBP 链接 URL 策略：不要链接到网站中权重最高的页面（据 Sterling Sky Diversity Update -- 存在压制自然排名的风险）
- 页面上营业时间的可见性（搜索发生时正处于营业状态的商家排名更高，位列第 5 大因素）

**评分标准：**
- 满分：存在 GBP 嵌入、类目信号匹配、动态活跃、有照片
- 部分：存在部分 GBP 信号但不完整
- 偏低：网站上无可见的 GBP 集成

### 2. 评论与口碑（占比 20%）

评论更新频率比总数更重要。**18 天法则**（Sterling Sky）：若 3 周内无新评论，排名会出现断崖式下跌。

**检查项：**
- 页面或 schema 中是否可见 Google 评论总数（临界阈值：10 条，Sterling Sky）
- 星级评分（据 BrightLocal 2026，31% 的消费者只看 4.5 星以上，68% 只看 4 星以上）
- 评论时效性指标（74% 的消费者只关心近 3 个月内的评论）
- schema 中的 `aggregateRating`（ratingValue、reviewCount、bestRating）
- 第三方评论平台的存在情况（据 BrightLocal 2026，消费者平均会参考 6 个评论网站）
- 商家回复模式（据 BrightLocal，88% 的消费者更愿意选择会回复评论的商家）
- 评论门控检测：任何在引导用户前往评论平台前先行筛选满意度的做法，均属 Google 明令禁止的行为（虚假互动政策），也违反 FTC 规定（每次违规罚款 $53,088）

**行业专属提示：**
- 医疗行业：HIPAA 规定，在评论回复中不得确认或否认评论者是否为患者
- 法律行业：评论回复需考虑律师-客户保密特权相关问题

**评分标准：**
- 满分：10+ 条评论，4.5 星以上，近期活跃，有商家回复，多平台均有覆盖
- 部分：有一定数量评论，但在时效性、评分或回复率方面存在差距
- 偏低：少于 10 条评论，无近期活动，无回复，仅单一平台

### 3. 本地页面 SEO（占比 20%）

独立的服务页面是**本地自然搜索排名的头号因素，同时也是 AI 可见度的第二大因素**（Whitespark 2026）。

**检查项：**
- 标题标签（title tag）中包含城市/服务关键词
- H1 标签带有本地意图（城市 + 服务）
- 页面 HTML 中可见 NAP（名称、地址、电话）信息（页脚、联系方式区块、页头）
- 独立的服务页面（每个核心服务对应一个页面）
- 多门店站点的地区页面质量：
  - 独特内容占比至少 **60%-70%**（行业共识，Google 并未给出官方阈值）
  - **互换测试**：如果把城市名互换后内容仍然读得通，说明这是一个"门面页"（doorway page，RicketyRoo 提出的方法）。某 HVAC 公司因此类问题在 2024 年 3 月核心算法更新后损失了 80% 的排名和 63% 的流量
  - 本地照片、地区专属客户评价、本地常见问题
- 内嵌 Google 地图（作为地理信号的强化手段，而非直接排名因素 -- 建议懒加载以减轻对速度的影响）
- 点击拨号按钮（`tel:` 链接）与联系表单置于首屏以上
- 内部链接架构：hub-and-spoke 模式，每个重要页面距首页不超过 3 次点击
- 每 1000 字正文中包含 2-5 条上下文相关的内部链接，并使用具描述性的锚文本

**多门店专属提示：**
- 门店查找器（store locator）需提供可独立抓取的 URL（相比 CSR，更推荐 SSR/SSG）
- 子目录结构：`domain.com/locations/city-name/`（子目录能更好地整合链接权重，据 Bruce Clay，流量提升可达 50% 以上）
- 每个地区页面拥有独立的 LocalBusiness schema，并带有唯一的 `@id`

**评分标准：**
- 满分：标题及 H1 含城市信息，NAP 可见，有独立服务页面，无门面页问题，内链结构良好
- 部分：有一定本地信号，但缺少服务页面或存在门面页风险
- 偏低：标题/H1 泛化，NAP 不可见，地区页面内容单薄

### 4. NAP 一致性与引用（占比 15%）

引用（citations）对传统内容包排名的影响正在下降，但 **Top 5 的 AI 可见度因素中有 3 项与引用相关**（Whitespark 2026）。Google 在 2025 年 7 月的文档更新中，已将"目录站点"从权威性定义中移除。

**检查项：**
- NAP 提取：对比以下三个来源的名称、地址、电话：
  1. 页面可见 HTML（页脚、联系我们页面）
  2. LocalBusiness JSON-LD schema
  3. 任何可见的 GBP 数据
  - 标记出这三个来源之间的任何不一致
- 一级（Tier 1）目录站点的引用情况（可通过 WebFetch 或 site: 搜索模式检查）：
  - 页面上的 Google Business Profile 信号
  - Yelp：`site:yelp.com "Business Name"`
  - BBB：`site:bbb.org "Business Name"`
  - Facebook 商家主页引用
- Apple Business Connect 认知度（使用率翻倍至 27%，BrightLocal 2026 -- 建议认领）
- Bing Places 认知度（是 ChatGPT、Copilot、Alexa 的数据来源之一 -- 建议认领并优化）
- 行业专属目录建议：参见 `../seo/references/local-schema-types.md` 中各垂类的引用来源
- 数据聚合商认知度：Data Axle、Foursquare、Neustar/TransUnion（建议提交信息以实现下游分发）

**评分标准：**
- 满分：页面/schema 间 NAP 一致，检测到一级引用，行业目录站点均有收录
- 部分：NAP 存在但有不一致，部分引用缺失
- 偏低：NAP 存在差异，未检测到任何引用，schema 中无地址

### 5. 本地 Schema 标记（占比 10%）

Schema 本身并非直接排名因素（John Mueller 已确认），但能触发富媒体结果（据 Webstix 案例研究，点击率提升 43%），并帮助 AI 系统解析商家信息。

**检查项：**
- LocalBusiness schema 的存在情况（提取 JSON-LD 代码块）
- 必需属性：`name`、带 PostalAddress 子属性的 `address`
- 建议属性：`geo`（精度至少 5 位小数，已确认）、`openingHoursSpecification`、`telephone`、`url`、`priceRange`（不超过 100 字符）、`image`、`aggregateRating`
- **是否使用了正确的行业子类型** -- 参见 `../seo/references/local-schema-types.md`：
  - 餐饮应使用 `Restaurant` 而非通用的 `LocalBusiness`
  - 法律应使用 `LegalService` 而非已弃用的 `Attorney`
  - 汽车经销商应使用 `AutoDealer` 而非已弃用的 `VehicleListing`
  - 医疗应使用 `MedicalClinic`/`Hospital`/`Dentist`，而非通用的 `MedicalBusiness`
- 上门服务型（SAB）专属：`areaServed` 中列出具体城市名（建议做法，虽未列入 Google 官方列表，但 Schema.org 支持）
- 多门店：每个地区页面拥有独立的 LocalBusiness，各带唯一 `@id`，并通过 `branchOf` 关联到首页的 Organization
- 各行业专属 schema 模式（详见 `../seo/references/local-schema-types.md`）：
  - 餐饮：Menu + MenuSection + MenuItem + ReserveAction
  - 医疗：Physician（Person）+ MedicalSpecialty + sameAs 关联至 NPI
  - 法律：LegalService + Person + Service（业务范围）
  - 家政服务：对应子类型 + areaServed + Service
  - 房地产：RealEstateAgent + Person + RealEstateListing
  - 汽车：AutoDealer + Car + Offer（各部门独立 schema）

**评分标准：**
- 满分：子类型正确，所有建议属性齐全，符合行业专属模式，JSON-LD 有效
- 部分：存在 LocalBusiness 但类型泛化或缺少建议属性
- 偏低：无本地 schema，或 schema 存在错误/占位内容

### 6. 本地链接与权威信号（占比 10%）

链接因素对本地内容包的影响正在下降，但仍占**本地自然排名约 26%**的权重（Whitespark 2026，位列第二大因素组）。"最佳榜单"类收录是**AI 可见度引用的头号因素**。

**检查项：**
- 可从页面检测到的本地反向链接信号：
  - 商会（Chamber of Commerce）提及或链接（信任度高，据 GlueUp，消费者到店量提升约 80%）
  - BBB 认证徽章（Google 会利用 BBB 数据进行商家核验）
  - 本地新闻/媒体报道
  - 社区参与信号（赞助、本地活动、合作伙伴关系）
- "最佳榜单"收录情况（据 Whitespark 2026，是 AI 可见度的头号因素）
- 数字公关（Digital PR）信号：据 BuzzStream 2026，66.2% 的公关从业者已将 AI 引用率纳入 KPI 追踪
- 品牌提及与 AI 可见度的相关性是传统反向链接的 **3 倍**（Ahrefs 数据：相关系数 0.664 对比 0.218）
- 链接增长基准：小型企业每月获取 5-10 条优质本地链接（行业共识）

**评分标准：**
- 满分：可见的本地权威信号（商会、BBB、媒体报道），社区参与度明显
- 部分：有一定权威信号，但本地链接信号有限
- 偏低：未检测到任何本地权威信号

---

## AI 搜索对本地 SEO 的影响

**不要与 seo-geo 的分析重复。** 这里只提供本地相关的 AI 背景信息，完整分析建议使用 `/seo geo <url>`。

本地 AI 关键事实：
- AI Overviews 在多达 68% 的本地搜索中出现（Whitespark 2025 年第二季度）
- ChatGPT 转化率为 15.9%，而 Google 自然搜索为 1.76%（Seer Interactive）
- Top 5 的 AI 可见度因素中有 3 项与引用相关（Whitespark 2026）
- ChatGPT 并不直接访问 GBP 数据 -- 其数据来源于 Bing 索引、Yelp、TripAdvisor、BBB、Reddit
- Bing Places 至关重要：是 ChatGPT、Copilot、Alexa 的数据来源
- AI 驱动的本地内容包（美国移动端）仅展示 1-2 家商家，展示数量减少 32%（Sterling Sky）

**建议**：运行 `/seo geo <url>` 获取全面的 AI 搜索可见度分析，包括可引用性评分、llms.txt 检查和品牌提及审计。

---

## 参考文件

按需加载：
- `../seo/references/local-seo-signals.md`：排名因素、评论基准、引用等级、GBP 功能状态、算法更新
- `../seo/references/local-schema-types.md`：按行业划分的 LocalBusiness 子类型、schema 模式、各垂类引用来源

---

## 输出

生成 `LOCAL-SEO-ANALYSIS-{domain}.md`，内容包括：

1. **本地 SEO 得分：XX/100**，附各维度细分表格
2. **商家类型**：实体门店 / 上门服务型（SAB）/ 混合型
3. **识别出的行业垂类** + 行业专属发现
4. **GBP 优化清单**（已检测信号 vs 缺失项）
5. **评论健康度快照**（评分、数量、更新频率指标、回复模式）
6. **NAP 一致性审计**（页面与 schema 的差异、多来源对比）
7. **引用情况检查**（一级目录站点收录状态）
8. **本地 schema 状态**（存在/缺失/格式错误 + 可直接使用的修复方案）
9. **地区页面质量**（如为多门店：独特内容占比、门面页风险、门店查找器情况）
10. **优先级排序的十项行动建议**（紧急 > 高 > 中 > 低）
11. **局限性说明**：本次分析无法评估的内容（地理网格排名、域名权重、完整反向链接情况、GBP Insights 数据、实时本地内容包排名），以及哪些付费工具可以弥补这些缺口

---

## 快速见效项

1. 认领并优化 Apple Business Connect（使用率已翻倍至 27%）
2. 认领并优化 Bing Places（是 ChatGPT、Copilot、Alexa 的数据来源）
3. 修复页面、schema 与 GBP 之间的任何 NAP 差异
4. 添加带正确行业子类型的 LocalBusiness schema
5. 添加精度 5 位以上小数的 `geo` 坐标
6. 确保电话号码使用 `tel:` 链接以支持点击拨号
7. 在标题标签和 H1 中加入城市 + 服务关键词

## 中等投入

1. 为每个核心服务创建独立页面（Whitespark：本地自然搜索排名的头号因素）
2. 建立评论获取策略，维持至少 18 天一次的更新频率
3. 提交至三个数据聚合商（Data Axle、Foursquare、Neustar/TransUnion）以实现下游分发
4. 认领行业专属目录站点收录（按垂类建议执行）
5. 添加行业专属 schema 模式（如餐饮用 Menu，医疗用 Physician 等）
6. 为服务/地区页面实施 hub-and-spoke 内部链接结构

## 高影响力

1. 制定以"最佳榜单"为目标的本地数字公关策略（AI 可见度头号因素）
2. 为每个地区页面开发独特、不可互换的内容（独特内容占比 60% 以上）
3. 在 ChatGPT 数据来源平台（Yelp、TripAdvisor、BBB、Reddit）上建立存在感
4. 争取加入商会及 BBB 会员（权威性 + 核验信号）
5. 制作社区参与类内容（赞助、本地活动、合作伙伴关系）

---

## DataForSEO 集成（可选）

若 DataForSEO MCP 工具可用，可用 `local_business_data` 提取实时 GBP 数据，用 `google_local_pack_serp` 获取实时本地内容包排名，用 `business_listings` 实现跨目录站点的自动化引用审计。

---

## 错误处理

| 场景 | 处理方式 |
|--------|--------|
| URL 无法访问（DNS 故障、连接被拒绝） | 清楚地报告错误，不要臆测页面内容。建议用户确认 URL 后重试。 |
| 页面未检测到任何本地信号 | 报告未发现本地商家相关指标。建议用户确认这确实是一家本地商家，并提供 GBP 列表链接（如有）。 |
| 页面 HTML 中未找到 NAP | 检查 schema 和 meta 标签。若仍未找到，标记为紧急问题，建议在页脚和联系页面添加可见的 NAP 信息。 |
| 行业垂类不明确 | 展示检测置信度最高的两个垂类及其对应信号，请用户确认后再应用行业专属建议。 |
| 多门店场景下地区页面超过 50 个 | 按照 seo orchestrator 的质量门限执行：30+ 页面时发出警告（要求独特内容占比 60% 以上），50+ 页面时强制停止（需用户给出理由后方可继续）。 |

## FLOW 框架集成

如需借助提示词完成本地优化，可使用 `/seo flow local <url>` —— FLOW 框架的 11 个 local 阶段提示词，涵盖 GBP 优化、元描述、标题标签及结构化本地审计流程。
</content>
