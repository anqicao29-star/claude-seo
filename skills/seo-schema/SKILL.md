---
name: seo-schema
description: >
  检测、校验并生成 Schema.org 结构化数据，优先采用 JSON-LD 格式。
  当用户说"schema"、"结构化数据"、"富媒体结果"、"标记数据" 或
  "schema", "structured data", "rich results", "JSON-LD", "markup" 时使用本技能。
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# Schema 标记分析与生成

## 检测

1. 扫描页面源码中的 JSON-LD `<script type="application/ld+json">`
2. 检查 Microdata（`itemscope`、`itemprop`）
3. 检查 RDFa（`typeof`、`property`）
4. 始终优先推荐 JSON-LD 作为主要格式（这是 Google 官方明确表示的偏好）

## 校验

- 按 schema 类型检查必填属性
- 对照 Google 支持的富媒体结果类型进行校验
- 检测常见错误：
  - 缺失 @context
  - 无效的 @type
  - 数据类型错误
  - 占位文本未替换
  - 相对路径 URL（应使用绝对路径）
  - 日期格式无效
- 标记已弃用的类型（见下文）

## Schema 类型现状（截至 2026 年 5 月）

完整清单请查阅 `references/schema-types.md`。关键规则如下：

### 活跃可用（可放心推荐）：
Organization、LocalBusiness、SoftwareApplication、WebApplication、Product（2025 年 4 月起支持 Certification 标记）、ProductGroup、Offer、Service、Article、BlogPosting、NewsArticle、Review、AggregateRating、BreadcrumbList、WebSite、WebPage、Person、ProfilePage、ContactPage、VideoObject、ImageObject、Event、JobPosting、Course、DiscussionForumPosting

### 视频与专项类型（可放心推荐）：
BroadcastEvent、Clip、SeekToAction、SoftwareSourceCode

以上类型的可直接使用的 JSON-LD 模板见 `schema/templates.json`。

> **JSON-LD 与 JavaScript 渲染：** 根据 Google 2025 年 12 月发布的 JS SEO 指南，
> 通过 JavaScript 注入的结构化数据可能面临处理延迟。对于时效性较强的标记
> （尤其是 Product、Offer），应将 JSON-LD 直接写入服务器端渲染的初始 HTML 中。

### 无富媒体结果——但仍建议保留供 AI 使用：
- **FAQPage**：Google 已于 2026 年 5 月 7 日对所有站点全面下线 FAQ 富媒体结果
  （取代了 2023 年 8 月针对政府/健康类站点的限制）。目前已不再有对应的 SERP 展现形式——
  但由于该标记仍有助于 AI Mode / AI Overviews 的实体识别，建议将现有 FAQPage 标记为
  信息提示级（Info），而非严重问题级（Critical）。对于真实的用户问答页面，应改用 **QAPage**。

### 已弃用（切勿推荐）：
- **HowTo**：富媒体结果已于 2023 年 9 月移除
- **SpecialAnnouncement**：于 2025 年 7 月 31 日弃用
- **CourseInfo、EstimatedSalary、LearningVideo**：于 2025 年 6 月下线
- **ClaimReview**：于 2025 年 6 月从富媒体结果下线
- **VehicleListing**：于 2025 年 6 月从富媒体结果下线
- **Practice Problem**：于 2025 年末从富媒体结果下线
- **Dataset**：于 2025 年末从富媒体结果下线
- **Book Actions**：曾被弃用后又恢复，截至 2026 年 2 月仍可正常使用（历史备注）

## 生成

在为页面生成 schema 时：
1. 通过内容分析识别页面类型
2. 选择合适的 schema 类型
3. 生成包含所有必填 + 推荐属性的有效 JSON-LD
4. 只填入真实、可核实的数据；对占位内容要清晰标注，留待用户自行填写
5. 呈现输出前先完成校验

## 常见 Schema 模板

### Organization
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Company Name]",
  "url": "[Website URL]",
  "logo": "[Logo URL]",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "[Phone]",
    "contactType": "customer service"
  },
  "sameAs": [
    "[Facebook URL]",
    "[LinkedIn URL]",
    "[Twitter URL]"
  ]
}
```

### LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Business Name]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street]",
    "addressLocality": "[City]",
    "addressRegion": "[State]",
    "postalCode": "[ZIP]",
    "addressCountry": "US"
  },
  "telephone": "[Phone]",
  "openingHours": "Mo-Fr 09:00-17:00",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "[Lat]",
    "longitude": "[Long]"
  }
}
```

### Article/BlogPosting
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Title]",
  "author": {
    "@type": "Person",
    "name": "[Author Name]"
  },
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "image": "[Image URL]",
  "publisher": {
    "@type": "Organization",
    "name": "[Publisher]",
    "logo": {
      "@type": "ImageObject",
      "url": "[Logo URL]"
    }
  }
}
```

## 输出

- `SCHEMA-REPORT.md`：检测与校验结果
- `generated-schema.json`：可直接使用的 JSON-LD 片段

### 校验结果
| Schema | 类型 | 状态 | 问题 |
|--------|------|--------|--------|
| ... | ... | ✅/⚠️/❌ | ... |

### 建议
- 缺失的 schema 补充机会
- 需要修复的校验问题
- 用于实施的生成代码

## 错误处理

| 场景 | 处理动作 |
|----------|--------|
| URL 无法访问 | 报告连接错误及状态码，建议核实 URL 并检查页面是否需要身份验证 |
| 未发现 schema 标记 | 报告未检测到 JSON-LD、Microdata 或 RDFa，基于页面内容分析推荐合适的 schema 类型 |
| JSON-LD 语法无效 | 解析并报告具体语法错误（缺少括号、多余逗号、键名未加引号等），提供修正后的 JSON-LD 输出 |
| 检测到已弃用的 schema 类型 | 标记该已弃用类型及其下线日期，推荐当前的替代类型；若无替代类型，建议直接移除 |
