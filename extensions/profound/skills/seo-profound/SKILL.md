---
name: seo-profound
description: Profound LLM 引用追踪器（扩展）。以时间序列形式追踪品牌在 ChatGPT、Perplexity 及其他 LLM 中的引用率。可与 seo-seranking 搭配，实现 AI 可见度的三角验证覆盖。Profound LLM citation tracker, time-series brand citation rates.
metadata:
  version: "2.2.0"
compatibility: "Requires a Profound API key (set PROFOUND_API_KEY by running extensions/profound/install.sh)."
---

# seo-profound

Profound 是专为 LLM 品牌提及追踪打造的工具。SE Ranking 是按需采样
提示词，而 Profound 则持续轮询并生成时间序列数据，使趋势变化
（周环比、月环比）成为一等能力。

## 前置条件

- 运行 `extensions/profound/install.sh` 或 `install.ps1`。
- 需要 Profound API key。
- 每次调用工具前，检查 `~/.claude/settings.json` 中是否有 `env.PROFOUND_API_KEY`。

## 路由

| 命令 | 用途 |
|---|---|
| `/seo profound citations <brand>` | 各 LLM 当前的引用率 + 30 天趋势 |
| `/seo profound prompts <brand>` | 能够（或未能）呈现该品牌的热门提示词 |
| `/seo profound competitors <brand>` | 在相同提示词下与该品牌一同被引用的品牌 |
| `/seo profound alerts <brand>` | 相对 7 天基线的激增/骤降告警 |

## 输出规范

- 每项指标都要注明 Profound 来源："Profound (live, confidence 0.90)"。
- Profound 原生覆盖 ChatGPT + Perplexity；如需 Gemini / AI
  Overviews / AI Mode 的覆盖，交由 `seo-seranking` 处理。
- 对于 Google AI Overviews 的引用率，若有条件也应交叉核对
  `seo-dataforseo` 的 AI 可见度工具。

## 跨技能委派

- 需要端到端 AI 搜索审计（段落可引用性 + 品牌提及 + 平台专项调优）时，交回 `seo-geo`。
- 需要提示词集设计 + 被引用内容中的 AI Cleanup 模式检测时，回退到 `seo-content`。
