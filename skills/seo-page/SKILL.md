---
name: seo-page
description: >
  单页面深度 SEO 分析，涵盖页面内元素、内容质量、技术类 meta 标签、schema、
  图片和性能表现。Use when user says
  "analyze this page", "check page SEO", "single URL", "check this page",
  "page analysis", or provides a single URL for review.
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 单页面分析

## 分析内容

### 页面内 SEO
- 标题标签（Title tag）：50-60 个字符，包含主关键词，且唯一
- 元描述（Meta description）：150-160 个字符，具有吸引力，包含关键词
- H1：有且仅有一个，与页面意图匹配，包含关键词
- H2-H6：层级逻辑合理（不跳级），描述清晰
- URL：简短、有描述性、使用连字符、不带参数
- 内部链接：数量充足、锚文本相关、无孤立页面
- 外部链接：指向权威来源，数量合理

### 内容质量
- 字数是否达到该页面类型的最低要求（参见 quality-gates.md）
- 可读性：Flesch 可读性评分（Flesch Reading Ease）、阅读难度等级
- 关键词密度：自然（1-3%），出现语义相关变体
- E-E-A-T 信号：作者简介、资质认证、一手经验佐证
- 内容新鲜度：发布日期、最后更新日期

### 技术性元素
- Canonical 标签：存在，且自引用或指向正确
- Meta robots：默认 index/follow，除非有意屏蔽
- Open Graph：og:title、og:description、og:image、og:url
- Twitter Card：twitter:card、twitter:title、twitter:description
- Hreflang：多语言场景下，实现是否正确

### Schema 标记
- 检测所有类型（优先 JSON-LD 格式）
- 校验必需属性
- 识别缺失的优化机会
- 切勿再推荐 HowTo（已弃用）或 FAQ 用于富媒体结果（已于 2026 年 5 月退役）；现有 FAQPage 可保留作为 AI 引用信号，真正的问答场景请使用 QAPage

### 图片
- Alt 文本：存在、具描述性，在自然的情况下包含关键词
- 文件体积：超过 200KB 标记为警告，超过 500KB 标记为严重问题
- 格式：建议使用 WebP/AVIF 替代 JPEG/PNG
- 尺寸：设置 width/height 以防止 CLS
- 懒加载：报告每张图片的 `lazy_method`（native | perfmatters | ewww | js-generic | none）。检测到 JS 懒加载方案（Perfmatters、EWWW、lazysizes）时不要标记"未启用懒加载" —— 这些方案会有意去除原生 `loading="lazy"` 属性，改用 `data-src` 占位符

### Core Web Vitals（仅供参考，无法仅凭 HTML 测量）
- 标记潜在的 LCP 问题（超大首屏图片、阻塞渲染的资源）
- 标记潜在的 INP 问题（繁重的 JS、缺少 async/defer）
- 标记潜在的 CLS 问题（图片缺少尺寸、注入式内容）

## 输出

### 页面评分卡
```
Overall Score: XX/100

On-Page SEO:     XX/100  ████████░░
Content Quality: XX/100  ██████████
Technical:       XX/100  ███████░░░
Schema:          XX/100  █████░░░░░
Images:          XX/100  ████████░░
```

### 发现的问题
按优先级排序：紧急 -> 高 -> 中 -> 低

### 优化建议
具体、可执行的改进方案及预期效果

### Schema 建议
针对已发现机会提供可直接使用的 JSON-LD 代码

## DataForSEO 集成（可选）

若 DataForSEO MCP 工具可用，可用 `serp_organic_live_advanced` 获取真实 SERP 排名，用 `backlinks_summary` 获取反向链接数据和垃圾分数。

## 错误处理

| 场景 | 处理方式 |
|------|--------|
| URL 无法访问（DNS 故障、连接被拒绝） | 清楚地报告错误，不要臆测页面内容。建议用户确认 URL 后重试。 |
| 页面需要身份验证（401/403） | 报告该页面处于登录验证之后。建议用户直接提供渲染后的 HTML，或提供可公开访问的 URL。 |
| JavaScript 渲染的内容（HTML 中 body 为空） | 说明关键内容可能是客户端渲染的。分析可获取的 HTML 部分，并标记结果可能不完整。建议在可行的情况下使用浏览器渲染后的快照。 |
</content>
