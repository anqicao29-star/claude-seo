---
name: seo-maps
description: >
  面向本地 SEO 的地图智能分析——geo-grid 排名追踪、通过 API 审计 GBP 主页、跨
  Google/Tripadvisor/Trustpilot 的评价情报、跨平台（Google/Bing/Apple/OSM）NAP
  信息核验、竞品半径地图，以及基于 API 数据生成 LocalBusiness schema。三档能力
  分级：免费档（Overpass + Geoapify）、DataForSEO 档（完整情报）、DataForSEO +
  Google 档（最大覆盖范围）。当用户提到 "地图分析"、"geo-grid"、"排名追踪"、
  "GBP 审计"、"评价增速"、"竞品半径"、"本地排名追踪"、"本地声量份额" —— Use when
  user says "maps", "geo-grid", "rank tracking", "GBP audit", "review
  velocity", "competitor radius", "maps analysis", "local rank
  tracking", "Share of Local Voice", or "SoLV".
user-invocable: true
argument-hint: "[command] [url|keyword|location]"
license: MIT
compatibility: "DataForSEO MCP for Tier 1+, Google Maps API for Tier 2"
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 地图智能分析（2026 年 3 月）

面向本地商户的地图平台分析。通过外部 API 评估商户在 Google Maps、Bing Places、
Apple Maps、OpenStreetMap 上的呈现情况。

**与 seo-local 的分工边界：** 本技能分析商户在地图**平台**上的表现（通过 API）；
seo-local 分析**网站**上的本地 SEO 信号（通过 HTML 抓取）。不要重复 seo-local 的
页面级分析。网站层面的检查请建议使用 `/seo local <url>`。

---

## 快速参考

| 命令 | 作用 | 所需档位 |
|---------|-------------|------|
| `/seo maps <url>` | 完整地图曝光审计（自动选择档位） | 0+ |
| `/seo maps grid <keyword> <location>` | Geo-grid 排名扫描（默认 7x7 网格，单关键词） | 1+ |
| `/seo maps reviews <business> <location>` | 跨平台评价情报 | 1+ |
| `/seo maps competitors <keyword> <location>` | 竞品半径地图 | 0+ |
| `/seo maps nap <business-name>` | 跨平台 NAP 信息核验 | 0+ |
| `/seo maps schema <business-name>` | 基于数据生成 LocalBusiness JSON-LD | 0+ |
| `/seo maps gbp <business> <location>` | GBP 完整度审计 | 1+ |

---

## 三档能力检测

分析前先检测可用的能力档位：

### Tier 0（免费档）
**检测方式：** DataForSEO MCP 工具不可用。
**具备能力：** Overpass API 竞品发现、Geoapify POI 搜索、Nominatim 地理编码、
静态 GBP 检查清单、schema 生成、跨平台 NAP 指导建议。
**加载：** `../seo/references/maps-free-apis.md`

### Tier 1（DataForSEO 档）
**检测方式：** `business_data_business_listings_search` MCP 工具可用。
**具备能力：** Tier 0 的全部能力，外加 geo-grid 排名追踪、实时 GBP 主页审计、
评价情报（增速、情感、分布）、GBP 动态发布情况、问答数据、Tripadvisor/Trustpilot
评价。
**加载：** `../seo/references/maps-api-endpoints.md`

### Tier 2（DataForSEO + Google Maps Platform 档）
**检测方式：** Tier 1 可用，且环境变量中配置了 Google Maps API 密钥。
**具备能力：** Tier 1 的全部能力，外加 Google Places 详情、实时营业状态、
AI 生成的地点摘要、图片分析。
**注意：** Google 服务条款要求仅可存储 `place_id`，经纬度缓存最长不超过 30 天。

**分析开始时务必向用户告知检测到的档位。**

---

## Geo-Grid 排名追踪（需 Tier 1 及以上）

模拟从多个 GPS 坐标点发起的 Google Maps 搜索，展示排名在地理范围内的波动情况。
需要 DataForSEO。

**加载：** `../seo/references/maps-geo-grid.md` 获取算法、SoLV 公式、热力图格式说明。
**加载：** `../seo/references/maps-api-endpoints.md` 获取 Maps SERP 接口的具体细节。

