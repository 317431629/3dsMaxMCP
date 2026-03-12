#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中为物体设置关键帧
# Version   : 1.0
# Comment   : 支持为物体的位置/旋转/缩放/自定义属性设置关键帧


def set_keyframe(object_name: str, frame: str, position: str = "", rotation: str = "", scale: str = "", property_name: str = "", property_value: str = "") -> dict:
    """在 3ds Max 中为指定物体的属性设置关键帧。

    该工具可以在指定帧为物体的变换属性（位置/旋转/缩放）或自定义属性设置关键帧。

    Args:
        object_name: 目标物体名称。
        frame: 关键帧所在的帧号，如 "0"、"30"、"60"。
        position: 在该帧的位置值，格式 "x,y,z"。留空表示不设置位置关键帧。
        rotation: 在该帧的旋转值（欧拉角度数），格式 "x,y,z"。留空表示不设置旋转关键帧。
        scale: 在该帧的缩放值，格式 "x,y,z" 或单个值如 "2"。留空表示不设置缩放关键帧。
        property_name: 自定义属性名（如 "radius"、"height" 等）。与 property_value 配合使用。
        property_value: 自定义属性在该帧的值。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - object_name (str): 物体名称。
            - frame (int): 关键帧号。
            - keys_set (list): 成功设置的关键帧类型列表。
            - message (str): 操作描述信息。

    示例调用 - 设置位置关键帧：
        set_keyframe(object_name="Box001", frame="0", position="0,0,0")
        set_keyframe(object_name="Box001", frame="30", position="100,0,0")

    示例调用 - 设置位置和旋转关键帧：
        set_keyframe(object_name="Box001", frame="0", position="0,0,0", rotation="0,0,0")
        set_keyframe(object_name="Box001", frame="60", position="100,0,0", rotation="0,0,360")

    示例调用 - 设置自定义属性关键帧（如半径动画）：
        set_keyframe(object_name="Sphere001", frame="0", property_name="radius", property_value="10")
        set_keyframe(object_name="Sphere001", frame="30", property_name="radius", property_value="50")
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        # 1. 查找目标物体
        obj = rt.getNodeByName(object_name)
        if obj is None:
            return {
                "success": False,
                "message": f"未找到名为 '{object_name}' 的物体，请确认物体名称是否正确。"
            }

        # 2. 解析帧号
        try:
            frame_num = int(frame.strip())
        except ValueError:
            return {"success": False, "message": f"帧号参数 '{frame}' 不是有效整数。"}

        keys_set = []
        errors = []

        # 使用 pymxs.animate 和 pymxs.attime 上下文管理器设置关键帧
        with pymxs.animate(True):
            with pymxs.attime(frame_num):
                # 3. 设置位置关键帧
                if position and position.strip():
                    try:
                        parts = [float(p.strip()) for p in position.split(",")]
                        if len(parts) != 3:
                            errors.append(f"位置参数需要 3 个值，实际得到 {len(parts)} 个")
                        else:
                            obj.pos = rt.Point3(parts[0], parts[1], parts[2])
                            keys_set.append("position")
                    except ValueError:
                        errors.append(f"位置参数包含无效数值")

                # 4. 设置旋转关键帧
                if rotation and rotation.strip():
                    try:
                        parts = [float(p.strip()) for p in rotation.split(",")]
                        if len(parts) != 3:
                            errors.append(f"旋转参数需要 3 个值，实际得到 {len(parts)} 个")
                        else:
                            quat = rt.execute(f'eulerToQuat (eulerAngles {parts[0]} {parts[1]} {parts[2]})')
                            obj.rotation = quat
                            keys_set.append("rotation")
                    except ValueError:
                        errors.append(f"旋转参数包含无效数值")

                # 5. 设置缩放关键帧
                if scale and scale.strip():
                    try:
                        parts = [float(p.strip()) for p in scale.split(",")]
                        if len(parts) == 1:
                            parts = [parts[0], parts[0], parts[0]]
                        elif len(parts) != 3:
                            errors.append(f"缩放参数需要 1 或 3 个值，实际得到 {len(parts)} 个")
                            parts = None
                        if parts:
                            obj.scale = rt.Point3(parts[0], parts[1], parts[2])
                            keys_set.append("scale")
                    except ValueError:
                        errors.append(f"缩放参数包含无效数值")

                # 6. 设置自定义属性关键帧
                if property_name and property_name.strip() and property_value and property_value.strip():
                    try:
                        prop_name = property_name.strip()
                        # 尝试数字
                        try:
                            if "." in property_value:
                                val = float(property_value.strip())
                            else:
                                val = int(property_value.strip())
                        except ValueError:
                            val = property_value.strip()

                        # 尝试在基础对象上设置
                        try:
                            rt.setProperty(obj, rt.Name(prop_name), val)
                        except Exception:
                            base_obj = obj.baseObject if hasattr(obj, 'baseObject') else obj
                            rt.setProperty(base_obj, rt.Name(prop_name), val)

                        keys_set.append(f"property:{prop_name}")
                    except Exception as prop_err:
                        errors.append(f"设置属性 {property_name} 失败: {str(prop_err)}")

        # 7. 构建结果
        msg_parts = []
        if keys_set:
            msg_parts.append(f"已在第 {frame_num} 帧为物体 '{object_name}' 设置了关键帧: {', '.join(keys_set)}")
        if errors:
            msg_parts.append(f"错误: {'; '.join(errors)}")

        return {
            "success": len(keys_set) > 0,
            "object_name": object_name,
            "frame": frame_num,
            "keys_set": keys_set,
            "errors": errors,
            "message": "。".join(msg_parts) + "。" if msg_parts else "未设置任何关键帧。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"设置关键帧失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
