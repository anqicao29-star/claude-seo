---
name: seo-technical
description: >
  技术 SEO（Technical SEO）审计，覆盖 9 大类别：可爬取性（crawlability）、可索引性
  （indexability）、安全性、URL 结构、移动端适配、Core Web Vitals、结构化数据、
  JavaScript 渲染以及 IndexNow 协议。当用户说"技术 SEO"、"technical SEO"、
  "爬取问题"、"crawl issues"、"robots.txt"、"Core Web Vitals"、"网站速度"、
  "site speed"、或"安全响应头"、"security headers" 时使用本技能。
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 技术 SEO 审计

## 类别

### 1. 可爬取性（Crawlability）
- robots.txt：是否存在、格式是否有效、是否误封了重要资源
- XML 站点地图（sitemap）：是否存在、是否在 robots.txt 中被引用、格式是否有效
- Noindex 标签：判断是有意为之还是误配置
- 爬取深度：重要页面距首页应在 3 次点击以内
- JavaScript 渲染：检查关键内容是否依赖 JS 执行才能呈现
- 爬取预算（crawl budget）：对于大型站点（页面数超过 1 万）尤其需要关注抓取效率

#### AI 爬虫管理

截至 2025-2026 年，AI 公司正在积极抓取网络内容用于模型训练和 AI 搜索。通过
robots.txt 管理这些爬虫，是当前技术 SEO 中的一项关键考量。

**已知的 AI 爬虫：**

| 爬虫 | 公司 | robots.txt 标识 | 用途 |
|---------|---------|-----------------|---------|
| GPTBot | OpenAI | `GPTBot` | 模型训练 |
| ChatGPT-User | OpenAI | `ChatGPT-User` | 实时浏览 |
| ClaudeBot | Anthropic | `ClaudeBot` | 模型训练 |
| PerplexityBot | Perplexity | `PerplexityBot` | 搜索索引 + 训练 |
| Bytespider | 字节跳动（ByteDance） | `Bytespider` | 模型训练 |
| Google-Extended | Google | `Google-Extended` | Gemini 训练（不用于搜索） |
| CCBot | Common Crawl | `CCBot` | 开放数据集 |

**关键区别：**
- 屏蔽 `Google-Extended` 只会阻止其用于 Gemini 训练，并不影响 Google 搜索索引或
  AI Overviews（这两者走的是 `Googlebot`）
- 屏蔽 `GPTBot` 只会阻止 OpenAI 训练用途，并不会阻止 ChatGPT 通过浏览方式
  （`ChatGPT-User`）引用你的内容
- 目前约 3%-5% 的网站已设置了针对 AI 的专项 robots.txt 规则

**示例：有选择地屏蔽 AI 爬虫**
```
# Allow search indexing, block AI training crawlers
User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Bytespider
Disallow: /

# Allow all other crawlers (including Googlebot for search)
User-agent: *
Allow: /
```

**建议：** 在屏蔽之前先想清楚自己的 AI 可见性策略。被 AI 系统引用有助于提升品牌
认知度和引荐流量。完整的 AI 可见性优化请交叉参考 `seo-geo` 技能。

### 2. 可索引性（Indexability）
- Canonical 标签：是否自我引用、是否与 noindex 冲突
- 重复内容：近似重复页面、带参数的 URL、www 与非 www 版本
- 内容单薄（thin content）：低于对应页面类型最低字数要求的页面
- 分页：rel=next/prev 或加载更多（load-more）模式
- Hreflang：多语言/多地区站点是否正确配置
- 索引膨胀（index bloat）：占用爬取预算的无价值页面

### 3. 安全性
- HTTPS：是否强制启用、SSL 证书是否有效、是否存在混合内容（mixed content）
- 安全响应头：
  - Content-Security-Policy（CSP）
  - Strict-Transport-Security（HSTS）
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
- HSTS 预加载：对安全性要求高的站点，检查是否已加入 preload 名单

### 4. URL 结构
- URL 干净整洁：具描述性、使用连字符、内容页不带查询参数
- 层级结构：文件夹结构合理反映网站架构
- 重定向：不存在跳转链（最多 1 跳），永久迁移使用 301
- URL 长度：超过 100 个字符需标记
- 结尾斜杠：使用方式保持一致

### 5. 移动端优化
- 响应式设计：viewport meta 标签、响应式 CSS
- 触控目标：最小 48x48px，间距 8px
- 字号：基础字号最小 16px
- 无水平滚动
- 移动优先索引（Mobile-first indexing）：Google 索引移动版页面。**截至 2024 年
  7 月 5 日，移动优先索引已 100% 完成。** Google 现已对所有网站统一使用移动版
  Googlebot 抓取和索引。

### 6. Core Web Vitals
- **LCP**（Largest Contentful Paint，最大内容绘制）：目标 <2.5s
- **INP**（Interaction to Next Paint，交互到下一次绘制）：目标 <200ms
  - INP 已于 2024 年 3 月 12 日取代 FID，FID 已于 2024 年 9 月 9 日从所有 Chrome
    工具（CrUX API、PageSpeed Insights、Lighthouse）中彻底移除。不应在任何地方
    再提及 FID。
- **CLS**（Cumulative Layout Shift，累积布局偏移）：目标 <0.1
- 评估采用真实用户数据的第 75 百分位
- 若有 MCP 可用，优先使用 PageSpeed Insights API 或 CrUX 数据

### 7. 结构化数据
- 检测：JSON-LD（首选）、Microdata、RDFa
- 对照 Google 支持的类型进行校验
- 完整分析参见 seo-schema 技能