### 工作流程

1. 对商户地址进行地理编码，获取中心点经纬度
2. 使用 Haversine 偏移公式生成网格点（默认：7x7 网格，5 公里半径）
3. **先展示预估花费并征得用户确认，再继续执行**
4. 对每个网格点调用 DataForSEO Maps SERP API，携带 `location_coordinate` 参数
5. 找出目标商户在每个网格点的排名
6. 计算 SoLV（本地声量份额）：`(前三名出现次数 / 网格点总数) * 100`
7. 在输出中渲染 ASCII 热力图

### 费用提示（必须展示）

每次 geo-grid 扫描前须展示：
```
Geo-Grid Scan: [keyword] at [location]
Grid: 7x7 (49 points) | Keywords: [N] | Est. cost: $[amount]
DataForSEO credits will be consumed. Proceed?
```

---

## GBP 主页审计（优先 Tier 1，Tier 0 为人工检查）

审计影响 Google Business Profile 质量与排名的 25 项字段。

**加载：** `../seo/references/maps-gbp-checklist.md` 获取完整检查清单及评分方法。

### Tier 1 工作流程

1. 通过 DataForSEO My Business Info API（关键词或 CID）获取商户主页数据
2. 将 API 返回字段映射至 25 项检查清单
3. 逐项评分：已填写且优化到位 = 2 分，已填写 = 1 分，缺失 = 0 分
4. 应用行业专属权重系数
5. 归一化为 0-100 分制

### Tier 0 工作流程

1. 通过 WebFetch 抓取商户官网
2. 提取可见的 GBP 相关信号（地图嵌入、地点引用、评价组件）
3. 基于可检测到的信号套用静态检查清单
4. 无法检测的字段标注为「未知（需 DataForSEO 获取实时数据）」

---

## 评价情报（需 Tier 1 及以上）

跨平台评价分析：增速、情感倾向、评分分布、虚假评价识别。

**参考：** `../seo/references/local-seo-signals.md` 获取基准数据（与 seo-local 共享）。

### 工作流程

1. 通过 DataForSEO Reviews API 获取 Google 评价（按最新排序）
2. 计算评价增速：近 6 个月内的月均评价数
3. 检查「18 天规则」（Sterling Sky 提出）：任何连续 3 周的评价空窗期都构成排名风险
4. 分析评分分布：健康分布应呈偏向 5 星的钟形曲线
5. 计算商户回复率：回复数 / 评价总数
6. 获取 Tripadvisor 与 Trustpilot 的评价数据（如可用）
7. 生成跨平台对比表

### 虚假评价识别信号

若某条评价命中以下 2 项或以上模式，需标记：
- 时间分布异常集中（同一天/同一小时出现多条评价）
- 评价账号历史记录很少或仅发布过一条评价
- 地理位置不一致（评价者所在地与商户所在地不符）
- 清一色 5 星评价且短期内激增（相较历史基线）
- 多条评价文本高度相似或几乎相同
- 评价数量突增，但没有对应的营销活动

---

## 竞品半径地图（Tier 0 及以上）

识别并分析指定半径范围内的竞品。

### Tier 0（Overpass API）

**加载：** `../seo/references/maps-free-apis.md` 获取查询模板。

1. 对商户地址进行地理编码
2. 通过 Overpass API 查询半径范围内具有相同 OSM 标签的商户
3. 解析结果：名称、地址、电话、网址、与中心点的距离
4. 按距离排序，以竞品格局表形式呈现

### Tier 1（DataForSEO）

1. 使用 Maps SERP API，携带商户关键词与位置信息
2. 提取排名前 20 的竞品及完整主页数据
3. 对比维度：评分、评价数、类目、图片、属性字段
4. 计算竞争密度评分：每平方公里竞品数量

---

## 跨平台 NAP 信息核验（Tier 0 及以上）

核查商户信息（名称、地址、电话）在 Google、Bing Places、Apple、OSM 各平台间的一致性。

### 工作流程

1. 在各平台搜索商户名称：
   - Google：从 GBP 数据或 Maps SERP 结果中获取
   - Bing：`WebFetch https://www.bing.com/maps?q=BUSINESS+NAME+LOCATION`
   - Apple：需人工核查（无公开 API——建议前往 businessconnect.apple.com 使用
     Apple Business Connect）
   - OSM：通过 Overpass 或 Nominatim 搜索
