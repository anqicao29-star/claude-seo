# 封测门槛完整回归证据

- 日期：2026-11-12
- 项目：Claude SEO 本地工作台
- 范围：`BETA-01`、`BETA-02`、`BETA-03` 以及工程完整测试
- 结论：本机可执行项已全部跑完；核心主链路通过，但发现 3 个封测前代码缺陷和 3 个外部/范围阻塞项

## 测试环境

- macOS，Apple Silicon
- 工作台服务：`http://127.0.0.1:7777/`
- 系统 Python：3.9.6
- 完整测试临时环境：Python 3.12
- Codex CLI：0.167.2
- Codex 模型：`gpt-6.1-sol`
- Codex 登录：ChatGPT 订阅登录有效
- Claude Code：2.1.250
- Claude 模型：Sonnet
- Claude 登录：有效

## 结果矩阵

| 项目 | 结果 | 证据或说明 |
|---|---|---|
| 工作台专项自动测试 | 通过 | 61 项通过，0 失败 |
| 全工程测试 | 未全绿 | Python 3.12 环境中，排除缺少 Pango 的 Google PDF 单项后，398 项通过、10 项失败，另有 17 个子测试通过 |
| Skill 可移植性检查 | 通过 | 33 个 `SKILL.md`，0 错误、0 警告 |
| ZIP 压缩完整性 | 通过 | `unzip -t` 无错误 |
| ZIP 内容完整性 | 先失败后修正 | 首个 ZIP 漏掉新加入 Git 的 `write_previews.py`；重新打包后确认文件存在 |
| 干净目录解压启动 | 通过 | 在 `/tmp` 全新目录、空白 HOME 中启动成功 |
| 缺少 Runtime 检测 | 通过 | 能识别 Codex/Claude 未安装或未登录状态 |
| 缺少 Claude 时的网页操作提示 | 失败 | 页面显示“点击顶部登录”，但 Claude 未安装时顶部登录按钮不存在 |
| 默认只读真实写入拦截 | 通过 | Codex 尝试创建 `read-only-guard-e2e.txt`，系统拒绝写入，原目录无文件 |
| 用户取消真实任务 | 通过 | 返回唯一终态 `task.cancelled` |
| 真实任务超时提示 | 通过 | 30 秒后返回 `task.timeout` 和用户可读提示 |
| 超时进程清理 | 失败 | Codex 主进程退出后，测试命令 `sleep 120` 子进程仍残留，已手动清理 |
| Claude 文章路由 | 通过 | 事件明确为 `runtime: claude`；H1、3 个 H2、结论和 Markdown 正常，无推广尾巴 |
| 安全写入预览 | 通过 | 确认前原目录无文件，Diff 正确 |
| 服务重启后恢复预览 | 通过 | 重启 7777 服务后仍能读取 pending 预览 |
| 确认写入与撤销 | 通过 | 应用后内容准确，撤销后测试文件消失 |
| 另一台物理电脑 | 未测试 | 当前没有第二台非开发电脑执行环境 |
| 外部授权目录选择 | 未测试 | 功能尚未实现，当前只操作工作台项目目录 |
| 订阅商业封装合规 | 未通过 | 官方资料不足以支持当前产品直接对外承诺，需切换官方商业认证/API 方案或取得书面确认 |

## 全工程 10 项失败分类

这些失败不是本地聊天工作台主链路的 61 项专项测试，但说明上游 SEO 工程还不是全绿状态。

1. 文档和清单漂移 5 项：
   - `seo-audit` 标题结构与测试约定不一致。
   - `seo-google` 中英文术语与测试约定不一致。
   - 主编排 Skill 的子 Skill 清单解析为空。
   - 主编排 Skill 的子 Agent 清单解析为空。
   - `seo-flow` 已有中文安全警告，但缺少测试要求的英文原句。
2. 网络/DNS 环境 3 项：
   - 当前网络把 `example.com` 解析到 `198.18.1.165`，SSRF 防护正确拒绝，导致 3 个依赖该地址的测试失败。
3. GitHub 限流 2 项：
   - FLOW 同步 dry-run 两项因 GitHub API 返回 403 rate limit 失败。
4. Google PDF 报告 1 项未收集：
   - Python 包已安装，但 macOS 缺少 WeasyPrint 所需 Pango/GObject 原生库。本项不属于当前封测门槛。

## 封测前必须修复

1. 超时/取消必须清理整个命令进程树，不能留下后台子进程。
2. Claude/Codex 未安装与未登录必须分开提示，并给出可执行安装步骤。
3. 启动器必须真正检测 Python 版本，不能只检查 `python3` 命令是否存在。

## 仍需外部条件

1. 在至少一台非开发电脑完成真实安装、登录、对话和安全写入测试。
2. 实现并验收用户主动选择外部授权目录。
3. 明确商业认证路线：OpenAI 的 Sign in with ChatGPT/合作方流程或 API Key，以及 Anthropic Claude for Work/API 商业方案。

## 分发包

- 路径：`dist/claude-seo-workbench-local.zip`
- SHA-256：`074df02994fb48cf43857d5a2c6001cd4655241cc9e3158e8b80715d8c2ed9f7`
- 已确认包含：`ui/workbench/write_previews.py`

## 官方资料

- OpenAI Codex App Server 认证：https://learn.chatgpt.com/docs/app-server#auth-endpoints
- Anthropic Legal Center：https://www.anthropic.com/legal
- Claude Code 安装与认证：https://code.claude.com/docs/en/getting-started
- Claude 订阅与 API 计费边界：https://support.claude.com/en/articles/9876003-why-is-claude-api-usage-billed-separately-from-my-paid-claude-plan
