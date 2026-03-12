# max-mcp

3ds Max MCP Server — 通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 远程控制 Autodesk 3ds Max。

## ✨ 功能

通过 MCP 客户端（如 Claude Desktop、Cursor 等）与 3ds Max 进行交互，支持以下操作：

| 类别 | 工具 |
|------|------|
| 🎬 场景 | 新建/打开/保存场景、导入/导出文件、获取场景信息和对象列表 |
| 📦 对象 | 创建/删除/克隆/重命名对象、设置变换/属性、添加修改器、选择对象 |
| 🎨 材质 | 创建材质、分配材质到对象 |
| 💡 灯光 | 创建各类灯光 |
| 🎞️ 动画 | 设置关键帧、设置时间范围 |
| 🔧 通用 | 执行 MAXScript / Python 脚本、获取 Max 版本信息 |

## 📦 安装

### 通过 uvx（推荐）

```bash
uvx max-mcp
```

### 通过 pip

```bash
pip install max-mcp
```

### 从源码安装

```bash
git clone https://github.com/317431629/3dsMaxMCP.git
cd 3dsMaxMCP
pip install -e .
```

## 🚀 使用

### 1. 在 3ds Max 中启动监听器

将 `startup_mcp_listener.ms` 复制到 3ds Max 的启动脚本目录（通常为 `C:\Users\<用户名>\AppData\Local\Autodesk\3dsMax\<版本>\ENU\scripts\startup\`），然后重启 3ds Max。

或者在 3ds Max 的 MAXScript 监听器中手动执行：

```maxscript
fileIn @"<项目路径>\startup_mcp_listener.ms"
```

### 2. 配置 MCP 客户端

在 MCP 客户端的配置文件中添加：

```json
{
    "mcpServers": {
        "max-mcp": {
            "command": "uvx",
            "args": ["max-mcp"]
        }
    }
}
```

如果是从源码安装：

```json
{
    "mcpServers": {
        "max-mcp": {
            "command": "python",
            "args": ["-m", "max_mcp"],
            "cwd": "<项目根目录路径>"
        }
    }
}
```

### 3. 开始使用

在 MCP 客户端中即可通过自然语言指令控制 3ds Max，例如：

- "在场景中创建一个球体"
- "将选中的对象移动到 (10, 0, 0)"
- "给选中的对象创建一个红色材质"
- "保存当前场景"

## 📋 系统要求

- Python >= 3.10
- Autodesk 3ds Max（需支持 Python 3 脚本执行）
- 3ds Max 与 MCP Server 在同一台机器上运行

## 📄 License

MIT License
