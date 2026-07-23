---
name: seo-ecommerce
description: >
  电商 SEO 分析：Google Shopping 可见度、Amazon 平台情报、产品 Schema 校验、
  竞品定价分析，以及平台关键词缺口挖掘。将站内产品 SEO 与来自 DataForSEO
  Merchant API 的平台数据相结合。当用户说"电商 SEO"、"ecommerce SEO"、
  "产品 SEO"、"product SEO"、"Google Shopping"、"平台 SEO"、
  "marketplace SEO"、"产品 schema"、"product schema"、"Amazon SEO"、
  "产品列表"、"product listings"、"购物广告"、"shopping ads"，或
  "商家 SEO"、"merchant SEO" 时使用本技能。
user-invocable: true
argument-hint: "<url or keyword>"
license: MIT
compatibility: "Enhanced with DataForSEO Merchant API (optional)"
metadata:
  author: AgriciDaniel
  original_author: "Matej Marjanovic (Pro Hub Challenge)"
  version: "2.2.0"
  category: seo
---

# 电商 SEO 分析

覆盖产品页优化、平台情报和竞品定价分析的综合分析能力。既可独立运行
（站内 + Schema 分析），也可结合 DataForSEO Merchant API 获取实时的
Google Shopping 和 Amazon 数据。

## 命令

| 命令 | 用途 | 是否需要 DataForSEO |
|---------|---------|-------------|
| `/seo ecommerce <url>` | 对产品页或店铺进行完整的电商 SEO 分析 | 可选 |
| `/seo ecommerce products <keyword>` | Google Shopping 竞品分析 | 必需 |
| `/seo ecommerce gaps <domain>` | 关键词缺口：自然排名 vs Shopping 可见度 | 必需 |
| `/seo ecommerce schema <url>` | 产品 Schema 校验与增强 | 否 |

---

## 1. 产品页分析（无需 DataForSEO）

抓取并解析任意产品页，评估其站内 SEO 质量。

### 工作流程

```
1. python3 scripts/render_page.py <url> --mode auto → 获取原始/渲染后的 HTML
2. python3 scripts/parse_html.py --url <url>   → 提取 SEO 元素
3. 分析产品专属信号（见下文）
```

### 产品 SEO 检查清单

#### Title 标签
- [ ] 包含核心产品关键词
- [ ] 包含品牌名称
- [ ] 不超过 60 个字符（避免在 SERP 中被截断）
- [ ] 格式：`[产品名称] - [核心卖点] | [品牌]`

#### Meta Description
- [ ] 包含产品关键词 + 利益点
- [ ] 包含价格或"低至 $XX"（有助于触发富媒体摘要展示）
- [ ] 包含行动号召（立即选购、购买、包邮）
- [ ] 不超过 155 个字符

#### 标题层级结构
- [ ] 单一 H1，与核心产品名称一致
- [ ] H2 覆盖：产品特性、规格参数、评价、相关产品
- [ ] 不同产品变体（variants）之间不出现重复 H1 标签

#### 产品图片
- [ ] Alt text 包含产品名称及区分性特征
- [ ] 文件名具有描述性（而非 `IMG_001.jpg`）
- [ ] 提供 WebP 格式（并附 JPEG 回退方案）
- [ ] 每个产品至少 3 张图片（主图、细节图、场景图）
- [ ] 图片尺寸 >= 800px，满足 Google Shopping 的准入要求
- [ ] 仅对首屏以下图片启用懒加载

#### 内链结构
- [ ] 面包屑导航：首页 > 分类 > 子分类 > 产品
- [ ] 相关产品模块（交叉销售/向上销售）
- [ ] 链接回分类页，锚文本包含关键词
- [ ] 评价区块链接到完整评价页（如为独立页面）

#### 内容质量
- [ ] 独特的产品描述（而非直接照搬厂商文案）
- [ ] 产品描述正文字数 >= 200
- [ ] 提供规格参数表（而非仅有大段文字）
- [ ] 页面内展示用户评价（UGC 信号）

### 评分权重

| 类别 | 权重 | 评分标准 |
|----------|--------|----------|
| Schema 完整度 | 25% | 必填 + 推荐的 Product 字段 |
| Title & Meta | 15% | 关键词位置、长度、格式 |
| 图片优化 | 20% | Alt text、格式、尺寸、数量 |
| 内容质量 | 20% | 独特描述、规格参数、评价 |
| 内链结构 | 10% | 面包屑、相关产品、分类页 |
| 技术层面 | 10% | 页面速度、移动端渲染、canonical |

---

## 2. Google Shopping 情报（DataForSEO Merchant API）

来自 Google Shopping 结果的实时竞品分析。

### 成本护栏（强制）

