<p align="center">
  <h1 align="center">🎮 3dsmax-mcp</h1>
  <p align="center">通过 <a href="https://modelcontextprotocol.io/">Model Context Protocol (MCP)</a> 让 AI 控制 Autodesk 3ds Max</p>
  <p align="center">
    <a href="https://github.com/317431629/3dsMaxMCP">GitHub</a> · 
    <a href="https://pypi.org/project/3dsmax-mcp/">PyPI</a> · 
    <a href="#-快速开始">快速开始</a> · 
    <a href="#-工具参考">工具参考</a>
  </p>
</p>

---

## 📖 简介

**3dsmax-mcp** 是一个 MCP（Model Context Protocol）服务器，它在 AI 助手（如 Claude Desktop、Cursor、Windsurf 等）和 Autodesk 3ds Max 之间架起桥梁。

通过自然语言对话，你可以让 AI 直接操控 3ds Max —— 创建模型、设置材质、调整灯光、制作动画，甚至执行自定义脚本，无需手动编写任何代码。

### 工作原理

```
┌──────────────┐     MCP协议     ┌──────────────┐    TCP Socket    ┌──────────────┐
│  MCP 客户端   │ ◄────────────► │  3dsmax-mcp  │ ◄──────────────► │   3ds Max    │
│ (Claude 等)  │    stdio 通道   │  (MCP Server) │   127.0.0.1     │  (监听脚本)   │
└──────────────┘                └──────────────┘    :50007         └──────────────┘
```

1. **MCP 客户端**（如 Claude Desktop）通过 MCP 协议与 `3dsmax-mcp` 服务器通信
2. **3dsmax-mcp** 将 AI 的指令转换为 Python 脚本
3. 通过 **TCP Socket**（端口 50007）发送到 3ds Max 中的监听脚本执行
4. 执行结果原路返回给 AI 助手

---

## 📋 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows（3ds Max 仅支持 Windows） |
| **Python** | >= 3.10 |
| **3ds Max** | 需支持 Python 3 脚本（推荐 2022 及以上版本） |
| **网络** | 3ds Max 与 MCP Server 需在同一台机器上运行 |
| **MCP 客户端** | Claude Desktop / Cursor / Windsurf / 或其他支持 MCP 的客户端 |

---

## 🚀 快速开始

整个安装只需 **两步**：配置 3ds Max 端的监听脚本，然后配置 MCP 客户端。

### 第一步：在 3ds Max 中启动监听

你需要让 3ds Max 运行一个 Socket 监听脚本，这样 MCP Server 才能与之通信。

#### 方式 A：自动启动（推荐）

将项目中的 `startup_mcp_listener.ms` 文件复制到 3ds Max 的启动脚本目录：

```
C:\Users\<你的用户名>\AppData\Local\Autodesk\3dsMax\<版本号>\ENU\scripts\startup\
```

> 💡 **提示**：放入该目录后，每次启动 3ds Max 会自动运行监听脚本，无需手动操作。

#### 方式 B：手动启动

在 3ds Max 中执行以下任一操作：

- **菜单方式**：`Scripting` → `Run Script` → 选择 `startup_mcp_listener.ms` 文件
- **拖拽方式**：将 `startup_mcp_listener.ms` 直接拖拽到 3ds Max 视口中
- **监听器方式**：在 MAXScript Listener 中输入：

```maxscript
fileIn @"C:\你的路径\3dsMaxMCP\startup_mcp_listener.ms"
```

> ✅ 启动成功后，MAXScript Listener 中会显示：`[3dsMaxMCP] MCP Socket Server 启动命令已发送`

### 第二步：安装并配置 MCP 客户端

#### 安装 3dsmax-mcp

提供以下三种安装方式：

**通过 pip 安装（推荐）：**

```bash
pip install 3dsmax-mcp
```

**通过 uvx 运行（免安装）：**

```bash
uvx 3dsmax-mcp
```

**从源码安装（开发者）：**

```bash
git clone https://github.com/317431629/3dsMaxMCP.git
cd 3dsMaxMCP
pip install -e .
```

#### 配置 MCP 客户端

<details>
<summary><b>🤖 Claude Desktop</b></summary>

编辑配置文件（通常位于 `%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
    "mcpServers": {
        "3dsmax-mcp": {
            "command": "uvx",
            "args": ["3dsmax-mcp"]
        }
    }
}
```

如果使用 pip 安装：

```json
{
    "mcpServers": {
        "3dsmax-mcp": {
            "command": "3dsmax-mcp"
        }
    }
}
```

</details>

<details>
<summary><b>✏️ Cursor</b></summary>

在 Cursor 的 Settings → MCP 中添加：

```json
{
    "mcpServers": {
        "3dsmax-mcp": {
            "command": "uvx",
            "args": ["3dsmax-mcp"]
        }
    }
}
```

