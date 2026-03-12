/*
    3ds Max MCP Server 启动脚本
    
    使用方法：
    1. 在 3ds Max 中：Scripting > Run Script > 选择此文件
    2. 或拖拽此文件到 3ds Max 视口中
    3. 或在 MAXScript Listener 中执行:
       fileIn @"E:\DCC_MCP\3dsmax_mcp\startup_mcp_listener.ms"
    
    功能：
    启动 MCP Socket Server，使 3ds Max 可以接收来自 MCP Client 的命令。
*/

-- 获取当前脚本所在目录
local scriptDir = getFilenamePath (getSourceFileName())
local listenerScript = scriptDir + @"core\connector\max_server_listener.py"

-- 检查文件是否存在
if doesFileExist listenerScript then (
    format "[3dsMaxMCP] 正在启动 MCP Socket Server...\n"
    format "[3dsMaxMCP] 脚本路径: %\n" listenerScript
    python.ExecuteFile listenerScript
    format "[3dsMaxMCP] MCP Socket Server 启动命令已发送\n"
) else (
    format "[3dsMaxMCP] 错误: 找不到监听脚本: %\n" listenerScript
    messageBox ("找不到 MCP 监听脚本:\n" + listenerScript) title:"3dsMaxMCP Error"
)
