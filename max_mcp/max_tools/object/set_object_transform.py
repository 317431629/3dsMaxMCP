#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 设置 3ds Max 物体的变换属性
# Version   : 1.0
# Comment   : 支持设置位置、旋转、缩放，可选绝对/相对模式


def set_object_transform(object_name: str, position: str = "", rotation: str = "", scale: str = "", relative: str = "false") -> dict:
    """设置 3ds Max 场景中指定物体的变换属性（位置/旋转/缩放）。

    该工具可以设置物体的位置、旋转和缩放，支持绝对模式和相对模式。
    可以同时设置多个变换属性，也可以只设置其中一个。

    Args:
        object_name: 目标物体的名称（场景中已存在的对象）。
        position: 位置坐标，格式为 "x,y,z"，如 "100,50,0"。
                  留空则不改变位置。
        rotation: 旋转欧拉角（度数），格式为 "x,y,z"，如 "0,0,45"。
                  留空则不改变旋转。
        scale: 缩放比例，格式为 "x,y,z"，如 "2,2,2"（等比放大2倍）。
               也可使用单个值表示等比缩放，如 "1.5"（等同于 "1.5,1.5,1.5"）。
               留空则不改变缩放。
        relative: 是否使用相对模式。"true" 表示在当前值基础上叠加，
                  "false"（默认）表示设置为绝对值。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - object_name (str): 物体名称。
            - old_transform (dict): 变换前的值。
            - new_transform (dict): 变换后的值。
            - message (str): 操作描述信息。

    示例调用 - 移动物体到指定位置：
        set_object_transform(object_name="Box001", position="100,0,50")

    示例调用 - 旋转物体45度（Z轴）：
        set_object_transform(object_name="Box001", rotation="0,0,45")

    示例调用 - 等比缩放物体：
        set_object_transform(object_name="Box001", scale="2,2,2")

    示例调用 - 相对移动物体（在当前位置基础上偏移）：
        set_object_transform(object_name="Box001", position="10,0,0", relative="true")

    示例调用 - 同时设置位置和旋转：
        set_object_transform(object_name="Box001", position="100,50,0", rotation="0,0,90")
    """
    import pymxs
    import traceback
    import math

    rt = pymxs.runtime

    try:
        # 1. 查找目标物体
        obj = rt.getNodeByName(object_name)
        if obj is None:
            return {
                "success": False,
                "message": f"未找到名为 '{object_name}' 的物体，请确认物体名称是否正确。"
            }

        is_relative = relative.lower().strip() == "true"

        # 记录旧的变换值
        old_pos = obj.pos
        old_transform = {
            "position": [float(old_pos.x), float(old_pos.y), float(old_pos.z)]
        }
        try:
            old_rot = rt.quatToEuler(obj.rotation)
            old_transform["rotation"] = [float(old_rot.x), float(old_rot.y), float(old_rot.z)]
        except Exception:
            old_transform["rotation"] = [0.0, 0.0, 0.0]
        try:
            old_scl = obj.scale
            old_transform["scale"] = [float(old_scl.x), float(old_scl.y), float(old_scl.z)]
        except Exception:
            old_transform["scale"] = [1.0, 1.0, 1.0]

        changes = []

        # 2. 设置位置
        if position and position.strip():
            try:
                parts = [float(p.strip()) for p in position.split(",")]
                if len(parts) != 3:
                    return {"success": False, "message": f"位置参数需要 3 个值 (x,y,z)，实际得到 {len(parts)} 个。"}
                if is_relative:
                    obj.pos = rt.Point3(old_pos.x + parts[0], old_pos.y + parts[1], old_pos.z + parts[2])
                else:
                    obj.pos = rt.Point3(parts[0], parts[1], parts[2])
                changes.append("位置")
            except ValueError:
                return {"success": False, "message": f"位置参数 '{position}' 包含无效数值。"}

        # 3. 设置旋转
        if rotation and rotation.strip():
            try:
                parts = [float(p.strip()) for p in rotation.split(",")]
                if len(parts) != 3:
                    return {"success": False, "message": f"旋转参数需要 3 个值 (x,y,z)，实际得到 {len(parts)} 个。"}
                if is_relative:
                    new_euler = rt.EulerAngles(
                        old_transform["rotation"][0] + parts[0],
                        old_transform["rotation"][1] + parts[1],
                        old_transform["rotation"][2] + parts[2]
                    )
                else:
                    new_euler = rt.EulerAngles(parts[0], parts[1], parts[2])
                obj.rotation = rt.execute(f'eulerToQuat (eulerAngles {new_euler.x} {new_euler.y} {new_euler.z})')
                changes.append("旋转")
            except ValueError:
                return {"success": False, "message": f"旋转参数 '{rotation}' 包含无效数值。"}

        # 4. 设置缩放
        if scale and scale.strip():
            try:
                parts = [float(p.strip()) for p in scale.split(",")]
                if len(parts) == 1:
                    parts = [parts[0], parts[0], parts[0]]
                elif len(parts) != 3:
                    return {"success": False, "message": f"缩放参数需要 1 或 3 个值，实际得到 {len(parts)} 个。"}
                if is_relative:
                    obj.scale = rt.Point3(
                        old_transform["scale"][0] * parts[0],
                        old_transform["scale"][1] * parts[1],
                        old_transform["scale"][2] * parts[2]
                    )
                else:
                    obj.scale = rt.Point3(parts[0], parts[1], parts[2])
                changes.append("缩放")
            except ValueError:
                return {"success": False, "message": f"缩放参数 '{scale}' 包含无效数值。"}

        # 5. 获取新的变换值
        new_pos = obj.pos
        new_transform = {
            "position": [float(new_pos.x), float(new_pos.y), float(new_pos.z)]
        }
        try:
            new_rot = rt.quatToEuler(obj.rotation)
            new_transform["rotation"] = [float(new_rot.x), float(new_rot.y), float(new_rot.z)]
        except Exception:
            new_transform["rotation"] = old_transform["rotation"]
        try:
            new_scl = obj.scale
            new_transform["scale"] = [float(new_scl.x), float(new_scl.y), float(new_scl.z)]
        except Exception:
            new_transform["scale"] = old_transform["scale"]

        if not changes:
            return {
                "success": True,
                "object_name": object_name,
                "old_transform": old_transform,
                "new_transform": new_transform,
                "message": f"未指定任何变换参数，物体 '{object_name}' 未做任何修改。"
            }

        mode_str = "相对" if is_relative else "绝对"
        return {
            "success": True,
            "object_name": object_name,
            "old_transform": old_transform,
            "new_transform": new_transform,
            "message": f"已成功设置物体 '{object_name}' 的{'/'.join(changes)}（{mode_str}模式）。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"设置物体变换失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