或使用 pip 安装后：

```json
{
    "mcpServers": {
        "3dsmax-mcp": {
            "command": "3dsmax-mcp"
        }
    }
}
```

</details>

<details>
<summary><b>🛠️ 从源码运行</b></summary>

如果你是从源码克隆的项目：

```json
{
    "mcpServers": {
        "3dsmax-mcp": {
            "command": "python",
            "args": ["-m", "max_mcp"],
            "cwd": "C:/你的路径/3dsMaxMCP"
        }
    }
}
```

</details>

### 第三步：开始使用 🎉

确保 3ds Max 已启动且监听脚本正在运行，然后在 MCP 客户端中用自然语言对话即可：

- *"在场景中创建一个球体，半径为 30"*
- *"把 Box001 移动到坐标 (100, 0, 50)"*
- *"给选中的对象创建一个红色金属材质"*
- *"在第 0 帧和第 60 帧之间为球体做一个位移动画"*
- *"保存当前场景到桌面"*

---

## 🔧 工具参考

3dsmax-mcp 提供了 **25 个工具**，覆盖 3ds Max 的常用操作。以下是完整的工具列表和说明。

### 🎬 场景管理（Scene）

| 工具名 | 功能 | 关键参数 |
|--------|------|----------|
| `new_scene` | 新建空白场景 | — |
| `open_scene` | 打开场景文件 | `file_path`: 文件路径 |
| `save_scene` | 保存当前场景 | `file_path`: 保存路径（可选，留空则覆盖保存） |
| `get_scene_info` | 获取场景信息（对象数、文件路径等） | — |
| `get_scene_objects` | 获取场景中所有对象的列表 | — |
| `import_file` | 导入外部文件到场景 | `file_path`: 文件路径 |
| `export_file` | 导出场景到文件 | `file_path`: 导出路径 |

### 📦 对象操作（Object）

| 工具名 | 功能 | 关键参数 |
|--------|------|----------|
| `create_object` | 创建几何体 | `object_type`: 类型（Box/Sphere/Cylinder 等）, `position`: 位置, `params`: 参数 JSON |
| `delete_object` | 删除对象 | `object_name`: 对象名称 |
| `clone_object` | 克隆对象 | `object_name`: 源对象名称 |
| `rename_object` | 重命名对象 | `object_name`: 当前名称, `new_name`: 新名称 |
| `set_object_transform` | 设置对象变换（位置/旋转/缩放） | `object_name`, `position`, `rotation`, `scale` |
| `set_object_property` | 设置对象属性 | `object_name`, `property_name`, `property_value` |
| `get_object_properties` | 获取对象的详细属性 | `object_name`: 对象名称 |
| `select_objects` | 选择对象 | `object_names`: 对象名称列表 |
| `add_modifier` | 添加修改器 | `object_name`: 对象名称, `modifier_type`: 修改器类型 |

### 🎨 材质（Material）

| 工具名 | 功能 | 关键参数 |
|--------|------|----------|
| `create_material` | 创建材质 | `material_type`: 类型（Standard/Physical 等）, `diffuse_color`: 颜色, `params`: 参数 JSON |
| `assign_material` | 将材质分配给对象 | `object_name`: 目标对象, `material_name`: 材质名称 |

### 💡 灯光（Light）

| 工具名 | 功能 | 关键参数 |
|--------|------|----------|
| `create_light` | 创建灯光 | `light_type`: 类型（Omni/FreeSpot/Skylight 等）, `position`, `color`, `intensity` |

### 🎞️ 动画（Animation）

| 工具名 | 功能 | 关键参数 |
|--------|------|----------|
| `set_keyframe` | 设置关键帧 | `object_name`, `frame`, `position`, `rotation`, `scale` |
| `set_time_range` | 设置动画时间范围 | 起始帧、结束帧 |

### 🔧 通用工具（Utils）

| 工具名 | 功能 | 关键参数 |
|--------|------|----------|
| `execute_maxscript` | 执行 MAXScript 代码 | `script`: MAXScript 代码字符串 |
| `execute_python_script` | 执行 Python 脚本 | `script`: Python 代码字符串 |
| `get_max_version` | 获取 3ds Max 版本信息 | — |

---

## 💡 使用示例

### 场景搭建

```
用户：帮我创建一个简单的桌子场景。桌面是一个扁平的 Box，四条腿也是 Box。

AI 会依次调用：
  → create_object(object_type="Box", name="TableTop", position="0,0,75", params='{"length":120,"width":80,"height":5}')
  → create_object(object_type="Box", name="Leg_FL", position="-50,-30,0", params='{"length":5,"width":5,"height":75}')
  → create_object(object_type="Box", name="Leg_FR", position="50,-30,0", params='{"length":5,"width":5,"height":75}')
  → create_object(object_type="Box", name="Leg_BL", position="-50,30,0", params='{"length":5,"width":5,"height":75}')
  → create_object(object_type="Box", name="Leg_BR", position="50,30,0", params='{"length":5,"width":5,"height":75}')
```

