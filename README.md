# Claude SEO Local Workbench

一个面向 SEO、内容和本地文件任务的轻量 AI 工作台。

用户在浏览器里直接下达任务，后台调用用户自己电脑上已经登录的 Codex 和 Claude Code。文件留在本机，默认只读；需要修改时先展示 Diff，由用户确认后才写入，并支持备份与撤销。

这个仓库的重点不是重新包装一组提示词，而是把原本只能在命令行里使用的 SEO 能力，变成普通用户可以启动、登录、对话和安全操作文件的本地产品。

> 当前定位：可运行、接近小范围封测的本地工作台。它还不是高并发 SaaS，也不应在未完成跨电脑验收和商业认证确认前作为成熟商业软件宣传。

## 我做了什么

本 fork 新增并持续维护的是完整的本地工作台层，主要包括：

- **浏览器对话界面**：用户不需要记忆命令，可以直接描述 SEO、内容或文件任务。
- **双模型强制路由**：SEO 与文件任务交给 Codex；完整文章创作交给 Claude Code，避免模型混用。
- **稳定 Runtime 适配层**：前端不直接解析 CLI 的易变输出，Codex 和 Claude 事件被转换为统一协议。
- **本机订阅登录**：复用用户自己电脑上的官方 CLI 登录状态，不保存或复制账号凭据。
- **默认只读**：未经用户开启写入权限，AI 只能分析文件，不能修改项目。
- **安全写入闭环**：在隔离副本中生成修改，先显示 Diff，再确认应用；支持放弃、备份、撤销和重启恢复。
- **可选并发**：用户可以选择同时运行多个任务，服务端仍保留容量限制。
- **任务取消与超时**：取消或超时时清理整棵子进程树，避免后台命令残留。
- **Markdown 展示**：标题、列表、表格和代码块按 Markdown 渲染，不再显示为一整段纯文本。
- **跨平台启动器**：提供 macOS、Linux 和 Windows 启动方式，并校验 Python 3.10+。
- **本地后台服务**：关闭启动终端后服务仍可运行，也支持状态检查和安全停止。
- **专项测试**：工作台相关自动测试目前为 86 项，覆盖路由、会话、并发、取消、超时、安全写入和启动交付。

这些改动主要位于：

```text
ui/                         浏览器界面和本地 HTTP 服务
ui/workbench/               协议、会话、任务、认证和安全写入
ui/workbench/runtime/       Codex / Claude Runtime 适配器
run_workbench.py            后台服务启动与管理
start-workbench.*           macOS / Linux / Windows 启动器
tests/test_workbench_*.py   工作台专项测试
```

## 和基础项目有什么不同

| 能力 | 基础 SEO 技能工程 | 本 fork |
|---|---|---|
| 主要入口 | Claude Code 命令 | 浏览器对话工作台 |
| Codex 支持 | 不是主要产品入口 | SEO/文件任务的默认执行端 |
| Claude 支持 | 运行 SEO 技能 | 专门负责完整文章创作 |
| 模型路由 | 由使用者自行决定 | 后台按任务类型强制路由 |
| 文件修改 | 依赖 CLI 权限 | 默认只读，Diff 确认后写入 |
| 撤销与恢复 | 不属于核心交互 | 备份、撤销、冲突检查、重启恢复 |
| 普通用户启动 | 需要理解命令行与技能 | 三个平台启动器 + 浏览器 UI |
| 多任务 | 依赖运行环境 | 页面可选择并发数，服务端限制容量 |

## 快速开始

### 环境要求

- Python 3.10 或更高版本
- Codex CLI
- Claude Code CLI
- macOS、Linux 或 Windows

先使用各自的官方方式安装并登录 CLI：

```bash
codex login
claude auth login
```

项目不会读取、复制或保存登录密码、令牌和验证码。

### 获取当前工作台版本

```bash
git clone https://github.com/anqicao29-star/claude-seo.git
cd claude-seo
git checkout workbench/main
```

### 启动

- macOS：双击 `start-workbench.command`
- Linux：运行 `./start-workbench.sh`
- Windows：双击 `start-workbench.bat`

启动后访问：

```text
http://localhost:7777
```

不要直接双击 `ui/index.html`。脱离本地服务打开时，页面无法连接 Runtime。

检查环境、服务状态或停止后台服务：

```bash
python3 run_workbench.py --check
python3 run_workbench.py --status
python3 run_workbench.py --stop
```

更完整的启动说明见 [README-WORKBENCH.md](README-WORKBENCH.md)。

## 模型分工

### Codex：SEO 与本地文件任务

适合网站 SEO 检查、本地文章批量分析、关键词与内容集群规划、项目文件读取和安全修改，以及脚本执行与结构化结果整理。

### Claude：完整文章创作

当任务类型选择“文章创作”时，后台固定调用 Claude Code。Codex 不会代写文章，也不会把 Codex 生成的文本冒充为 Claude 输出。

