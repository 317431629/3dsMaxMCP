#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中新建场景
# Version   : 1.0
# Comment   : 支持强制重置（不提示保存）


def new_scene(force: str = "true") -> dict:
    """在 3ds Max 中新建/重置场景。

    该工具将清空当前场景并创建一个新的空场景。

    Args:
        force: 是否强制新建（不提示保存当前场景）。
               "true"（默认）表示强制新建，不保存当前更改。
               "false" 表示如果当前场景有未保存更改，会先保存。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - message (str): 操作描述信息。

    示例调用 - 强制新建：
        new_scene()

    示例调用 - 保存后新建：
        new_scene(force="false")
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        is_force = force.strip().lower() != "false"

        if is_force:
            rt.resetMaxFile(rt.Name("noPrompt"))
        else:
            # 先保存（如果有文件路径）
            current_name = str(rt.maxFileName)
            if current_name and current_name.strip():
                import os
                full_path = os.path.join(str(rt.maxFilePath), current_name)
                rt.saveMaxFile(full_path)
            rt.resetMaxFile(rt.Name("noPrompt"))

        return {
            "success": True,
            "message": "已成功创建新场景。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"新建场景失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
