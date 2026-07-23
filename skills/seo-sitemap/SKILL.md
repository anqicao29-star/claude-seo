---
name: seo-sitemap
description: >
  分析既有 XML 站点地图或使用行业模板生成新的站点地图，校验格式、URL
  与结构。当用户说"站点地图"、"生成 sitemap"、"sitemap 问题" 或
  "sitemap", "generate sitemap", "sitemap issues", "XML sitemap" 时使用本技能。
user-invocable: true
argument-hint: "[url or generate]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# 站点地图分析与生成

## 模式 1：分析既有 Sitemap

### 校验项
- XML 格式是否有效
- 单文件 URL 数量 <50,000（协议限制）
- 所有 URL 是否返回 HTTP 200
- `<lastmod>` 日期是否准确（不是全部相同）
- 不存在已废弃标签：`<priority>` 和 `<changefreq>` 已被 Google 忽略
- Sitemap 是否在 robots.txt 中注册
- 对比已抓取页面与 sitemap，标记缺失的页面

### 质量信号
- 若 URL 超过 5 万，应使用 sitemap 索引文件
- 按内容类型拆分（页面、文章、图片、视频）
- sitemap 中不应包含非规范（non-canonical）URL
- sitemap 中不应包含已设为 noindex 的 URL
- sitemap 中不应包含被重定向的 URL
- 仅使用 HTTPS URL（不使用 HTTP）

### 常见问题
| 问题 | 严重程度 | 修复方式 |
|-------|----------|-----|
| 单文件超过 5 万个 URL | 严重 | 使用 sitemap 索引拆分 |
| 非 200 状态的 URL | 高 | 移除或修复失效 URL |
| 包含 noindex 的 URL | 高 | 从 sitemap 中移除 |
| 包含被重定向的 URL | 中 | 更新为最终跳转后的 URL |
| lastmod 全部相同 | 低 | 使用真实的修改日期 |
| 使用了 priority/changefreq | 提示 | 可以移除（Google 已忽略这两个标签） |

## 模式 2：生成新 Sitemap

### 流程
1. 询问业务类型（或从现有站点自动识别）
2. 从 `../seo-plan/assets/` 目录加载行业模板
3. 与用户交互式规划结构
4. 应用质量门槛：
   - ⚠️ 警告：地区页面达到 30+ 个（需 60%+ 独有内容）
   - 🛑 硬性停止：地区页面达到 50+ 个（需提供正当理由）
5. 生成有效的 XML 输出
6. 超过 5 万 URL 时使用 sitemap 索引拆分
7. 生成 STRUCTURE.md 文档

### 可以安全批量生产的程序化页面
✅ 集成页面（配有真实的接入文档）
✅ 模板/工具页面（配有可下载内容）
✅ 词汇表页面（200 字以上的定义）
✅ 产品页面（独有的规格、评价）
✅ 用户主页（用户生成内容）

### 存在处罚风险（不应批量生产）
❌ 仅替换城市名的地区页面
❌ 缺乏行业针对性价值的"[行业]最佳[工具]"页面
❌ 没有真实对比数据的"[竞品]替代方案"页面
❌ 缺乏人工审核和独特价值的 AI 生成页面

## Sitemap 格式

### 标准 Sitemap
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <lastmod>2026-02-07</lastmod>
  </url>
</urlset>
```

### Sitemap 索引（适用于超过 5 万个 URL 的情况）
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-pages.xml</loc>
    <lastmod>2026-02-07</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-posts.xml</loc>
    <lastmod>2026-02-07</lastmod>
  </sitemap>
</sitemapindex>
```

## 错误处理

- **URL 无法访问**：报告 HTTP 状态码，建议检查站点是否正常运行
- **未找到 sitemap**：在报告"未找到"之前，先检查常见位置（/sitemap.xml、/sitemap_index.xml、robots.txt 中的引用）
- **XML 格式无效**：报告具体的解析错误及行号
- **检测到限流**：降速重试并报告部分结果，附注重试时机建议

## 输出

### 分析模式
- `VALIDATION-REPORT.md`：分析结果
- 带严重程度标注的问题清单
- 优化建议

### 生成模式
- `sitemap.xml`（或带索引的拆分文件）
- `STRUCTURE.md`：站点架构文档
- URL 数量与组织结构摘要
