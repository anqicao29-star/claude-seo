# Claude SEO 本地工作台

这是可以直接发给其他人使用的轻量本地版。用户自己的账号留在自己的电脑上，本项目不读取、复制或保存登录凭据。

## 第一次使用

电脑需要安装：

1. Python 3.10 或更高版本
2. Codex CLI
3. Claude Code

安装后分别登录：

```bash
codex login
claude auth login
```

可以先检查环境：

```bash
python3 run_workbench.py --check
```

## 启动

- macOS：双击 `start-workbench.command`
- Linux：运行 `./start-workbench.sh`
- Windows：双击 `start-workbench.bat`

启动器会自动打开：

`http://localhost:7777`

不要直接双击 `ui/index.html`。HTML 文件只是界面，脱离本地服务会显示无法连接。

## 模型分工

- `SEO/文件任务`：使用本机已经登录的 Codex。
- `文章创作`：使用本机已经登录的 Claude Code。

文章任务的模型选择由后台强制执行，不会误走 Codex。切换任务类型时会开始新的会话，避免两个模型混用会话上下文。

## 权限

默认仅允许读取和分析，不修改文件。开发者或高级用户确认需要写入后，可以在启动前设置：

```bash
export CLAUDE_SEO_MAX_SANDBOX=workspace-write
./start-workbench.sh
```

Windows PowerShell：

```powershell
$env:CLAUDE_SEO_MAX_SANDBOX = "workspace-write"
.\start-workbench.bat
```

## 常见问题

### Codex 未登录

运行：

```bash
codex login
```

### Claude 未登录

运行：

```bash
claude auth login
```

### 页面显示 Failed to fetch

关闭直接打开的 HTML 页面，运行启动器，然后访问 `http://localhost:7777`。

### 端口 7777 被占用

```bash
python3 run_workbench.py --port 7788
```

然后访问 `http://localhost:7788`。