### 材质与灯光

```
用户：给桌面创建一个木质感的棕色材质，然后在桌子上方添加一盏暖黄色的灯。

AI 会依次调用：
  → create_material(material_type="Standard", name="WoodMat", diffuse_color="139,90,43")
  → assign_material(object_name="TableTop", material_name="WoodMat")
  → create_light(light_type="Omni", name="TableLight", position="0,0,200", color="255,235,200", intensity="1.2")
```

### 关键帧动画

```
用户：让球体从位置 (0,0,0) 在 60 帧内移动到 (100,0,50)，同时旋转 360 度。

AI 会依次调用：
  → set_keyframe(object_name="Sphere001", frame="0", position="0,0,0", rotation="0,0,0")
  → set_keyframe(object_name="Sphere001", frame="60", position="100,0,50", rotation="0,0,360")
  → set_time_range(...)  // 设置播放范围为 0-60
```

### 执行自定义脚本

```
用户：把所有 Box 对象的线框颜色设为红色。

AI 会调用：
  → execute_maxscript(script="for obj in objects where classOf obj == Box do obj.wireColor = color 255 0 0")
```

---

## ❗ 常见问题

### 连接问题

<details>
<summary><b>Q: 提示"无法连接到 3ds Max"怎么办？</b></summary>

请依次检查：

1. **3ds Max 是否正在运行？** —— 必须先启动 3ds Max
2. **监听脚本是否已执行？** —— 检查 MAXScript Listener 中是否有 `[3dsMaxMCP] MCP Socket Server 启动命令已发送` 的提示
3. **端口是否被占用？** —— 默认使用端口 `50007`，确保没有其他程序占用
4. **防火墙设置** —— 某些安全软件可能阻止本地 Socket 通信，请添加例外

</details>

<details>
<summary><b>Q: 执行超时怎么办？</b></summary>

默认 Socket 超时时间为 60 秒。如果你的操作需要更长时间（如复杂渲染或大场景处理），可能会超时。建议：

- 将复杂操作拆分为多个简单步骤
- 避免在 MCP 工具中执行渲染等耗时操作

</details>

### 安装问题

<details>
<summary><b>Q: uvx 命令找不到怎么办？</b></summary>

`uvx` 是 [uv](https://github.com/astral-sh/uv) 工具的一部分。安装方法：

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# 或通过 pip
pip install uv
```

</details>

<details>
<summary><b>Q: 支持哪些版本的 3ds Max？</b></summary>

理论上支持所有内置 Python 3 的 3ds Max 版本（2022 及以上）。推荐使用 **3ds Max 2024** 及以上版本，Python 环境更稳定。

</details>

### 使用问题

<details>
<summary><b>Q: 可以同时控制多个 3ds Max 实例吗？</b></summary>

当前版本默认连接 `127.0.0.1:50007`，仅支持单实例。如需多实例支持，需要修改监听端口配置。

</details>

<details>
<summary><b>Q: 支持 V-Ray / Arnold 等第三方渲染器吗？</b></summary>

支持！`create_material` 和 `create_light` 工具可以创建第三方插件提供的材质和灯光类型（如 `VRayMtl`、`VRayLight`），前提是 3ds Max 中已安装对应插件。对于更复杂的操作，可以使用 `execute_maxscript` 或 `execute_python_script` 工具直接执行自定义脚本。

</details>

---

## 🏗️ 项目结构

```
3dsMaxMCP/
├── max_mcp/                        # Python 包主目录
│   ├── __init__.py                 # 包入口
│   ├── __main__.py                 # python -m max_mcp 入口
│   ├── server.py                   # MCP Server 核心实现
│   ├── OperationManager.py         # 工具注册与管理
│   ├── log.py                      # 日志管理
│   ├── connector/                  # 通信层
│   │   ├── max_connection.py       # MCP Server → 3ds Max 的 TCP 客户端
│   │   └── max_server_listener.py  # 3ds Max 端的 TCP 监听服务（在 Max 内运行）
│   ├── max_tools/                  # 所有 MCP 工具脚本
│   │   ├── scene/                  # 场景相关工具（7个）
│   │   ├── object/                 # 对象操作工具（9个）
│   │   ├── material/               # 材质工具（2个）
│   │   ├── light/                  # 灯光工具（1个）
│   │   ├── animation/              # 动画工具（2个）
│   │   └── utils/                  # 通用工具（3个）
│   └── utils/                      # 内部工具函数
├── startup_mcp_listener.ms         # 3ds Max 启动脚本（MAXScript）
├── pyproject.toml                  # Python 包配置
├── LICENSE                         # MIT 许可证
└── README.md                       # 本文件
```

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可。