2. 从每个数据源提取 NAP（名称、地址、电话）信息
3. 对比一致性：完全一致、部分一致、缺失或存在冲突
4. 按严重程度标记差异：Critical（名称不一致）、High（地址不一致）、Medium（电话不一致）
5. 建议认领尚未认领的主页

---

## Schema 生成（Tier 0 及以上）

基于采集到的数据生成 LocalBusiness JSON-LD 标记。

**参考：** `../seo/references/local-schema-types.md` 获取行业细分子类型（与 seo-local 共享）。

### 工作流程

1. 确定该行业最贴切的 schema 子类型
2. 填充必需属性：`@type`、`name`、`address`、`image`
3. 补充推荐属性：`telephone`、`url`、`geo`、`openingHoursSpecification`、`priceRange`
4. 面向多门店场景补充战略属性：`branchOf`、`areaServed`、`sameAs`
5. 如有评价数据，补充 `aggregateRating`
6. 输出可直接落地使用的合法 JSON-LD 代码块

**切勿生成自我背书式的评价标记**——Google 会忽略商户自行标注的 LocalBusiness
评价数据。仅应标记页面上真实展示的第三方评价。

---

## 参考文件

按需加载，不要在启动时一次性全部加载：
- `../seo/references/maps-api-endpoints.md`：DataForSEO 接口细节、参数、费用
- `../seo/references/maps-free-apis.md`：Overpass、Geoapify、Nominatim 查询模板
- `../seo/references/maps-geo-grid.md`：网格算法、SoLV 公式、热力图渲染方式
- `../seo/references/maps-gbp-checklist.md`：25 项 GBP 审计清单及行业权重
- `../seo/references/local-seo-signals.md`：排名因素、评价基准（共享）
- `../seo/references/local-schema-types.md`：按行业细分的 LocalBusiness 子类型（共享）

---

## 输出

生成 `MAPS-ANALYSIS-{domain}.md`，包含以下内容：

1. **地图健康分：XX/100**，附各维度细分表
2. **检测到的能力档位**（Tier 0 或 Tier 1），并说明该档位下可用的能力
3. **Geo-grid 热力图**（Tier 1）：带 SoLV 百分比及平均排名的 ASCII 网格
4. **GBP 主页审计**：逐字段评分，附行业专属权重
5. **评价情报**：增速趋势图、评分分布、回复率、跨平台对比
6. **竞品格局**：半径范围内竞品数量、评分/评价数 Top 5、竞争密度
7. **跨平台曝光情况**：Google/Bing/Apple/OSM 各平台的主页状态
8. **Schema 建议**：生成的 LocalBusiness JSON-LD（若缺失或不完整）
9. **优先行动清单 Top 10**（Critical > High > Medium > Low）
10. **费用报告**：分析过程中消耗的 DataForSEO 额度（仅 Tier 1）
11. **局限性说明**：当前档位下无法评估的内容

---

## 跨技能委派

- 网站页面级本地信号：建议使用 `/seo local <url>`
- 全面的 AI 搜索可见度：建议使用 `/seo geo <url>`
- Schema 校验与修复：建议使用 `/seo schema <url>`
- 实时 SERP 与关键词数据：建议使用 `/seo dataforseo [command]`

---

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| DataForSEO MCP 不可用 | 降级至 Tier 0，并告知用户：「未检测到 DataForSEO，将执行免费档分析。如需 geo-grid 追踪和评价情报，请安装 DataForSEO 扩展。」 |
| 在 Maps SERP 中未找到该商户 | 尝试用关键词调用 My Business Info；若仍未找到，报告「该商户在此位置的 Google Maps 中未找到」 |
| 地理编码失败（Nominatim） | 请用户提供坐标或更精确的地址 |
| 触发 API 限流 | 报告限流情况，建议等待或改用标准（排队）方式而非实时方式 |
| 未发现任何评价 | 报告零评价状态，建议以 18 天节奏为目标制定评价获取策略 |
| 检测到多门店 | 询问用户要分析哪个门店，或提供带单店费用预估的批量分析模式 |
</content>
