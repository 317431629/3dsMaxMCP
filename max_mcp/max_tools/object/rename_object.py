#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 重命名 3ds Max 场景中的物体
# Version   : 1.0
# Comment   : 支持重命名单个对象


def rename_object(object_name: str, new_name: str) -> dict:
    """重命名 3ds Max 场景中的指定物体。

    Args:
        object_name: 当前物体名称（场景中已存在的对象）。
        new_name: 新的物体名称。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - old_name (str): 原名称。
            - new_name (str): 新名称。
            - message (str): 操作描述信息。

    示例调用：
        rename_object(object_name="Box001", new_name="Wall_Left")
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        obj = rt.getNodeByName(object_name)
        if obj is None:
            return {
                "success": False,
                "message": f"未找到名为 '{object_name}' 的物体，请确认物体名称是否正确。"
            }

        if not new_name or not new_name.strip():
            return {
                "success": False,
                "message": "新名称不能为空。"
            }

        old_name = str(obj.name)
        obj.name = new_name.strip()
        actual_new_name = str(obj.name)

        return {
            "success": True,
            "old_name": old_name,
            "new_name": actual_new_name,
            "message": f"已将物体 '{old_name}' 重命名为 '{actual_new_name}'。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"重命名失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