每次调用 Merchant API 前：
```bash
python3 scripts/dataforseo_costs.py check merchant_google_products_search
```

- `"status": "approved"` —— 直接执行
- `"status": "needs_approval"` —— 展示成本，征询用户
- `"status": "blocked"` —— 停止操作，告知用户

每次调用完成后：
```bash
python3 scripts/dataforseo_costs.py log merchant_google_products_search <cost>
```

### 工作流程

```bash
# 产品搜索：谁在以什么价格卖什么
python3 scripts/dataforseo_merchant.py search "<keyword>" --marketplace google

# 商家分析：商家评分与市场占有情况
python3 scripts/dataforseo_merchant.py sellers "<keyword>"

# 结果归一化处理，便于分析
python3 scripts/dataforseo_normalize.py results.json --module merchant
```

### 分析输出

#### 定价情报
- 价格分布：最低值、最高值、中位数、P25、P75
- 价格异常值（偏离中位数超过 2 个标准差）
- 价格与评分的相关性
- 统一换算为美元（或用户指定币种）

#### 商家格局
- 按上架商品数排名的前 10 商家
- 商家评分分布
- 包邮商家占比
- 新商家与老牌商家的对比

#### 产品列表质量
- 排名靠前列表中的标题关键词规律
- 平均评分与评论数基准
- 每个列表的图片数量
- 库存状态分布

加载 `references/marketplace-endpoints.md` 获取完整的 API 参数说明。

---

## 3. Amazon 平台（DataForSEO）

对比 Google Shopping 与 Amazon 的跨平台情报。

### 成本护栏（强制）

```bash
python3 scripts/dataforseo_costs.py check merchant_amazon_products_search
```

Amazon 相关端点属于 `warn_endpoints` 集合——始终需要用户批准。

### 工作流程

```bash
# Amazon 产品搜索
python3 scripts/dataforseo_merchant.py search "<keyword>" --marketplace amazon

# 跨平台对比
python3 scripts/dataforseo_merchant.py compare "<keyword>"
```

### 跨平台对比报告

| 指标 | Google Shopping | Amazon |
|--------|---------------|--------|
| 平均价格 | $ | $ |
| 评分中位数 | X.X | X.X |
| 平均评论数 | N | N |
| 头部商家份额 | % | % |
| 包邮占比 | % | % |

---

## 4. 平台关键词缺口

识别自然排名与 Shopping 可见度之间的错位。

### 工作流程

1. 通过 seo-dataforseo 获取自然排名：
   针对该域名调用 `dataforseo_labs_google_ranked_keywords`
2. 通过 Merchant API 获取 Google Shopping 曝光情况：
   针对排名靠前的自然关键词调用 `merchant_google_products_search`
3. 交叉对比结果

### 缺口类型

| 缺口类型 | 含义 | 建议动作 |
|----------|---------|--------|
| **仅自然排名** | 有自然排名但无 Shopping 广告 | 建立 Google Merchant Center feed，针对这些关键词投放竞价 |
| **仅 Shopping 曝光** | 有 Shopping 曝光但自然排名弱/无 | 针对这些关键词创建内容（购买指南、对比页） |
| **两者兼有** | 两个渠道都有曝光 | 优化：确保价格一致性，增强 Schema |
| **两者皆无** | 两个渠道都无曝光 | 除非搜索量很高，否则优先级较低 |

### 输出格式

```
## 关键词缺口分析：example.com

### 机会点：自然排名 → Shopping（12 个关键词）
| 关键词 | 自然排名位置 | 搜索量 | CPC | 建议动作 |
|---------|------------|--------|-----|-------------------|

### 机会点：Shopping → 自然排名（8 个关键词）
| 关键词 | Shopping 排名 | 搜索量 | CPC | 所需内容类型 |
|---------|-------------|--------|-----|-------------------|
```

---

## 5. 产品 Schema 增强

按 Google 现行要求校验并生成 Product Schema。

