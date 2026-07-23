---
name: seo-bing
description: Bing Webmaster Tools + IndexNow 扩展。Microsoft Copilot 的引用内容来自 Bing 索引；本技能让 Bing 可见度、链接数据和 IndexNow URL 提交成为一等公民。Bing Webmaster Tools, IndexNow, Microsoft Copilot citations.
metadata:
  version: "2.2.0"
compatibility: "Requires BING_WEBMASTER_API_KEY and (optionally) INDEXNOW_KEY in ~/.claude/settings.json env. Run extensions/bing-webmaster/install.sh to configure."
---

# seo-bing

非 Google 的索引通道。Google 目前仍拒绝 IndexNow（据 Gary Illyes 在
2024-2025 年多期 SOTR 节目中所述），因此本技能专门用于
**Bing/Yandex/Seznam/Naver 索引**以及
**Microsoft Copilot AI 引用**（其内容取自 Bing 索引）。

## 前置条件

- 运行 `extensions/bing-webmaster/install.sh` 或 `install.ps1`。
- 需要一个 Bing Webmaster Tools API key。
- 可选：一个 IndexNow host key（32 位以上字符），发布在
  `INDEXNOW_KEY_LOCATION` 声明的 URL 上。

## 路由

| 命令 | 底层脚本 |
|---|---|
| `/seo bing links <url>` | `python3 scripts/bing_webmaster.py links <url>` |
| `/seo bing compare <urlA> <urlB>` | `python3 scripts/bing_webmaster.py compare <urlA> <urlB>` |
| `/seo bing submit <url>`（单个 URL） | `python3 scripts/indexnow_submit.py --host ... --urls <url>` |
| `/seo bing submit-batch <file>` | `python3 scripts/indexnow_submit.py --urls-file <file>` |
| `/seo bing verify-indexnow` | `python3 scripts/indexnow_submit.py --verify-only` |

## 适用场景

- 用户正在发布新页面，希望获得 Microsoft Copilot 的引用资格
  （即被 Bing 索引收录）。
- 用户希望推动 Bing/Yandex/Seznam/Naver 对新 URL 的索引。
- 用户正在做竞争对手外链分析，需要 Bing 独有的链接数据（Bing
  追踪的一些链接是 Google API 不会呈现的）。

## 跨技能委派

- 对于 Google 索引（模型完全不同——依赖站点地图驱动，不涉及
  IndexNow），使用 `seo-google indexing`。
- 需要多来源外链置信度加权时，回退到已整合 Bing + Moz + CC 的
  `seo-backlinks`。
