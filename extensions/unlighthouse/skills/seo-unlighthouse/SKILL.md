---
name: seo-unlighthouse
description: 通过 MIT 许可的 Unlighthouse CLI 进行多页面 Lighthouse 审计。是对整站每个 URL 运行 PageSpeed 的免费替代方案——不消耗 API 配额，完全本地运行。Multi-page Lighthouse audit, Unlighthouse CLI, free-tier alternative.
metadata:
  version: "2.2.0"
compatibility: "Requires Node 18+ and the unlighthouse npm package. Run extensions/unlighthouse/install.sh to pre-warm."
---

# seo-unlighthouse

对站点内每个 URL（数量上限可配置）运行 Lighthouse 并汇总结果。
适用场景：

- PageSpeed Insights 的免费配额（每天 2.5 万次请求）不足以覆盖大型站点。
- 需要离线 / 本地的 CWV 测量（CI 集成、受限环境）。
- 部署后需要快速做一次全站范围的回归检查。

## 前置条件

- 运行 `extensions/unlighthouse/install.sh`（无需 API key）。
- `$PATH` 中需要 Node 18+。

## 路由

| 命令 | 效果 |
|---|---|
| `/seo unlighthouse <url>` | 移动端审计，最多 200 条路由，JSON+HTML 报告输出到临时目录 |
| `/seo unlighthouse <url> --device desktop` | 桌面端形态 |
| `/seo unlighthouse <url> --max-routes 50 --output-dir ./reports` | 限制数量并持久化保存 |

所有参数都会转发给 `scripts/unlighthouse_run.py`，由它负责 url_safety
预检和子进程超时管理。

## 输出处理

包装脚本会读取 Unlighthouse 输出目录中的 `ci-result.json` 并解析
返回。汇总字段包括：

- `score.performance`（各受审路由的中位数）
- `score.accessibility`、`score.bestPractices`、`score.seo`
- 按路由细分的数据可在 `<output_dir>/ci-result.json` 中查看

## 跨技能委派

- 需要单 URL 现场数据（CrUX）时，使用 `seo-google psi` / `seo-google crux`。
- 需要对慢页面做 LCP 子阶段拆解时，使用
  `scripts/lcp_subparts.py` 工作流（Phase C）。