切换模型任务类型时，工作台会使用独立会话，避免上下文串线。

## 文件安全设计

工作台当前采用以下写入流程：

```text
用户选择允许修改
        ↓
在隔离副本中运行 AI
        ↓
生成文件 Diff
        ↓
用户确认或放弃
        ↓
备份原文件后应用修改
        ↓
需要时一键撤销
```

安全边界：

- 默认 `read-only`。
- 写入功能必须由部署者明确开启。
- AI 先操作隔离副本，不直接覆盖原目录。
- 敏感路径、符号链接和越权路径会被阻止。
- 如果原文件在预览后被其他程序修改，应用操作会拒绝覆盖。
- 服务重启后仍可以恢复尚未确认的预览。
- 取消和超时会终止 Runtime 及其后代进程。

启用写入预览：

```bash
export CLAUDE_SEO_MAX_SANDBOX=workspace-write
./start-workbench.sh
```

Windows PowerShell：

```powershell
$env:CLAUDE_SEO_MAX_SANDBOX = "workspace-write"
.\start-workbench.bat
```

## 当前可使用的 SEO 能力

仓库保留了完整的通用 SEO 技能引擎，可用于全站和单页审计、技术 SEO、内容质量、Schema.org、GEO、站点地图、图片、国际化、本地 SEO、电商 SEO、外链以及 Google 数据扩展。

工作台会根据自然语言目标选择相关技能。高级用户仍然可以直接使用 `/seo audit`、`/seo page`、`/seo geo` 等原有命令。完整参考见 [docs/COMMANDS.md](docs/COMMANDS.md)。

## 下一步原创方向

下面是这个 fork 准备继续发展的方向。它们是路线图，不冒充为已经完成的功能。

### 1. AI 来源流量落地页分析

把 GA4、GSC 和可用的来源数据合在一起，识别 AI 来源访问主要落到哪些页面、页面类型是什么、与自然搜索的结构有何不同，以及哪些页面有曝光却没有后续转化。

### 2. 可见度读数与噪声检查

在展示可见度结果前，先检查样本量、品牌词与非品牌词、地区差异、一次性波动，以及不同数据源之间的统计口径是否一致。

### 3. 内容类型与流量对照

把内容按文章、产品页、工具页、品牌页等类型分组，对照曝光、点击、参与和转化，避免用全站平均值掩盖真正有效或无效的内容。

### 4. 下载事件口径检查

检查 GA4、GTM 和站内代码对下载事件的命名、参数、去重与触发条件是否一致，减少“报表有数据但口径错误”的情况。

优先从其中一到两个方向做成独立子技能，并使用公开网站或自有站点提供可复现案例。客户数据不会作为公开演示材料。

## 测试

运行工作台专项测试：

```bash
python3 -m unittest \
  tests.test_codex_runtime \
  tests.test_claude_runtime \
  tests.test_runtime_processes \
  tests.test_workbench_auth \
  tests.test_workbench_core \
  tests.test_workbench_delivery_guards \
  tests.test_workbench_launcher \
  tests.test_workbench_markdown \
  tests.test_workbench_server \
  tests.test_workbench_sessions \
  tests.test_workbench_tasks \
  tests.test_workbench_write_previews \
  tests.test_workbench_write_ui
```

运行 Skill 可移植性检查：

```bash
python3 scripts/portability_check.py
```

## 当前限制

- 尚未完成另一台非开发电脑的完整分发验收。
- 外部工作目录选择仍在待办中，目前主要围绕项目目录工作。
- 用户订阅登录能否作为第三方商业产品的正式认证方案，仍需遵守 OpenAI 和 Anthropic 的官方规则；本项目不会自行承诺商业合规。
- 目前不是面向大量用户的高并发服务。
- CMS、多模型、国内外发布闭环和数据监测属于后续能力。

产品路线和待办见 [docs/product-backlog-domestic-overseas.md](docs/product-backlog-domestic-overseas.md)。

## 项目来源与署名

本项目是在开源项目 [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) 基础上开发的 fork。

基础项目提供了 SEO skills、agents、scripts、schema 模板以及相关文档。本 fork 的主要新增工作是上面说明的本地工作台、双 Runtime 路由、安全文件写入、跨平台启动和测试交付层。

原项目采用 MIT License。本仓库继续保留原版权声明和许可文本，详见 [LICENSE](LICENSE)；社区贡献记录见 [CONTRIBUTORS.md](CONTRIBUTORS.md)。这段归属说明用于准确区分继承内容与本 fork 的新增内容。

## 维护者

本 fork 的本地工作台方向由 [anqicao29-star](https://github.com/anqicao29-star) 开发和维护。

欢迎围绕本地 AI 工作流、SEO 数据质量、AI 来源流量分析和安全文件操作提交问题与改进建议。
