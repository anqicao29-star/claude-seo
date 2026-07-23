---
name: seo-drift
description: >
  SEO 漂移监控（SEO drift monitoring）：捕获页面 SEO 关键元素的基线快照，检测变化，
  并持续追踪各项回归问题。相当于给 SEO 做版本管理——建立基线（baseline）、比对差异、
  追踪你的页面 SEO 变化。当用户说"SEO 漂移"、"SEO drift"、"建立基线"、"baseline"、
  "追踪变化"、"track changes"、"是不是出问题了"、"did anything break"、"SEO 回归"、
  "SEO regression"、"对比 SEO"、"compare SEO"、"前后对比"、"before and after"、
  "监控 SEO 变化"、"monitor SEO changes"、或"部署检查"、"deployment check" 时使用本技能。
user-invocable: true
argument-hint: "baseline|compare|history <url>"
license: MIT
metadata:
  author: AgriciDaniel
  original_author: "Dan Colta (Pro Hub Challenge)"
  version: "2.2.0"
  category: seo
---

# SEO 漂移监控（2026 年 4 月）

为你的 SEO 打造一套版本管理机制：捕获基线、检测回归、持续追踪变化。

---

## 命令

| 命令 | 用途 |
|---------|---------|
| `/seo drift baseline <url>` | 将当前页面的 SEO 状态捕获为一份「已知良好」快照 |
| `/seo drift compare <url>` | 将当前页面状态与已存储的基线进行比对 |
| `/seo drift history <url>` | 展示变更历史与历次比对记录 |

---

## 捕获内容

每份基线都会记录以下 SEO 关键元素：

| 元素 | 字段 | 来源 |
|---------|-------|--------|
| Title 标签 | `title` | `parse_html.py` |
| Meta 描述（Meta description） | `meta_description` | `parse_html.py` |
| 规范链接（Canonical URL） | `canonical` | `parse_html.py` |
| Robots 指令 | `meta_robots` | `parse_html.py` |
| H1 标题 | `h1`（数组） | `parse_html.py` |
| H2 标题 | `h2`（数组） | `parse_html.py` |
| H3 标题 | `h3`（数组） | `parse_html.py` |
| JSON-LD 结构化数据 | `schema`（数组） | `parse_html.py` |
| Open Graph 标签 | `open_graph`（字典） | `parse_html.py` |
| Core Web Vitals | `cwv`（字典） | `pagespeed_check.py` |
| HTTP 状态码 | `status_code` | `fetch_page.py` |
| HTML 内容哈希 | `html_hash`（SHA-256） | 计算得出 |
| 结构化数据哈希 | `schema_hash`（SHA-256） | 计算得出 |

---

## 比对原理

比对引擎共应用 **17 条规则、覆盖 3 个严重级别**。完整规则集（含阈值、建议操作及跨技能关联）
请加载 `references/comparison-rules.md`。

### 严重级别

| 级别 | 含义 | 响应时限 |
|-------|---------|---------------|
| **CRITICAL（严重）** | 破坏 SEO 的变更，很可能导致流量下滑 | 立即处理 |
| **WARNING（警告）** | 存在潜在影响，需要进一步排查 | 一周内处理 |
| **INFO（提示）** | 仅作知悉，可能是有意为之的改动 | 有空时查看 |

---

## 数据存储

所有数据均以 SQLite 形式存储在本地：

```
~/.cache/claude-seo/drift/baselines.db
```

### 数据表

- **baselines**：包含全部 SEO 元素的快照记录
- **comparisons**：差异比对结果，含触发的规则与严重级别

URL 归一化处理确保匹配的一致性：协议/主机名统一转为小写、去除默认端口（80/443）、
对查询参数排序、移除 UTM 参数、去掉结尾斜杠。

---

## 命令：`baseline`

捕获页面当前状态并存储。

**执行步骤：**
1. 校验 URL（通过 `google_auth.validate_url()` 提供 SSRF 防护）
2. 通过 `scripts/fetch_page.py` 抓取页面
3. 通过 `scripts/parse_html.py` 解析 HTML
4. 可选：通过 `scripts/pagespeed_check.py` 获取 Core Web Vitals 数据（使用 `--skip-cwv` 可跳过）
5. 对 HTML 正文与结构化数据内容做哈希（SHA-256）
6. 将快照存入 SQLite

