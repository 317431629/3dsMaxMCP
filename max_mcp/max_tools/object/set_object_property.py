#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 设置 3ds Max 物体的通用属性
# Version   : 1.0
# Comment   : 支持设置可见性、颜色、冻结等通用属性，以及对象的创建参数


def set_object_property(object_name: str, property_name: str, property_value: str) -> dict:
    """设置 3ds Max 场景中指定物体的属性值。

    该工具可以设置物体的各种属性，包括显示属性和创建参数。

    常用属性名称（property_name 参数）：
    - wirecolor: 线框颜色，值格式 "r,g,b" (0-255)，如 "255,0,0"
    - isHidden: 是否隐藏，值 "true" 或 "false"
    - isFrozen: 是否冻结，值 "true" 或 "false"
    - renderable: 是否可渲染，值 "true" 或 "false"
    - boxMode: 是否以盒模式显示，值 "true" 或 "false"
    - backfaceCull: 是否背面剔除，值 "true" 或 "false"
    - 以及对象的创建参数（如 radius、length、width、height、segments 等）

    Args:
        object_name: 目标物体名称。支持通配符 "*" 进行批量设置。
        property_name: 属性名称。
        property_value: 属性值（字符串形式）。
                        数字值: "30"、"1.5"
                        布尔值: "true"、"false"
                        颜色值: "255,0,0"（仅 wirecolor 属性使用）

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - modified (list): 成功修改的物体列表。
            - property_name (str): 属性名称。
            - property_value (str): 设置的属性值。
            - message (str): 操作描述信息。

    示例调用 - 设置线框颜色为红色：
        set_object_property(object_name="Box001", property_name="wirecolor", property_value="255,0,0")

    示例调用 - 隐藏物体：
        set_object_property(object_name="Box001", property_name="isHidden", property_value="true")

    示例调用 - 修改球体半径：
        set_object_property(object_name="Sphere001", property_name="radius", property_value="50")

    示例调用 - 批量冻结所有 Box：
        set_object_property(object_name="Box*", property_name="isFrozen", property_value="true")
    """
    import pymxs
    import traceback
    import fnmatch

    rt = pymxs.runtime

    try:
        # 1. 查找目标物体
        has_wildcard = "*" in object_name or "?" in object_name
        target_objects = []

        if has_wildcard:
            for obj in rt.objects:
                if fnmatch.fnmatch(str(obj.name), object_name):
                    target_objects.append(obj)
        else:
            obj = rt.getNodeByName(object_name)
            if obj:
                target_objects.append(obj)

        if not target_objects:
            return {
                "success": False,
                "message": f"未找到匹配 '{object_name}' 的物体。"
            }

        # 2. 解析属性值
        prop_name = property_name.strip()
        prop_value_str = property_value.strip()

        modified = []
        errors = []

        for obj in target_objects:
            obj_name = str(obj.name)
            try:
                if prop_name.lower() == "wirecolor":
                    # 特殊处理颜色
                    rgb = [int(c.strip()) for c in prop_value_str.split(",")]
                    if len(rgb) != 3:
                        errors.append(f"{obj_name}: 颜色需要 3 个值")
                        continue
                    obj.wirecolor = rt.Color(rgb[0], rgb[1], rgb[2])
                elif prop_value_str.lower() in ("true", "false"):
                    # 布尔值
                    bool_val = prop_value_str.lower() == "true"
                    rt.setProperty(obj, rt.Name(prop_name), bool_val)
                else:
                    # 尝试数字
                    try:
                        if "." in prop_value_str:
                            val = float(prop_value_str)
                        else:
                            val = int(prop_value_str)
                    except ValueError:
                        val = prop_value_str

                    # 先尝试在节点上设置
                    try:
                        rt.setProperty(obj, rt.Name(prop_name), val)
                    except Exception:
                        # 再尝试在 baseObject 上设置（创建参数）
                        base_obj = obj.baseObject if hasattr(obj, 'baseObject') else obj
                        rt.setProperty(base_obj, rt.Name(prop_name), val)

                modified.append(obj_name)

            except Exception as e:
                errors.append(f"{obj_name}: {str(e)}")

        # 3. 构建结果
        msg_parts = []
        if modified:
            msg_parts.append(f"已为 {len(modified)} 个物体设置 {prop_name} = {prop_value_str}")
        if errors:
            msg_parts.append(f"设置失败: {'; '.join(errors)}")

        return {
            "success": len(modified) > 0,
            "modified": modified,
            "errors": errors,
            "property_name": prop_name,
            "property_value": prop_value_str,
            "message": "。".join(msg_parts) + "。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"设置属性失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