### 8. JavaScript 渲染
- 检查内容是出现在初始 HTML 中，还是需要依赖 JS
- 区分客户端渲染（CSR）与服务端渲染（SSR）
- 标记可能导致索引问题的 SPA 框架（React、Vue、Angular）
- 如适用，核实动态渲染（dynamic rendering）配置

#### JavaScript SEO：Canonical 与索引指引（2025 年 12 月）

Google 于 2025 年 12 月更新了 JavaScript SEO 文档，带来几项关键澄清：

1. **Canonical 冲突：** 若原始 HTML 中的 canonical 标签与 JavaScript 注入的不同，
   Google 可能采用其中任意一个。应确保服务端渲染 HTML 与 JS 渲染输出中的
   canonical 标签保持一致。
2. **JavaScript 处理的 noindex：** 若原始 HTML 中含有
   `<meta name="robots" content="noindex">`，但 JavaScript 将其移除，Google
   仍可能沿用原始 HTML 中的 noindex 指令。应在初始 HTML 响应中就提供正确的
   robots 指令。
3. **非 200 状态码：** Google 不会对返回非 200 HTTP 状态码的页面执行 JavaScript
   渲染。错误页面上通过 JS 注入的任何内容或 meta 标签，Googlebot 都无法看到。
4. **JavaScript 中的结构化数据：** 通过 JS 注入的 Product、Article 等结构化数据
   可能面临处理延迟。对于时效性较强的结构化数据（尤其是电商 Product 标记），
   应将其包含在初始服务端渲染 HTML 中。

**最佳实践：** 将关键 SEO 元素（canonical、meta robots、结构化数据、title、
meta description）放在初始服务端渲染 HTML 中，而不是依赖 JavaScript 注入。

### 9. IndexNow 协议
- 检查站点是否支持 IndexNow，服务于 Bing、Yandex、Naver
- 该协议由 Google 以外的搜索引擎支持
- 建议实施该协议，加快非 Google 搜索引擎的收录速度

## Agent 友好型页面（前瞻性考量）

AI agent（不仅是 AI 摘要工具）越来越多地通过三种渠道读取网站：基于截图的视觉
模型、原始 HTML/DOM，以及**无障碍树（accessibility tree）**（信号最干净的一种）。
审计标准——语义化 HTML（真正的 `<button>` 和 `<a>`，而非 `<div onclick>`）、
标签关联、交互目标尺寸、跨模板的布局稳定性、`cursor: pointer` 的正确使用——
详见 `references/agent-friendly-pages.md`。

### 审计命令

```bash
# Render with Playwright + capture accessibility tree, then score
python3 scripts/agent_ux_check.py https://example.com --json
```

该扫描器会输出 Agent-UX 评分（0-100）及逐项问题清单：
- HTML 层面发现：真实按钮/链接的使用情况、`<div onclick>` 组件、语义化地标、
  缺少 `<label for>` 的输入框、缺少 ARIA 标签的输入框
- 无障碍树层面发现：节点总数、可交互节点数、未命名的可交互元素、
  `role="generic"` 占比

无障碍树快照使用 Playwright 的
`page.accessibility.snapshot(interesting_only=False)`。若只需获取该树而不
打分，可使用 `python3 scripts/render_page.py <url> --a11y-tree --json`。

请将这些发现呈现为**优化机会**，而非硬性失败项。相关标准（WebMCP、agent UX
启发式规则）尚处于早期阶段——不要因为分数没满 100 就判定审计不通过。

## 输出

### 技术得分：XX/100

### 分类明细
| 类别 | 状态 | 得分 |
|----------|--------|-------|
| 可爬取性 | pass/warn/fail | XX/100 |
| 可索引性 | pass/warn/fail | XX/100 |
| 安全性 | pass/warn/fail | XX/100 |
| URL 结构 | pass/warn/fail | XX/100 |
| 移动端 | pass/warn/fail | XX/100 |
| Core Web Vitals | pass/warn/fail | XX/100 |
| 结构化数据 | pass/warn/fail | XX/100 |
| JS 渲染 | pass/warn/fail | XX/100 |
| IndexNow | pass/warn/fail | XX/100 |

### 严重问题（立即修复）
### 高优先级（1 周内修复）
### 中优先级（1 个月内修复）
### 低优先级（列入待办）

## DataForSEO 集成（可选）

如果 DataForSEO MCP 工具可用，使用 `on_page_instant_pages` 获取真实页面分析
数据（状态码、页面耗时、失效链接、页面级检查项），使用 `on_page_lighthouse`
进行 Lighthouse 审计（性能、无障碍、SEO 得分），使用
`domain_analytics_technologies_domain_technologies` 检测技术栈。

## Google API 集成（可选）

如果已配置 Google API 凭证，使用 `python3 scripts/pagespeed_check.py <url> --json`
获取真实的 PSI + CrUX 现场数据（替代仅有实验室数据的 CWV 估算值），使用
`python3 scripts/crux_history.py <url> --json` 获取 25 周的 CWV 趋势，使用
`python3 scripts/gsc_inspect.py <url> --json` 获取各 URL 的真实收录状态。

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| URL 无法访问 | 报告连接错误及状态码。建议核实 URL、检查 DNS 解析，并确认站点可公开访问。 |
| 未找到 robots.txt | 说明根域名下未检测到 robots.txt，建议创建一个包含合适指令的文件，并继续审计其余类别。 |
| 未配置 HTTPS | 标记为严重问题。报告是否存在无重定向的 HTTP 访问、混合内容，或 SSL 证书缺失/过期。 |
| Core Web Vitals 数据不可用 | 说明 CrUX 数据不可用（低流量站点常见情况）。建议以 Lighthouse 实验室数据作为替代参考，并建议流量提升后再重新测试。 |
