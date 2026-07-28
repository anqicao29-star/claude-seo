# 工作日志：可分发的 Codex + Claude 本地工作台

- 日期：2026-07-28
- 阶段：轻量可交付版本
- 开始提交：`afe4d28`
- 实现提交：`a092a4f`
- 修复提交：`9a4f3b4`
- 状态：功能已完成，可开始内部验收

## 大白话总结

这次没有继续做大型系统需要的复杂基础设施，而是直接围绕“发给别人后能在本地使用”完成一版轻量交付：

1. 用户自己的电脑安装并登录 Codex 和 Claude Code。
2. 双击启动器，工作台自动启动并打开浏览器。
3. SEO、网站分析和文件任务交给 Codex。
4. 选择“文章创作”后，后台强制交给 Claude，不会误用 Codex。
5. 项目不会读取、复制或打包用户的登录凭据。

现在已经有一个可以直接发送的 ZIP，不再要求别人先理解项目结构或手动双击 HTML。

## 本次完成内容

### 1. Codex 与 Claude 分工

- 新增 Claude Code CLI 适配器。
- 通用任务路由到本机 Codex。
- 文章创作任务路由到本机 Claude Code。
- 后台只接受 `general` 和 `article` 两种任务类型。
- 模型路由由后台决定，不能仅靠前端文字伪装。
- Claude 使用 `sonnet` 稳定别名，可通过环境变量调整。
- 同一个应用会话切换模型时会自动建立新会话，避免 Codex 和 Claude 的内部会话 ID 混用。

### 2. 登录和运行状态

- 同时检测 Codex CLI 与 Claude Code 是否安装。
- 同时检测两个 CLI 是否已登录。
- 页面顶部显示：
  - Codex 已登录或未登录。
  - Claude 已登录或未登录。
- 未登录时给出准确命令：
  - `codex login`
  - `claude auth login`
- 不读取或返回具体凭据内容。

### 3. 网页功能

- 增加任务类型选择：
  - `SEO/文件任务 · Codex`
  - `文章创作 · Claude`
- 增加“创作完整文章”快捷入口。
- 文章模式明确显示由 Claude 执行。
- Claude 未登录时不会把文章任务降级交给 Codex，而是直接提示登录。
- 直接双击 `ui/index.html` 时会提示打开方式不正确。
- 并发能力保留，但新用户默认并发改回 1，符合当前轻量产品目标。

### 4. 可分发启动器

- macOS：`start-workbench.command`
- Linux：`start-workbench.sh`
- Windows：`start-workbench.bat`
- 通用启动器：`run_workbench.py`
- 启动后自动打开 `http://localhost:7777`。
- 已运行时再次启动会直接打开已有工作台。
- 支持环境检查：

```bash
python3 run_workbench.py --check
```

### 5. 开箱即用

- 技能和 Agent 默认从压缩包自身读取，不再依赖接收者提前把技能安装到 `~/.claude`。
- 分发包内置 25 个核心 SEO 技能。
- 新增独立使用说明 `README-WORKBENCH.md`。
- 中英文主 README 都增加了本地工作台入口。

## 分发包

- 文件：`dist/claude-seo-workbench-local.zip`
- 大小：约 2.3 MB
- SHA-256：`9a9fb76dfcd6963be646a49b4716f8cb6e59d467412fe65b5b22f4c7e9ec0e11`

压缩包只从 Git 已跟踪文件构建，并主动排除测试、内部工作日志和项目协作文档。解压检查没有发现：

- `.env`
- Codex `auth.json`
- Claude 登录文件
- PEM/P12/PFX 密钥
- 本机 SQLite 数据库

## 验证结果

- 54 个工作台测试全部通过。
- Claude 事件、会话恢复、登录状态和任务路由测试通过。
- 验证文章任务响应头明确为 `claude`。
- 验证文章提示词由 Claude 适配器接收，而不是 Codex。
- 验证切换模型会产生新的应用会话。
- 真实 Codex 端到端任务返回 `READY`。
- 浏览器实测：
  - 正确显示 Codex 已登录、Claude 未登录。
  - 可切换到“文章创作 · Claude”。
  - Claude 未登录时准确显示 `claude auth login`。
  - 未产生错误的 Codex 回退请求。
- 从最终 ZIP 解压后的副本运行 `--check` 成功：
  - Codex 安装和登录识别正确。
  - Claude 安装但未登录识别正确。
  - 25 个核心技能可读取。
- Python 语法检查通过。
- 前端 JavaScript 语法检查通过。
- 33 个 Skill 的跨平台兼容检查无错误、无警告。

## 当前唯一未完成的真人账号验证

当前电脑上的 Claude Code 已安装，但 `claude auth status` 显示尚未登录。因此本次不能用真实 Claude 账号生成一篇文章。

用户登录后运行：

```bash
claude auth login
```

刷新工作台，即可进行最后一条真实文章验收。代码层、模拟 CLI 流、路由和界面已经全部完成。

## 支持范围

当前轻量版要求接收者电脑具备：

- Python 3.10+
- Codex CLI
- Claude Code
- 两个 CLI 各自完成本地登录

macOS 已完成实际启动和浏览器验证。Linux、Windows 已提供对应启动器和路径兼容逻辑，但还需要分别在一台真实机器上做冒烟测试，不能把“脚本存在”描述成“所有系统已经实机验证”。

## 距离封闭测试还有多久

按照本次收窄后的目标，不再等待原先完整桌面软件、签名公证和大型任务中心：

- 当前即可开始本机内部验收。
- Claude 登录后，约 10–20 分钟可完成真实文章验收。
- 找 2–3 台不同电脑完成安装、登录、启动和一条任务测试后，预计 3–7 天可以开始小范围封测。

如果仍要求“不安装 Python”“双击原生 App”“macOS 签名公证”和任意目录的图形化授权，则仍需要额外开发；这些不属于本次轻量交付范围。

## 下一步

1. 用户运行 `claude auth login`。
2. 在网页选择“文章创作 · Claude”，生成一篇短文章进行真人账号验收。
3. 把 ZIP 发给 2–3 名测试者，分别记录 macOS、Windows、Linux 的启动结果。
4. 只修复真实测试遇到的问题，不继续提前建设大型基础设施。