**执行命令：**
```bash
python3 scripts/drift_baseline.py <url>
python3 scripts/drift_baseline.py <url> --skip-cwv
```

**输出：** 包含基线 ID、时间戳、URL 及所捕获元素摘要的 JSON。

---

## 命令：`compare`

抓取当前页面状态，并与最近一次基线进行差异比对。

**执行步骤：**
1. 校验 URL
2. 从 SQLite 中加载最近的基线（或指定的 `--baseline-id`）
3. 抓取并解析当前页面状态
4. 运行全部 17 条比对规则
5. 按严重级别对发现的问题分类
6. 存储比对结果
7. 输出 JSON 差异报告

**执行命令：**
```bash
python3 scripts/drift_compare.py <url>
python3 scripts/drift_compare.py <url> --baseline-id 5
python3 scripts/drift_compare.py <url> --skip-cwv
```

**输出：** 包含所有触发规则、新旧数值、严重级别及建议操作的 JSON。

比对完成后，可主动提出生成 HTML 报告：
```bash
python3 scripts/drift_report.py <comparison_json_file> --output drift-report.html
```

---

## 命令：`history`

展示某个 URL 的全部基线与比对记录。

**执行命令：**
```bash
python3 scripts/drift_history.py <url>
python3 scripts/drift_history.py <url> --limit 10
```

**输出：** 基线的 JSON 数组（按时间倒序排列），含时间戳与比对摘要。

---

## 跨技能协同

检测到漂移后，应推荐对应的专项技能：

| 发现的问题 | 建议操作 |
|---------|----------------|
| 结构化数据被移除或修改 | 运行 `/seo schema <url>` 进行完整校验 |
| Core Web Vitals 出现回归 | 运行 `/seo technical <url>` 进行性能审计 |
| Title 或 Meta 描述发生变化 | 运行 `/seo page <url>` 进行内容分析 |
| 规范链接（Canonical）被修改或移除 | 运行 `/seo technical <url>` 进行可索引性检查 |
| 新增了 Noindex 标签 | 运行 `/seo technical <url>` 进行可爬取性审计 |
| H1/标题层级结构发生变化 | 运行 `/seo content <url>` 进行 E-E-A-T 审查 |
| OG 标签被移除 | 运行 `/seo page <url>` 进行社交分享分析 |
| 状态码变为错误状态 | 运行 `/seo technical <url>` 进行全面诊断 |

---

## 错误处理

| 场景 | 处理方式 |
|----------|--------|
| URL 无法访问 | 报告 `fetch_page.py` 返回的错误。不要臆测页面状态，建议用户核实 URL。 |
| 该 URL 尚无基线 | 告知用户，并建议先运行 `baseline` 命令。 |
| 被 SSRF 防护拦截（私有 IP） | 报告 `validate_url()` 的拒绝原因，绝不能绕过该防护。 |
| SQLite 数据库不存在 | 首次使用时自动创建，不视为错误。 |
| Core Web Vitals 获取失败（无 API key） | CWV 相关字段存为 `null`，比对时跳过相关规则。 |
| 页面返回 4xx/5xx | 仍然作为基线捕获（状态码本身就是被追踪的字段）。 |
| 存在多份基线 | 默认使用最近一份，除非指定了 `--baseline-id`。 |

---

## 安全性

- **所有 URL 抓取**均通过 `scripts/fetch_page.py` 完成，该脚本强制执行 SSRF 防护
  （拦截私有 IP、环回地址、保留地址段、GCP 元数据端点）
- **不使用 curl，不使用 subprocess 发起 HTTP 请求** —— 只走项目内经过校验的抓取流程
- **所有 SQLite 查询**均使用参数化占位符（`?`），绝不使用字符串拼接
- **TLS 始终校验** —— 整条流程中任何位置都不会出现 `verify=False`

---

## 典型工作流

### 部署前后检查
```
/seo drift baseline https://example.com     # Before deploy
# ... deploy happens ...
/seo drift compare https://example.com      # After deploy
```

### 持续监控
```
/seo drift baseline https://example.com     # Initial capture
# ... weeks later ...
/seo drift compare https://example.com      # Check for drift
/seo drift history https://example.com      # Review all changes
```

### 排查流量下滑
```
/seo drift compare https://example.com      # What changed?
/seo drift history https://example.com      # When did it change?
```
