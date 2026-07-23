---
name: seo-audit
description: "全站 SEO 审计，通过并行子 agent 委派完成分析。最多爬取 500 个页面，自动检测业务类型，最多委派给 15 个专项 agent（8 个常驻 + 7 个按需触发），生成健康度评分。当用户说 audit、全面 SEO 检查、分析我的网站、网站体检 时使用本技能。Use when user says audit, full SEO check, analyze my site, or website health check."
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 全站 SEO 审计

## 流程

1. **渲染首页**：使用 `python3 scripts/render_page.py <url> --mode auto --json` 捕获原始 HTML、渲染后 HTML、提取的文本、SPA 状态，以及必要时的无障碍数据
2. **检测业务类型**：按 seo 编排器的规则分析首页信号
3. **爬取站点**：沿内部链接爬取，最多 500 个页面，遵守 robots.txt
4. **委派子 agent**（如可用；否则按顺序在本地依次执行）：
   - `seo-technical` —— robots.txt、sitemap、canonical、Core Web Vitals、安全响应头
   - `seo-content` —— E-E-A-T、可读性、内容单薄、AI 引用就绪度
   - `seo-schema` —— 结构化数据检测、校验、生成建议
   - `seo-sitemap` —— 结构分析、质量门槛、缺失页面
   - `seo-performance` —— LCP、INP、CLS 测量
   - `seo-visual` —— 截图、移动端测试、首屏内容分析
   - `seo-geo` —— AI 爬虫可访问性、llms.txt、可引用性、品牌提及信号
   - `seo-local` —— GBP（Google Business Profile）信号、NAP 一致性、评价、本地结构化数据、行业专属本地因素（当检测到本地服务型行业时触发：实体门店、上门服务型（SAB）或混合业务类型）
   - `seo-maps` —— 地理网格排名追踪（geo-grid rank tracking）、GBP 审计、评价情报、竞对辐射范围地图（当检测到本地服务型业务且 DataForSEO MCP 可用时触发）
   - `seo-google` —— CWV 现场数据（CrUX）、URL 收录状态（GSC）、自然流量（GA4）（当通过 `python3 scripts/google_auth.py --check` 检测到 Google API 凭证时触发）
   - `seo-backlinks` —— 外链画像数据：DA/PA、引荐域名、锚文本、垃圾链接（当通过 `python3 scripts/backlinks_auth.py --check` 检测到 Moz 或 Bing API 凭证时触发；否则始终纳入 Common Crawl 域名级指标）
   - `seo-cluster` —— 语义聚类分析（当检测到内容策略相关信号时触发：博客、支柱页面、话题集群）
   - `seo-sxo` —— 搜索体验分析：页面类型错配、用户故事、人设打分（全站审计中始终纳入）
   - `seo-drift` —— 漂移分析：与已存储的基线进行对比（当通过 `python3 scripts/drift_history.py <url>` 检测到该 URL 存在漂移基线时触发）
   - `seo-ecommerce` —— 产品结构化数据、电商平台情报（当检测到电商行业时触发）
5. **评分** —— 汇总为 SEO 健康度评分（0-100）
6. **归档审计产出物** —— 将全部输出写入 `{domain}-audit/` 目录下
7. **报告** —— 生成优先级排序的行动计划，并可选生成 PDF/HTML 报告

## 爬取配置

```
Max pages: 500
Respect robots.txt: Yes
Follow redirects: Yes (max 3 hops)
Timeout per page: 30 seconds
Concurrent requests: 5
Delay between requests: 1 second
```

## 输出文件

- `{domain}-audit/FULL-AUDIT-REPORT.md`：完整发现汇总
- `{domain}-audit/ACTION-PLAN.md`：按优先级排序的建议（严重 > 高 > 中 > 低）
- `{domain}-audit/audit-data.json`：用于生成报告的结构化审计数据封装
- `{domain}-audit/findings/*.md`：各专项 agent 的分类发现（`technical.md`、`content.md`、`schema.md`、`performance.md`、`visual.md` 等）
- `{domain}-audit/screenshots/`：桌面端 + 移动端截图（若 Playwright 可用）
- **PDF 报告**（推荐）：使用 `scripts/google_report.py --type full --data {domain}-audit/audit-data.json --domain <domain> --output-dir {domain}-audit/` 生成专业的 A4 PDF。该报告采用白色封面的企业级排版，含目录、执行摘要、图表（Lighthouse 仪表盘、查询柱状图、索引环形图）、指标卡片、阈值表、附带工作量预估的优先级建议，以及实施路线图。每次完成审计后都应主动提出生成 PDF。

