---
name: seo-ahrefs
description: Ahrefs API 数据分析师（扩展）。通过官方 @ahrefs/mcp@0.0.11 服务器读取外链来源域名、反向链接、自然关键词及内容浏览器（Content Explorer）数据。可与 seo-backlinks 搭配，实现多来源置信度加权。Ahrefs API analyst, referring domains, backlinks, organic keywords.
metadata:
  version: "2.2.0"
compatibility: "Requires the official @ahrefs/mcp@0.0.11 server (installed by extensions/ahrefs/install.sh)."
---

# seo-ahrefs

通过官方 `@ahrefs/mcp@0.0.11` 服务器获取 Ahrefs 实时数据。

## 前置条件

- 使用本技能前，请先运行 `extensions/ahrefs/install.sh`（Linux/macOS）或 `install.ps1`（Windows）。
- 需要一个 Ahrefs API token（https://ahrefs.com/api）。
- MCP 服务器需要 `$PATH` 中存在 Node 18+。

在调用任何 Ahrefs 工具前，请先确认本会话中已能使用某个 Ahrefs MCP
工具，以此验证 MCP 已连接。若工具不可用，请告知用户该扩展尚未安装，
并提供上方的安装命令。

## 路由

| 命令 | 作用 |
|---|---|
| `/seo ahrefs metrics <url>` | 域名/URL 评级、外链来源域名数量、自然流量估算 |
| `/seo ahrefs backlinks <url>` | 主要外链来源域名、锚文本分布、follow/nofollow 比例 |
| `/seo ahrefs organic <url>` | 自然关键词、排名分布、按国家划分的流量 |
| `/seo ahrefs content <topic>` | Content Explorer 热门结果、社交分享数、外链来源域名 |

## 输出规范

- 每项指标都要注明数据来源："Ahrefs (live, confidence 1.00)"。
- 当 Ahrefs 与 Moz 在同一指标上出现分歧时，以 Ahrefs 为准，并在报告中注明差异。
- 有害链接评估：将 Ahrefs Spam Score 与现有 seo-backlinks 的 Common Crawl + verify 爬虫信号结合使用。

## 跨技能委派

- 若需要跨 Moz + Bing + Common Crawl + Ahrefs 的多来源置信度加权，交回 `seo-backlinks` 处理。
- 若涉及 Ahrefs 与 DataForSEO 重叠的 SERP 特征分析，优先使用 DataForSEO 获取实时 SERP 数据。

## 成本护栏

Ahrefs API 用量按单位计费。在运行批量任务（>= 50 个 URL）之前：

1. 使用 `python3 scripts/dataforseo_costs.py` 估算成本（该成本追踪模块是通用的，支持 Ahrefs 的单位计费）。
2. 将估算结果提交给编排器（orchestrator）。
3. 每次调用后记录实际花费。

这与 seo-dataforseo 技能使用的工作流相同。
