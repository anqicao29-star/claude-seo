---
name: seo-seranking
description: SE Ranking AI 可见度分析师（扩展）。一次查询即可追踪品牌在 ChatGPT、Gemini、Perplexity、AI Overviews 和 AI Mode 中的 AI Share-of-Voice（AI 声量占比）。根据 v2 差距分析，这是影响力最高的新扩展——没有其他供应商能在单一 API 中覆盖全部 5 个 AI 平台。SE Ranking AI visibility, Share-of-Voice, ChatGPT, Gemini, Perplexity, AI Overviews, AI Mode.
metadata:
  version: "2.2.0"
compatibility: "Requires an SE Ranking API key (set SERANKING_API_KEY by running extensions/seranking/install.sh)."
---

# seo-seranking

通过 SE Ranking REST API 进行实时 AI 可见度追踪。

## 前置条件

- 运行 `extensions/seranking/install.sh`（或 `install.ps1`）。
- 需要一个 SE Ranking API key（https://seranking.com/api）。
- 在发起任何调用之前，先确认 `~/.claude/settings.json` 的 `env.` 下存在 `SERANKING_API_KEY`。若不存在，请告知用户运行安装脚本。

## 路由

| 命令 | 用途 |
|---|---|
| `/seo seranking ai-visibility <brand>` | `brand` 在 ChatGPT、Gemini、Perplexity、AI Overviews、AI Mode 中的声量占比（share-of-voice） |
| `/seo seranking serp <keyword>` | 自然排名前 100 位 + SERP 特征 |
| `/seo seranking backlinks <url>` | 外链画像（Ahrefs / DataForSEO 的免费层替代方案） |
| `/seo seranking competitors <url>` | 前 10 名自然排名竞争对手及共享关键词差距 |

## AI Share-of-Voice 评分

SE Ranking 会在一组可配置的提示词（prompt）集合上，对每个 AI 平台的
回答进行品牌提及采样。其打分逻辑与 Profound / Peec AI 相同，只是
整合进了一个 MCP/API。输出字段：

- `chatgpt_sov`：品牌出现在采样提示词回答中的百分比。
- `gemini_sov`：针对 Google Gemini 的同类指标。
- `perplexity_sov`：针对 Perplexity 的同类指标。
- `ai_overviews_sov`：品牌在 Google AI Overviews 中的引用率。
- `ai_mode_sov`：品牌在 Google AI Mode 中的引用率（优先支持美式英语）。

每项都应以百分比形式呈现，并根据样本量给出置信度说明。

## 成本护栏

SE Ranking API 采用单位计费。单次 AI 可见度查询约消耗 5 个单位
（每个平台 1 个）。使用 `scripts/dataforseo_costs.py` 记录各供应商的花费。

## 跨技能委派

- 需要传统外链分析 + 内容审计时，回退到 `seo-backlinks` / `seo-content`。
- 需要针对单一平台的深入分析（仅 ChatGPT、仅 Perplexity）时，优先使用专门的 `seo-geo` 技能，它提供品牌提及相关性（Brand Mention Correlation）指导。