### 必填属性（Google Merchant）

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "",
  "image": [""],
  "description": "",
  "brand": { "@type": "Brand", "name": "" },
  "offers": {
    "@type": "Offer",
    "url": "",
    "priceCurrency": "USD",
    "price": "0.00",
    "availability": "https://schema.org/InStock",
    "seller": { "@type": "Organization", "name": "" }
  }
}
```

### 推荐属性（增强富媒体结果）

- `sku` —— 产品标识符
- `gtin13` / `gtin14` / `mpn` —— 全球贸易标识码
- `aggregateRating` —— 星级评分 + 评论数
- `review` —— 单条评价（至少 1 条）
- `color`、`material`、`size` —— 变体属性
- `shippingDetails` —— 包含费率和配送时长的 ShippingDetails
- `hasMerchantReturnPolicy` —— 包含类型和天数的 MerchantReturnPolicy

### 校验规则

1. `price` 必须是数字字符串，而非 "$29.99"（不含货币符号）
2. `availability` 必须使用完整的 Schema.org URL 枚举值
3. `image` 应为数组，至少包含 1 张高分辨率图片 URL
4. `priceCurrency` 必须符合 ISO 4217 标准（USD、EUR、GBP）
5. `brand.name` 不得为空或 "N/A"
6. `priceValidUntil` 中的日期必须符合 ISO 8601 格式
7. 若存在 `aggregateRating`：`ratingValue` 和 `reviewCount` 为必填项

### Schema 评分标准

| 完整度 | 得分 |
|-------------|-------|
| 全部必填字段 | 50/100 |
| + aggregateRating | 65/100 |
| + sku/gtin/mpn | 75/100 |
| + shippingDetails | 85/100 |
| + merchantReturnPolicy | 90/100 |
| + 评价（3 条以上） | 100/100 |

---

## 跨技能集成

| 技能 | 集成点 |
|-------|------------------|
| **seo-schema** | 委托生成 Product Schema，复用其校验逻辑 |
| **seo-images** | 产品图片审计（alt text、格式、尺寸）——以及针对 AI 生成产品图片的 `DigitalSourceType: TrainedAlgorithmicMedia` IPTC 标签（Merchant Center 强制要求） |
| **seo-content** | 产品描述的 E-E-A-T 与独特性分析 |
| **seo-dataforseo** | 用于缺口分析的自然关键词排名数据 |
| **seo-technical** | 产品页的 Core Web Vitals（主图的 LCP 表现） |
| **seo-google** | 通过 GSC 校验 Google Merchant Center feed |

## UCP —— 统一商务协议（前瞻性内容）

由 Google 主导（并与 Shopify、Etsy、Walmart、Wayfair、Visa、
Mastercard 等共同开发）的一项标准，让 AI 代理无需逐一定制对接，
即可发现、协商并与商家完成交易。目前已在 AI Mode 和 Gemini 中
支撑直接购买场景。

已入驻 **Google Merchant Center** 且拥有完善 Product Schema 的商家，
可在 `/.well-known/ucp` 处声明 UCP 配置文件，列出自身能力
（`dev.ucp.shopping.checkout`、`.fulfillment`、`.discount`）。审计标准、
能力示例，以及与 AP2（Agent Payments Protocol）的关系，详见
`references/ucp-universal-commerce-protocol.md`。

### 审计命令

```bash
# 发现并校验 UCP 配置文件
python3 scripts/ucp_check.py https://store.example.com --json

# 附带端点可达性探测（对每个已声明能力发起 HEAD 请求）
python3 scripts/ucp_check.py https://store.example.com --probe-endpoints --json
```

该脚本返回：配置文件是否存在、版本号、已声明的能力、
结构性问题（缺失字段、未知能力 ID），以及（在使用
`--probe-endpoints` 时）各端点的可达性。被 SSRF 拦截的端点会被明确标出。
配置文件缺失会被视为待改进的机会点，而非失败项——UCP 目前仍处于早期阶段。

---

## 错误处理

| 错误 | 原因 | 应对方式 |
|-------|-------|----------|
| 未找到 Product Schema | 页面缺少 JSON-LD | 分析页面内容，生成推荐的 Schema |
| DataForSEO 凭证缺失 | 环境变量未设置 | 在不使用平台数据的情况下继续分析，并注明局限性 |
| 成本检查被拦截 | 已超出每日预算 | 告知用户，提供仅限免费数据的分析 |
| Shopping 结果为空 | 该关键词无对应产品 | 建议扩大关键词范围，检查地区设置 |
| Amazon API 超时 | 网络问题/触发限流 | 采用退避策略重试，回退为仅使用 Google 数据 |
| URL 无效 | 输入格式错误 | 通过 `google_auth.validate_url()` 校验，展示错误信息 |
| 非产品页面 | URL 为分类页/首页 | 检测页面类型，建议改用 `/seo ecommerce schema` |

---

## 输出模板

```
## 电商 SEO 报告：[URL 或关键词]

### 综合得分：XX/100

### 产品页 SEO
- Schema 完整度：XX/100
- Title & Meta：XX/100
- 图片优化：XX/100
- 内容质量：XX/100
- 内链结构：XX/100

### 平台情报（如 DataForSEO 可用）
- Google Shopping 列表数：找到 N 个产品
- 价格区间：$XX - $XX（中位数：$XX）
- 头部商家：[名称]（市场份额 XX%）
- Amazon 对比：[已获取/未检查]

### 重点建议
1. [严重] ...
2. [高] ...
3. [中] ...

是否生成 PDF 报告？使用 `/seo google report`
```
