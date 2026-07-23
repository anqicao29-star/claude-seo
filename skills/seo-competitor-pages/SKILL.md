---
name: seo-competitor-pages
description: >
  生成 SEO 优化的竞品对比页与替代品页。涵盖"X vs Y"版式、"X 的替代品"页面、
  功能对比矩阵、schema 标记，以及转化优化。当用户提到"对比页"、"vs 页面"、
  "替代品页面"、"竞品对比"、"X vs Y"、"对比一下"、"比较竞品"、"X 的替代方案"，
  或说 "comparison page", "vs page", "alternatives page", "competitor
  comparison", "X vs Y", "versus", "compare competitors", "alternative to"
  时使用本技能。
user-invocable: true
argument-hint: "[url or generate] [competitor]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 竞品对比与替代品页面

打造针对竞争型搜索意图关键词的高转化对比页与替代品页，内容准确、结构清晰。

## 页面类型

### 1. "X vs Y" 对比页
- 两个产品/服务之间的正面头对头对比
- 逐项功能的均衡分析
- 给出明确结论或推荐，并附理由
- 目标关键词：`[Product A] vs [Product B]`

### 2. "X 的替代品"页面
- 列出某个产品/服务的替代方案
- 每个替代品附简要说明、优缺点、最适合的使用场景
- 目标关键词：`[Product] alternatives`、`best alternatives to [Product]`

### 3. "最佳 [类别] 工具"榜单页
- 某个类别内热门工具/服务的精选榜单
- 明确说明排名标准
- 目标关键词：`best [category] tools [year]`、`top [category] software`

### 4. 对比表格页
- 多个产品并列展示的功能矩阵
- 若为交互式页面，支持排序/筛选
- 目标关键词：`[category] comparison`、`[category] comparison chart`

## 对比表格生成

### 功能矩阵版式
```
| Feature          | Your Product | Competitor A | Competitor B |
|------------------|:------------:|:------------:|:------------:|
| Feature 1        | ✅           | ✅           | ❌           |
| Feature 2        | ✅           | ⚠️ Partial   | ✅           |
| Feature 3        | ✅           | ❌           | ❌           |
| Pricing (from)   | $X/mo        | $Y/mo        | $Z/mo        |
| Free Tier        | ✅           | ❌           | ✅           |
```

### 数据准确性要求
- 所有功能描述都必须能从公开信息源核实
- 价格必须是最新的（注明"截至 [日期]"）
- 更新频率：每季度复核一次，或在竞品发布重大更新时复核
- 尽量为每个竞品数据点附上来源链接

## Schema 标记建议

### 带 AggregateRating 的 Product Schema
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "description": "[Product Description]",
  "brand": {
    "@type": "Brand",
    "name": "[Brand Name]"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[Rating]",
    "reviewCount": "[Count]",
    "bestRating": "5",
    "worstRating": "1"
  }
}
```

### SoftwareApplication（用于软件类对比）
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "[Software Name]",
  "applicationCategory": "[Category]",
  "operatingSystem": "[OS]",
  "offers": {
    "@type": "Offer",
    "price": "[Price]",
    "priceCurrency": "USD"
  }
}
```

### ItemList（用于榜单页）
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Best [Category] Tools [Year]",
  "itemListOrder": "https://schema.org/ItemListOrderDescending",
  "numberOfItems": "[Count]",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "[Product Name]",
      "url": "[Product URL]"
    }
  ]
}
```

## 关键词定向

### 对比型意图模式
| 模式 | 示例 | 搜索量信号 |
|---------|---------|---------------------|
| `[A] vs [B]` | "Slack vs Teams" | 高 |
| `[A] alternative` | "Figma alternatives" | 高 |
| `[A] alternatives [year]` | "Notion alternatives 2026" | 高 |
| `best [category] tools` | "best project management tools" | 高 |
| `[A] vs [B] for [use case]` | "AWS vs Azure for startups" | 中 |
| `[A] review [year]` | "Monday.com review 2026" | 中 |
| `[A] vs [B] pricing` | "HubSpot vs Salesforce pricing" | 中 |
| `is [A] better than [B]` | "is Notion better than Confluence" | 中 |

### Title 标签公式
- X vs Y：`[A] vs [B]: [Key Differentiator] ([Year])`
- 替代品页：`[N] Best [A] Alternatives in [Year] (Free & Paid)`
- 榜单页：`[N] Best [Category] Tools in [Year], Compared & Ranked`

### H1 模式
- 与 title 标签的意图保持一致
- 自然融入主关键词
- 控制在 70 字符以内

## 转化优化版式

### CTA 布局
- **首屏**：简要对比摘要 + 主 CTA
- **对比表格之后**："免费试用 [你的产品]" CTA
- **页面底部**：最终推荐 + CTA
- 在描述竞品的段落中避免使用强推销式 CTA（会削弱可信度）

### 社会认同板块
- 与对比标准相关的客户证言
- G2/Capterra/TrustPilot 评分（附来源链接）
- 展示从竞品迁移过来的案例研究
- "从 [Competitor] 换过来"的故事

### 定价亮点
- 清晰的定价对比表格
- 突出价值优势（而非单纯比谁便宜）
- 注明隐藏成本（开通费、按用户计费、超量费用）
- 链接到完整定价页面

### 信任信号
- "最后更新于 [日期]"时间戳
- 具备相关专业背景的作者署名
- 对比方法论说明（如何进行对比的）
- 说明自身产品关联的利益披露

## 公正性准则

- **准确性**：所有竞品信息都必须能从公开来源核实
- **禁止诋毁**：绝不对竞品做虚假或误导性陈述
- **注明来源**：链接到竞品官网、测评网站或官方文档
- **及时更新**：竞品发布重大更新时及时复核并更新
- **披露关联关系**：清楚说明哪个产品是自家的
- **平衡呈现**：如实承认竞品的优点
- **价格准确性**：所有价格数据都注明"截至 [日期]"
- **功能核实**：尽量实测竞品功能，无法实测时引用官方文档

## 内链建设

- 从对比章节链接到自家产品/服务页面
- 相关对比页之间互相交叉链接（例如"A vs B"链接到"A vs C"）
- 讨论具体功能时链接到对应的功能专题页
- 面包屑导航：Home > Comparisons > [本页]
- 页面底部设置相关对比推荐区
- 链接到对比中提到的案例研究和客户证言

## 输出

### 对比页模板
- `COMPARISON-PAGE.md`：可直接落地实施的页面结构，含各章节
- 功能矩阵表格
- 内容大纲，附字数目标（不少于 1,500 字）

### Schema 标记
- `comparison-schema.json`：Product/SoftwareApplication/ItemList JSON-LD

### 关键词策略
- 主关键词与次级关键词
- 相关长尾机会词
- 相对现有竞品页面的内容差距

### 建议
- 现有对比页的内容改进建议
- 新对比页的机会点
- Schema 标记补充建议
- 转化优化建议

## 错误处理

| 场景 | 处理方式 |
|------|--------|
| 竞品 URL 无法访问 | 报告哪些竞品 URL 抓取失败，使用现有数据继续，并在对比中注明数据缺口 |
| 竞品数据不足（价格、功能信息缺失） | 明确标记缺失的数据点，在对比表格中标注"暂无公开信息"，而非凭空猜测 |
| 未发现产品/服务存在重叠 | 报告这些产品服务的市场不同，建议改用有功能重叠的竞品，或转为类别榜单形式 |
