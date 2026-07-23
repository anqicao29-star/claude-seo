---
name: seo-hreflang
description: >
  hreflang 与国际化 SEO 的审查、校验与生成工具，检测常见错误，校验语言/地区代码，
  并生成正确的 hreflang 实现方案。当用户提到"hreflang"、"国际化 SEO"、"多语言"、
  "多地区网站"、"语言标签"，或说 "hreflang", "i18n SEO", "international SEO",
  "multi-language", "multi-region", "language tags" 时使用本技能。
user-invocable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# Hreflang 与国际化 SEO

校验现有站点的 hreflang 实现，或为多语言、多地区站点生成正确的 hreflang 标签。
支持 HTML、HTTP 响应头和 XML 站点地图三种实现方式。

## 校验项

### 1. 自我引用标签（Self-Referencing Tags）
- 每个页面都必须包含一个指向自身的 hreflang 标签
- 自我引用的 URL 必须与该页面的 canonical URL 完全一致
- 缺少自我引用标签会导致 Google 忽略整组 hreflang 设置

### 2. 回链标签（Return Tags）
- 如果页面 A 通过 hreflang 链接到页面 B，页面 B 也必须回链到页面 A
- 每一组 hreflang 关系都必须是双向的（A→B 且 B→A）
- 缺少回链标签会使两个页面的 hreflang 信号都失效
- 检查所有语言版本是否互相引用（形成完整的网状结构）

### 3. x-default 标签
- 必需项：用于指定未匹配到语言/地区时的回退页面
- 通常指向语言选择页或英文版本
- 每组备用语言中只能有一个 x-default
- 其他所有语言版本也必须回链到该 x-default 页面

### 4. 语言代码校验
- 必须使用 ISO 639-1 双字母代码（例如 `en`、`fr`、`de`、`ja`）
- 常见错误：
  - 用 `eng` 代替 `en`（这是 ISO 639-2 代码，hreflang 不支持）
  - 用 `jp` 代替 `ja`（日语的正确代码是 `ja`）
  - `zh` 未加地区限定（含义不明确，应使用 `zh-Hans` 或 `zh-Hant`）

### 5. 地区代码校验
- 可选的地区限定符使用 ISO 3166-1 Alpha-2 代码（例如 `en-US`、`en-GB`、`pt-BR`）
- 格式为 `language-REGION`（语言小写，地区大写）
- 常见错误：
  - 用 `en-uk` 代替 `en-GB`（UK 不是有效的 ISO 3166-1 代码）
  - `es-LA`（拉丁美洲不是一个国家，应使用具体国家代码）
  - 地区代码缺少语言前缀

### 6. Canonical URL 一致性
- hreflang 标签只能出现在 canonical URL 上
- 如果页面的 `rel=canonical` 指向其他 URL，该页面上的 hreflang 会被忽略
- canonical URL 与 hreflang URL 必须完全一致（包括末尾斜杠）
- 非 canonical 页面不应出现在任何 hreflang 集合中

### 7. 协议一致性
- 同一组 hreflang 中的所有 URL 必须使用相同协议（HTTPS 或 HTTP）
- 混用 HTTP/HTTPS 会导致校验失败
- 迁移到 HTTPS 后，需要同步更新所有 hreflang 标签为 HTTPS

### 8. 跨域支持
- hreflang 支持跨不同域名使用（例如 example.com 与 example.de）
- 跨域 hreflang 需要两个域名都设置回链标签
- 确认两个域名都已在 Google Search Console 完成验证
- 跨域场景建议采用基于站点地图的实现方式

## 常见错误汇总

| 问题 | 严重程度 | 修复方式 |
|-------|----------|-----|
| 缺少自我引用标签 | 严重 | 添加指向页面自身 URL 的 hreflang |
| 缺少回链标签（A→B 但无 B→A） | 严重 | 在所有备用语言页面上添加对应的回链标签 |
| 缺少 x-default | 高 | 添加指向回退页/语言选择页的 x-default |
| 语言代码无效（如 `eng`） | 高 | 使用 ISO 639-1 双字母代码 |
| 地区代码无效（如 `en-uk`） | 高 | 使用 ISO 3166-1 Alpha-2 代码 |
| hreflang 出现在非 canonical URL 上 | 高 | 将 hreflang 仅保留在 canonical URL 上 |
| URL 协议混用 HTTP/HTTPS | 中 | 统一所有 URL 为 HTTPS |
| 末尾斜杠不一致 | 中 | 与 canonical URL 格式保持完全一致 |
| HTML 与站点地图中同时存在 hreflang | 低 | 二选一实现（大型站点建议使用站点地图） |
| 需要地区限定却只用了语言代码 | 低 | 针对地域定向内容补充地区限定符 |

## 实现方式

### 方式一：HTML Link 标签
适用场景：每个页面语言/地区变体少于 50 个的站点。

```html
<link rel="alternate" hreflang="en-US" href="https://example.com/page" />
<link rel="alternate" hreflang="en-GB" href="https://example.co.uk/page" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

放置在 `<head>` 区块中。每个页面都必须包含全部备用语言版本（含自身）。

### 方式二：HTTP 响应头
适用场景：非 HTML 文件（PDF、文档等）。

```
Link: <https://example.com/page>; rel="alternate"; hreflang="en-US",
      <https://example.com/fr/page>; rel="alternate"; hreflang="fr",
      <https://example.com/page>; rel="alternate"; hreflang="x-default"
