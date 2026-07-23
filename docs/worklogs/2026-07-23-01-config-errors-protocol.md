# 工作日志：配置、错误码与协议核心

- 日期：2026-07-23
- 阶段：01 工程化底座
- 开始提交：`0cdc557`
- 实现提交：`c59443e`
- 状态：已完成

## 本次目标

继续拆分单文件工作台后端，优先建立集中配置、稳定错误响应和版本化事件协议，同时保持现有启动方式与聊天行为兼容。

## 完成内容

1. 新建 `ui/workbench/` 核心包。
2. 将目录、Codex 路径、模型、权限上限和请求限制集中到 `config.py`。
3. 无效的写权限配置会自动降级为 `read-only`。
4. 建立稳定错误码与统一错误结构：
   - `code`
   - `message`
   - `retryable`
   - `request_id`
   - `details`
5. 每个 HTTP 请求生成独立 `request_id`，同时通过 `X-Request-ID` 返回。
6. 前端兼容新的结构化错误响应。
7. 建立 `claude-seo.workbench` v1 事件模型：
   - 固定协议名和版本。
   - `task_id`、`event_id`、序号和 UTC 时间戳。
   - 限定公开事件类型。
   - 强制序号递增。
   - 每个任务只能出现一个终态，终态后禁止继续发送事件。
8. 新增核心模块测试，并更新 HTTP 特征测试。

## 主要文件

- `ui/workbench/config.py`
- `ui/workbench/errors.py`
- `ui/workbench/protocol.py`
- `ui/server.py`
- `ui/index.html`
- `tests/test_workbench_core.py`
- `tests/test_workbench_server.py`

## 验证结果

- `python3 -m unittest tests.test_workbench_core tests.test_workbench_server -v`
  - 19 个测试通过。
- Python 语法编译检查通过。
- 前端内联 JavaScript 语法检查通过。
- `git diff --check` 通过。

测试使用 Fake Codex 进程，不调用真实 Codex、不访问外部网站、不修改用户文章。

## 当前限制

- v1 事件模型已经建立，但 `/api/chat` 仍在输出旧 NDJSON 事件；迁移需要兼容层，不能一次切换。
- 会话仍由浏览器 `localStorage` 和 Codex Runtime 内部线程共同维持。
- 系统默认 Python 为 3.9.6，而项目元数据要求 Python 3.10 以上。
- 当前环境没有全局 `pytest`，本次使用标准库 `unittest` 完成验证。

## 下一步

1. 提取 Codex CLI Runtime 适配器。
2. 使用 Fake Runtime 将 HTTP 测试与真实 CLI 命令解耦。
3. 建立任务状态机和应用会话 ID。
4. 增加 v1 流式接口，并保留旧 `/api/chat` 兼容层。
5. 更新架构、测试和状态文档。

