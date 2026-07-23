# 工作日志：Codex Runtime 适配器

- 日期：2026-07-23
- 阶段：01 工程化底座
- 开始提交：`3657324`
- 实现提交：`c1744b2`
- 状态：已完成

## 大白话总结

以前网页后端既要接收用户消息，又要自己拼 Codex 命令、启动进程、看懂 Codex 返回的每一种消息，还要负责停止进程。所有事情挤在一个文件里，Codex CLI 一升级，网页就可能一起坏。

这次相当于在网页后端和 Codex 之间增加了一个“翻译员兼司机”：

- 网页后端只需要说：“请执行这个任务，使用只读模式。”
- Runtime 适配器负责把它翻译成正确的 Codex CLI 命令。
- Codex 返回的专用事件先由适配器翻译成产品内部事件，再交给网页。
- Codex 进程或它启动的子进程需要停止时，也由适配器统一处理。

用户暂时看不到新按钮，但底层已经更稳定。以后升级 Codex CLI，或者增加其他模型时，不需要重新改整套网页服务。

## 本次完成内容

1. 建立与具体模型无关的 Runtime 接口：
   - `RuntimeAdapter`
   - `RuntimeRequest`
   - `RuntimeStatus`
   - `RuntimeEvent`
   - `RuntimeSession`
2. 建立 Codex CLI 专用适配器。
3. 将以下 Codex 专属逻辑移出 `ui/server.py`：
   - 新任务和续接任务的命令拼装。
   - Codex 版本及登录状态检查。
   - 子进程启动和标准输入写入。
   - JSON 事件解析。
   - stderr 收集。
   - 进程结束和进程组终止。
4. HTTP 服务现在只依赖 Runtime 接口，不再直接调用 `subprocess.Popen`。
5. HTTP 测试改用 Fake Runtime，不需要电脑真实安装或登录 Codex。
6. Codex 适配器拥有独立测试，锁定当前命令参数和事件转换行为。

## 主要文件

- `ui/workbench/runtime/base.py`
- `ui/workbench/runtime/codex_cli.py`
- `ui/workbench/runtime/__init__.py`
- `ui/server.py`
- `tests/test_codex_runtime.py`
- `tests/test_workbench_server.py`

## 验证结果

- 22 个工作台测试通过。
- Python 语法编译检查通过。
- 前端 JavaScript 语法检查通过。
- `git diff --check` 通过。
- 测试未调用真实 Codex、未访问外部网站、未修改用户文章。

## 距离封闭测试还有多久

按以下范围估算：

- 只做 macOS。
- 第一批 10–30 位测试用户。
- 首版不做 CMS、不做多模型。
- 需求范围不继续扩大。
- 保持当前节奏持续推进。

预计时间：

- 可供内部自己试用的 Alpha：约 3–4 周。
- 可发给 10–30 位客户的封闭测试版：约 7–10 周。

当前仍需要完成：

1. 01 工程化底座剩余部分：任务状态、会话、取消、v1 接口、日志和 CI。
2. 02 本地文件工作区：选目录、只读、Diff、备份、撤销和路径安全。
3. 03 Codex 登录和版本兼容。
4. 04 macOS 安装包、签名和公证。
5. 05 崩溃恢复、升级回退及真实用户测试。

最大不确定因素：

- ChatGPT/Codex 订阅登录用于第三方桌面软件的官方允许范围。
- Codex Runtime 是否随应用分发，还是要求用户单独安装。
- Apple 签名、公证和自动更新链路。

如果订阅登录方案无法直接产品化，需要切换为“用户自行安装并登录官方 Codex”或“用户提供 API Key”，封测时间可能增加约 1–3 周。

## 下一步

1. 建立任务状态机和应用自己的任务 ID。
2. 增加真正的任务取消接口。
3. 将 v1 事件协议接入流式接口。
4. 让前端逐步摆脱 Codex `thread_id`。