```

通过服务器配置或 CDN 规则设置。

### 方式三：XML 站点地图（推荐用于大型站点）
适用场景：语言变体较多、涉及跨域，或页面数超过 50 个的站点。

详见下方的「Hreflang 站点地图生成」章节。

### 三种方式对比
| 方式 | 适用场景 | 优点 | 缺点 |
|--------|----------|------|------|
| HTML link 标签 | 小型站点（少于 50 个变体） | 实现简单，源码中可见 | `<head>` 会变臃肿，规模化后难维护 |
| HTTP 响应头 | 非 HTML 文件 | 适用于 PDF、图片等 | 服务器配置较复杂，HTML 中不可见 |
| XML 站点地图 | 大型站点、跨域场景 | 可扩展、集中管理 | 页面上不可见，需要维护站点地图 |

## Hreflang 生成流程

### 处理流程
1. **检测语言**：扫描站点中的语言标识（URL 路径、子域名、TLD、HTML lang 属性）
2. **映射对应页面**：匹配不同语言/地区版本下的对应页面
3. **校验语言代码**：依据 ISO 639-1 和 ISO 3166-1 逐一核对所有代码
4. **生成标签**：为每个页面生成 hreflang 标签（含自我引用）
5. **核实回链标签**：确认所有关系均为双向
6. **添加 x-default**：为每组页面设置回退版本
7. **输出**：生成实现代码（HTML、HTTP 响应头或站点地图 XML）

## Hreflang 站点地图生成

### 带 Hreflang 的站点地图
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/page</loc>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://example.com/page" />
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.de/page" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/page" />
  </url>
  <url>
    <loc>https://example.com/fr/page</loc>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://example.com/page" />
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.de/page" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/page" />
  </url>
</urlset>
```

关键规则：
- 必须声明 `xmlns:xhtml` 命名空间
- 每个 `<url>` 条目都必须包含全部语言版本（含自身）
- 每个语言版本都要作为独立的 `<url>` 条目出现，并携带完整的一组标签
- 每个站点地图文件按 50,000 条 URL 拆分

## 输出

### Hreflang 校验报告

#### 概览
- 扫描页面总数：XX
- 检测到的语言变体数：XX
- 发现问题数：XX（严重：X，高：X，中：X，低：X）

#### 校验结果
| 语言 | URL | 自我引用 | 回链标签 | x-default | 状态 |
|----------|-----|----------|-------------|-----------|--------|
| en-US | https://... | ✅ | ✅ | ✅ | ✅ |
| fr | https://... | ❌ | ⚠️ | ✅ | ❌ |
| de | https://... | ✅ | ❌ | ✅ | ❌ |

### 生成的 Hreflang 标签
- HTML `<link>` 标签（若选择 HTML 方式）
- HTTP 响应头值（若选择响应头方式）
- `hreflang-sitemap.xml`（若选择站点地图方式）

### 建议
- 需要补充的缺失实现
- 需要修正的错误代码
- 实现方式迁移建议（例如站点规模扩大后从 HTML 迁移到站点地图）

## 文化适配评估

分析多语言站点时，不能只停留在 hreflang 技术校验层面，还要评估内容是否针对每个目标市场做了文化适配。

加载 `references/cultural-profiles.md` 获取预置的文化画像（DACH 德语区、法语区、西语区、日本市场）。

**评估步骤：**
1. 确认所有语言版本及其目标市场
2. 加载相应的文化画像
3. 检查 CTA 是否符合当地文化预期（直接型 vs 含蓄型）
4. 检查信任信号是否符合当地习惯（资质认证、法律页面等）
5. 检查本地化页面上是否出现不相关的境外品牌引用
6. 检查数字、日期、货币格式是否一致
7. 将文化适配问题标记为中等严重程度

**输出：** 每个语言版本的文化适配得分（0-100），并附具体发现。

## 内容一致性（Parity）审查

**命令：** `/seo hreflang audit <directory-or-url>`

对站点或本地内容目录中所有语言版本之间的内容一致性进行审查。

加载 `references/content-parity.md` 获取完整的一致性矩阵与评分方法。

**检查内容：**
- 各声明语言版本的页面是否都存在
- 各版本章节结构是否对等（H2/H3 数量）
- SEO 元素一致性（标题、meta、schema 本地化）
- 字数比例校验（德语通常应比英语长 25-35%，日语应短 10-25%）
- 时效性追踪（通过时间戳检测过期翻译）
- 文化标记扫描（境外品牌、错误的法律引用、未翻译的元素）

**输出：** 一致性矩阵表，含各页面得分及优先行动项。

## 本地化格式校验

加载 `references/locale-formats.md` 获取各地区的数字、日期、货币、地址、电话格式参考表。

**检查项：**
- 数字格式一致性（例如 de-DE 页面上 "1,000.00" 应写作 "1.000,00"）
- 日期格式是否符合当地习惯
- 货币符号及位置是否符合目标市场规范
- 电话号码是否使用带正确国家代码的国际格式

## 参考文件

按需加载（不要在启动时全部加载）：
- `references/cultural-profiles.md`：DACH 德语区、法语区、西语区、日本市场的文化适配画像
- `references/locale-formats.md`：各地区的数字、日期、货币、地址、电话格式对照表
- `references/content-parity.md`：内容一致性审查方法与评分标准

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| URL 无法访问（DNS 失败、连接被拒绝） | 明确报告错误，不要臆测站点结构，建议用户核实 URL 后重试。 |
| 未发现任何 hreflang 标签 | 报告该情况，检查其他国际化信号（子目录、子域名、ccTLD），并推荐合适的 hreflang 实现方式。 |
| 检测到无效的语言/地区代码 | 逐条列出无效代码及正确替换值，提供可直接实施的修正版 hreflang 标签集。 |
| 该语言没有对应的文化画像 | 使用 cultural-profiles.md 中的默认画像清单，并注明该评估基于通用准则而非预置画像。 |
| 内容一致性审查目录为空 | 报告未找到内容文件，建议核实目录路径，或改为提供 URL 进行线上站点分析。 |
