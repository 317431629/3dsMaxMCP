#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中执行 MAXScript 代码
# Version   : 1.0
# Comment   : 通用的 MAXScript 执行工具，适用于某些用 MAXScript 更直接的操作


def execute_maxscript(script: str) -> dict:
    """在 3ds Max 中执行一段 MAXScript 代码并返回结果。

    该工具允许你发送 MAXScript 代码到 3ds Max 中执行。
    适用于某些用 MAXScript 更直接或更方便的操作场景。

    使用说明：
    - 脚本中最后一个表达式的值将作为返回结果。
    - 如果需要返回复杂结构，建议将结果构造为字符串或在脚本中使用 print。
    - MAXScript 文档参考: https://help.autodesk.com/view/3DSMAX/2025/ENU/?guid=GUID-MAXScript-Index

    Args:
        script: 要执行的 MAXScript 代码字符串。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功执行。
            - result (str): MAXScript 执行结果的字符串表示。
            - message (str): 操作描述信息。

    示例脚本 - 获取选中对象数量：
        execute_maxscript(script="selection.count")

    示例脚本 - 选中所有 Box 对象：
        execute_maxscript(script="select (for obj in objects where classOf obj == Box collect obj)")

    示例脚本 - 重置场景：
        execute_maxscript(script="resetMaxFile #noPrompt")

    示例脚本 - 设置渲染分辨率：
        execute_maxscript(script="renderWidth = 1920; renderHeight = 1080")
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        result = rt.execute(script)

        # 将结果转换为可序列化的字符串
        if result is None:
            result_str = "OK"
        elif isinstance(result, (int, float, bool)):
            result_str = str(result)
        elif isinstance(result, str):
            result_str = result
        else:
            result_str = str(result)

        return {
            "success": True,
            "result": result_str,
            "message": f"MAXScript 执行成功，返回值: {result_str}"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"MAXScript 执行失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
