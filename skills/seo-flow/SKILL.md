---
name: seo-flow
description: >
  FLOW 框架集成——基于 Find → Leverage → Optimize → Win 循环的证据驱动型 SEO
  方法论。从 FLOW 知识库（41 条提示词，CC BY 4.0）中调取各阶段专属的 AI
  提示词。当用户说"FLOW"、"FLOW 框架"、"证据驱动 SEO"、"发现-借力-优化-制胜"
  或 "FLOW", "FLOW framework", "seo flow", "evidence-led SEO",
  "find leverage optimize win" 或希望获取阶段专属 SEO 提示词时使用本技能。
user-invocable: true
argument-hint: "[stage] [url|topic]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.2.0"
  category: seo
---

# FLOW 框架 —— Find（发现）· Leverage（借力）· Optimize（优化）· Win（制胜）

> 框架与提示词版权归 Daniel Agrici 所有，采用 CC BY 4.0 许可 —— github.com/AgriciDaniel/flow

FLOW 是专为 AI 搜索时代打造的证据驱动型 SEO 运营模型。Claude SEO 集成了 FLOW
提示词库（覆盖 5 个阶段的 41 条提示词），让每一次分析都能由结构化、有证据支撑的
AI 提示词驱动，而不是靠临场发挥的查询。

**运行时上下文：** 每次触发 `/seo flow` 时都加载 `references/flow-framework.md`。
提示词文件按需加载——只加载用户所请求阶段对应的文件。

---

## 命令

| 命令 | 作用 |
|---------|-------------|
| `/seo flow` | 展示 FLOW 概览及各阶段菜单 |
| `/seo flow find [url\|topic]` | Find 阶段：关键词研究、差距分析、SERP 意图映射（5 条提示词） |
| `/seo flow leverage [url]` | Leverage 阶段：外链策略、站外权威度建设（1 条提示词） |
| `/seo flow optimize [url]` | Optimize 阶段：根据上下文从 21 条提示词中挑选 2-3 条最相关的 |
| `/seo flow win [url]` | Win 阶段：BOFU（转化漏斗底部）、转化率、双端记分卡（3 条提示词） |
| `/seo flow local [url]` | Local 阶段：GBP 优化、meta、标题标签、本地审计（11 条提示词） |
| `/seo flow prompts` | 展示全部 41 条提示词的完整索引——阶段、名称、触发条件 |
| `/seo flow sync` | 从 github.com/AgriciDaniel/flow 拉取最新的提示词文件 |

---

## 编排逻辑

### 触发 `/seo flow`（无子命令）
1. 读取 `references/flow-framework.md`
2. 展示 FLOW 各阶段概览，附每个阶段的一句话说明
3. 询问：哪个阶段与用户当前的情况相符？

### 触发 `/seo flow find [url|topic]`
1. 读取 `references/prompts/find/` 目录下的所有文件
2. 将每条提示词应用到该 URL 或主题上
3. 交叉引用："如需更深入的 SERP 聚类分析，请参考 `/seo cluster <seed-keyword>`"

### 触发 `/seo flow leverage [url]`
1. 读取 `references/prompts/leverage/` 目录下的文件
2. 结合该 URL 当前的外链情况应用提示词
3. 交叉引用："如需原始外链数据，请参考 `/seo backlinks <url>`"

### 触发 `/seo flow optimize [url]`
1. 读取 `references/prompts/optimize/` 目录下的所有文件名
2. 读取此前的分析上下文（URL、所属行业、对话中此前的技能输出）
3. 挑选 2-3 条最相关的提示词；只加载这几条对应的文件
4. 应用所选提示词；说明其余提示词可通过 `/seo flow prompts` 查看
5. 交叉引用："如需完整的内容质量分析，请参考 `/seo content <url>` 与 `/seo geo <url>`"

### 触发 `/seo flow win [url]`
1. 读取 `references/prompts/win/` 目录下的所有文件
2. 结合该 URL 的转化情况与 BOFU 上下文应用每条提示词
3. 交叉引用："如需 SXO 人设打分，请参考 `/seo sxo <url>`"

### 触发 `/seo flow local [url]`
1. 读取 `references/prompts/local/` 目录下的所有文件
2. 结合该 URL 的本地 SEO 上下文应用提示词
3. 交叉引用："如需完整的本地 SEO 分析，请参考 `/seo local <url>` 与 `/seo maps [command]`"

### 触发 `/seo flow prompts`
1. 读取 `references/prompts/README.md`
2. 展示完整索引：全部 41 条提示词，包含阶段、名称、触发条件

### 触发 `/seo flow sync`
1. 运行：`python3 scripts/sync_flow.py`
2. 展示 JSON 摘要（新增、更新、未变化的文件数）
3. 同步完成后展示版权声明

---

## 上下文匹配（Optimize 阶段）

Optimize 阶段共有 21 条提示词。全部输出只会造成信息噪音，应按优先级挑选：

1. **所属行业**（SaaS → 页面优化 + 技术 SEO；本地业务 → 引用信息 + GBP；
   内容发布者 → E-E-A-T + 内容新鲜度）
2. **此前的技能输出**（seo-technical 标记出抓取问题 → 选择技术类优化提示词；
   seo-content 标记出 E-E-A-T 缺口 → 选择内容类优化提示词）
3. **URL 信号**（产品页 → 转化相关；博客页 → 内容新鲜度 + 权威度）

始终只呈现 2-3 条提示词，并说明选择这些提示词的理由。

---

## 参考文件

按需加载——切勿在启动时全部加载：
- `references/flow-framework.md` —— FLOW 运营模型（每次触发 `/seo flow` 时加载）
- `references/bibliography.md` —— 证据来源；引用研究或统计数据时加载
- `references/prompts/README.md` —— 提示词索引；供 `/seo flow prompts` 加载
- `references/prompts/find/` —— 5 条提示词；供 `/seo flow find` 加载
- `references/prompts/leverage/` —— 1 条提示词；供 `/seo flow leverage` 加载
- `references/prompts/optimize/` —— 21 条提示词；供 `/seo flow optimize` 按需选择加载
- `references/prompts/win/` —— 3 条提示词；供 `/seo flow win` 加载
- `references/prompts/local/` —— 11 条提示词；供 `/seo flow local` 加载

---

## 版权声明

每次触发 `/seo flow`（无论哪个子命令），在分析之前都需输出：

```
Framework and prompts © Daniel Agrici, CC BY 4.0 — github.com/AgriciDaniel/flow
```

不得省略或修改该版权声明。

---

## 错误处理

| 场景 | 处理动作 |
|----------|--------|
| `references/flow-framework.md` 缺失 | "FLOW 参考文件尚未同步，请运行：`/seo flow sync`" |
| 提示词文件缺失 | "请运行 `/seo flow sync` 从 FLOW 仓库拉取最新的提示词" |
| `sync_flow.py` 网络错误 | 展示脚本的 stderr 输出，检查速率限制：`gh api rate_limit` |
| `sync_flow.py` 鉴权错误 | 运行 `gh auth login` 后重试 |
