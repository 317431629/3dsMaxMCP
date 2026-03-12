#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 删除 3ds Max 场景中的物体
# Version   : 1.0
# Comment   : 支持按名称删除单个或多个对象，支持通配符


def delete_object(object_name: str) -> dict:
    """删除 3ds Max 场景中的指定物体。

    该工具可以删除场景中指定名称的对象。支持通配符 "*" 进行批量删除。

    Args:
        object_name: 要删除的物体名称。支持以下格式：
                     - 精确名称：如 "Box001"，删除指定物体。
                     - 通配符：如 "Box*"，删除所有以 "Box" 开头的物体。
                     - 多个名称：用英文逗号分隔，如 "Box001,Sphere001,Cylinder001"。
                     - 特殊值 "*"：删除场景中所有对象（谨慎使用！）。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - deleted (list): 被删除的对象名称列表。
            - deleted_count (int): 被删除的对象数量。
            - not_found (list): 未找到的对象名称列表（仅精确匹配时）。
            - message (str): 操作描述信息。

    示例调用 - 删除单个物体：
        delete_object(object_name="Box001")

    示例调用 - 批量删除（通配符）：
        delete_object(object_name="Box*")

    示例调用 - 删除多个指定物体：
        delete_object(object_name="Box001,Sphere001,Cylinder001")

    示例调用 - 删除所有物体：
        delete_object(object_name="*")
    """
    import pymxs
    import traceback
    import fnmatch

    rt = pymxs.runtime

    try:
        deleted = []
        not_found = []

        # 检查是否包含通配符
        names = [n.strip() for n in object_name.split(",")]

        for name_pattern in names:
            if not name_pattern:
                continue

            # 判断是否含有通配符
            has_wildcard = "*" in name_pattern or "?" in name_pattern

            if has_wildcard:
                # 通配符模式：遍历所有对象进行匹配
                # 先收集要删除的对象（避免在遍历中删除导致问题）
                to_delete = []
                for obj in list(rt.objects):
                    if fnmatch.fnmatch(str(obj.name), name_pattern):
                        to_delete.append(obj)

                for obj in to_delete:
                    obj_name = str(obj.name)
                    try:
                        rt.delete(obj)
                        deleted.append(obj_name)
                    except Exception as del_err:
                        not_found.append(f"{obj_name} (删除失败: {str(del_err)})")
            else:
                # 精确匹配模式
                obj = rt.getNodeByName(name_pattern)
                if obj is None:
                    not_found.append(name_pattern)
                else:
                    obj_name = str(obj.name)
                    rt.delete(obj)
                    deleted.append(obj_name)

        # 构建结果消息
        msg_parts = []
        if deleted:
            msg_parts.append(f"已成功删除 {len(deleted)} 个对象: {', '.join(deleted)}")
        if not_found:
            msg_parts.append(f"未找到或删除失败的对象: {', '.join(not_found)}")
        if not deleted and not not_found:
            msg_parts.append("未匹配到任何对象。")

        return {
            "success": len(deleted) > 0,
            "deleted": deleted,
            "deleted_count": len(deleted),
            "not_found": not_found,
            "message": "。".join(msg_parts) + "。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"删除对象失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
