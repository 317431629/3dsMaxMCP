#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中选择/取消选择对象
# Version   : 1.0
# Comment   : 支持按名称、通配符、类型进行选择操作


def select_objects(object_name: str = "", object_type: str = "", action: str = "select") -> dict:
    """在 3ds Max 场景中选择或取消选择对象。

    该工具可以按名称或类型选择场景中的对象，也可以清除当前选择。

    Args:
        object_name: 要选择的物体名称。支持以下格式：
                     - 精确名称：如 "Box001"
                     - 通配符：如 "Box*" 选择所有以 Box 开头的物体
                     - 多个名称：用英文逗号分隔，如 "Box001,Sphere001"
                     - 留空配合 object_type 使用，按类型选择
        object_type: 按类型选择，如 "Geometry"、"Light"、"Camera"、"Box"、"Sphere" 等。
                     可与 object_name 组合使用。
        action: 操作类型。
                - "select": 选择匹配的对象（默认），替换当前选择。
                - "add": 将匹配的对象添加到当前选择中。
                - "deselect": 从当前选择中移除匹配的对象。
                - "clear": 清除所有选择（忽略 object_name 和 object_type）。
                - "invert": 反转当前选择（忽略 object_name 和 object_type）。
                - "all": 选择所有对象（忽略 object_name 和 object_type）。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - selected (list): 当前选中的对象名称列表。
            - selected_count (int): 当前选中的对象数量。
            - message (str): 操作描述信息。

    示例调用 - 选择单个对象：
        select_objects(object_name="Box001")

    示例调用 - 按通配符选择：
        select_objects(object_name="Wall*")

    示例调用 - 按类型选择所有灯光：
        select_objects(object_type="Light")

    示例调用 - 清除选择：
        select_objects(action="clear")

    示例调用 - 选择所有对象：
        select_objects(action="all")
    """
    import pymxs
    import traceback
    import fnmatch

    rt = pymxs.runtime

    try:
        action_lower = action.strip().lower()

        # 特殊操作：清除、全选、反转
        if action_lower == "clear":
            rt.clearSelection()
            return {
                "success": True,
                "selected": [],
                "selected_count": 0,
                "message": "已清除所有选择。"
            }

        if action_lower == "all":
            rt.select(rt.objects)
            selected = [str(obj.name) for obj in rt.selection]
            return {
                "success": True,
                "selected": selected,
                "selected_count": len(selected),
                "message": f"已选择所有 {len(selected)} 个对象。"
            }

        if action_lower == "invert":
            # 反转选择
            currently_selected = set(str(obj.name) for obj in rt.selection)
            all_names = set(str(obj.name) for obj in rt.objects)
            to_select_names = all_names - currently_selected

            rt.clearSelection()
            for name in to_select_names:
                obj = rt.getNodeByName(name)
                if obj:
                    rt.selectMore(obj)

            selected = [str(obj.name) for obj in rt.selection]
            return {
                "success": True,
                "selected": selected,
                "selected_count": len(selected),
                "message": f"已反转选择，当前选中 {len(selected)} 个对象。"
            }

        # 按名称/类型匹配对象
        super_class_map = {
            "geometry": rt.GeometryClass,
            "light": rt.Light,
            "camera": rt.Camera,
            "helper": rt.Helper,
            "shape": rt.Shape,
        }

        matched_objects = []

        for obj in rt.objects:
            obj_name = str(obj.name)
            match = True

            # 名称过滤
            if object_name and object_name.strip():
                names = [n.strip() for n in object_name.split(",")]
                name_match = False
                for pattern in names:
                    if "*" in pattern or "?" in pattern:
                        if fnmatch.fnmatch(obj_name, pattern):
                            name_match = True
                            break
                    else:
                        if obj_name == pattern:
                            name_match = True
                            break
                if not name_match:
                    match = False

            # 类型过滤
            if match and object_type and object_type.strip():
                type_lower = object_type.strip().lower()
                if type_lower in super_class_map:
                    if not rt.isKindOf(obj, super_class_map[type_lower]):
                        match = False
                else:
                    class_name = str(rt.classOf(obj)).lower().replace(" ", "_")
                    if class_name != type_lower.replace(" ", "_"):
                        match = False

            if match:
                matched_objects.append(obj)

        if not object_name and not object_type:
            return {
                "success": False,
                "message": "请指定 object_name 或 object_type 参数。"
            }

        # 执行选择操作
        if action_lower == "select":
            rt.clearSelection()
            for obj in matched_objects:
                rt.selectMore(obj)
        elif action_lower == "add":
            for obj in matched_objects:
                rt.selectMore(obj)
        elif action_lower == "deselect":
            for obj in matched_objects:
                rt.deselect(obj)
        else:
            return {
                "success": False,
                "message": f"不支持的操作类型 '{action}'，可选值: select, add, deselect, clear, invert, all。"
            }

        # 返回结果
        selected = [str(obj.name) for obj in rt.selection]

        return {
            "success": True,
            "selected": selected,
            "selected_count": len(selected),
            "matched_count": len(matched_objects),
            "message": f"操作 '{action_lower}' 完成，匹配了 {len(matched_objects)} 个对象，当前选中 {len(selected)} 个对象。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"选择操作失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
