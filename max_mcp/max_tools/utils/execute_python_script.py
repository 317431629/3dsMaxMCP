#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中执行 Python 脚本
# Version   : 1.0
# Comment   : 通用的 Python 脚本执行工具，允许 MCP 客户端发送任意 Python 代码到 3ds Max 执行


def execute_python_script(script: str) -> dict:
    """在 3ds Max 中执行一段 Python 脚本并返回执行结果。

    该工具允许你发送任意 Python 代码到 3ds Max 中执行。
    脚本在 3ds Max 的 Python 环境中运行，可以访问 pymxs、MaxPlus 等模块。

    使用说明：
    - 脚本中可以通过 `import pymxs; rt = pymxs.runtime` 来访问 MAXScript 运行时。
    - 脚本中可以使用 `print()` 输出调试信息（会打印到 3ds Max 控制台）。
    - 如果需要返回结果，请将结果赋值给 `_mcp_max_results` 变量（字典或可 JSON 序列化的对象）。
    - 如果脚本没有设置 `_mcp_max_results`，则返回 `{"success": True, "message": "脚本已执行完成"}`。

    示例脚本 - 获取场景中所有对象的名称：
        import pymxs
        rt = pymxs.runtime
        names = [str(obj.name) for obj in rt.objects]
        _mcp_max_results = {"success": True, "object_names": names, "count": len(names)}

    示例脚本 - 创建一个球体：
        import pymxs
        rt = pymxs.runtime
        sphere = rt.Sphere(radius=30, pos=rt.Point3(0, 0, 0))
        sphere.name = "MCP_Sphere"
        _mcp_max_results = {"success": True, "name": str(sphere.name), "radius": 30}

    Args:
        script: 要在 3ds Max 中执行的 Python 脚本代码字符串。

    Returns:
        dict: 包含执行结果的字典。
            - success (bool): 脚本是否执行成功。
            - 其他字段取决于脚本中 `_mcp_max_results` 的内容。
    """
    import json
    import traceback

    try:
        # 创建一个独立的命名空间来执行脚本，避免污染全局作用域
        exec_namespace = {}
        exec(script, exec_namespace)

        # 尝试从执行命名空间中获取返回结果
        if '_mcp_max_results' in exec_namespace:
            result = exec_namespace['_mcp_max_results']
            if isinstance(result, dict):
                return result
            elif isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"success": True, "result": result}
            else:
                return {"success": True, "result": str(result)}
        else:
            return {"success": True, "message": "脚本已执行完成"}

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"脚本执行出错: {str(e)}",
            "traceback": traceback.format_exc()
        }