## 结构化审计数据封装

按以下结构写入 `{domain}-audit/audit-data.json`，这样即便 Google API 数据不可用，
`python3 scripts/google_report.py --type full --data {domain}-audit/audit-data.json --domain <domain> --output-dir {domain}-audit/` 也能生成报告：

```json
{
  "summary": {
    "health_score": 0,
    "business_type": "detected type",
    "top_findings": [],
    "quick_wins": []
  },
  "categories": [
    {
      "name": "Technical SEO",
      "score": 0,
      "what_works": [],
      "findings": [
        {
          "title": "Finding title",
          "severity": "Critical|High|Medium|Low|Info",
          "description": "Evidence-backed detail",
          "recommendation": "Specific fix"
        }
      ]
    }
  ],
  "action_plan": {
    "phases": [
      {"name": "Phase 1: Critical Fixes", "timeframe": "Week 1", "items": []},
      {"name": "Phase 2: High-Impact Improvements", "timeframe": "Weeks 2-3", "items": []},
      {"name": "Phase 3: Content & Authority", "timeframe": "Month 2", "items": []},
      {"name": "Phase 4: Monitoring & Iteration", "timeframe": "Ongoing", "items": []}
    ]
  },
  "artifacts": {
    "findings_dir": "findings/",
    "screenshots_dir": "screenshots/"
  }
}
```

## 评分权重

| 类别 | 权重 |
|----------|--------|
| 技术 SEO | 22% |
| 内容质量 | 23% |
| 页面 SEO（On-Page） | 20% |
| 结构化数据（Schema） | 10% |
| 性能（Core Web Vitals） | 10% |
| AI 搜索就绪度 | 10% |
| 图片 | 5% |

## 报告结构

### 执行摘要
- 整体 SEO 健康度评分（0-100）
- 检测到的业务类型
- 五大严重问题
- 五大速赢机会

### 技术 SEO
- 可爬取性问题
- 可索引性问题
- 安全性隐患
- Core Web Vitals 状态

### 内容质量
- E-E-A-T 评估
- 内容单薄的页面
- 重复内容问题
- 可读性评分

### 页面 SEO（On-Page）
- Title 标签问题
- Meta description 问题
- 标题层级结构
- 内链缺口

### 结构化数据
- 现有实现情况
- 校验错误
- 待补充的机会点

### 性能
- LCP、INP、CLS 得分
- 资源优化需求
- 第三方脚本的影响

### 图片
- 缺失 alt 文本
- 图片体积过大
- 格式优化建议

### AI 搜索就绪度
- 可引用性得分
- 结构性改进建议
- 权威性信号

## 优先级定义

- **严重（Critical）**：阻碍收录或导致处罚（立即修复）
- **高（High）**：显著影响排名（1 周内修复）
- **中（Medium）**：优化机会（1 个月内修复）
- **低（Low）**：锦上添花（列入待办）

## DataForSEO 集成（可选）

如果 DataForSEO MCP 工具可用，在现有子 agent 之外并行委派 `seo-dataforseo` agent，
用真实数据丰富审计内容：真实 SERP 排名、含垃圾分数的外链画像、页面级分析
（Lighthouse）、商家列表信息，以及 AI 可见性检查（ChatGPT 抓取、LLM 提及情况）。

## Google API 集成（可选）

如果已配置 Google API 凭证（`python3 scripts/google_auth.py --check`），委派
`seo-google` agent 用真实 Google 现场数据丰富审计内容：CrUX 的 Core Web Vitals
（替代仅有实验室数据的估算值）、GSC 的 URL 收录状态、搜索表现数据
（点击、展现、CTR）以及 GA4 自然流量趋势。性能（CWV）这一类别的评分从现场数据中
受益最大。

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| URL 无法访问（DNS 失败、连接被拒绝） | 清晰地报告错误，不要臆测网站内容。建议用户核实 URL 后重试。 |
| robots.txt 阻止爬取 | 报告哪些路径被阻止。仅分析可访问的页面，并在报告中说明这一限制。 |
| 触发限流（429 响应） | 降低并发请求数量。报告部分结果，并说明哪些板块未能完成分析。 |
| 大型站点（500+ 页面）超时 | 在超时限制内截断爬取范围。报告已爬取页面的发现，并预估整站规模。 |
