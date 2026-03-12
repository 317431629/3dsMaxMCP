#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 获取 3ds Max 中物体的详细属性信息
# Version   : 1.0
# Comment   : 返回物体的变换、尺寸、修改器列表、材质等信息


def get_object_properties(object_name: str) -> dict:
    """获取 3ds Max 场景中指定物体的详细属性信息。

    该工具返回物体的变换信息（位置/旋转/缩放）、几何属性、修改器列表、
    材质信息等综合属性数据，帮助 AI 了解物体的当前状态。

    Args:
        object_name: 目标物体的名称（场景中已存在的对象）。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - name (str): 物体名称。
            - class_name (str): 物体类名（如 Box, Sphere, Editable_Poly 等）。
            - super_class (str): 物体超类名（如 GeometryClass, Light 等）。
            - transform (dict): 变换信息。
                - position (list): 位置 [x, y, z]。
                - rotation (list): 旋转欧拉角 [x, y, z]（度数）。
                - scale (list): 缩放 [x, y, z]。
            - properties (dict): 物体的创建参数（如 radius, length 等）。
            - modifiers (list): 修改器列表，每个包含 name 和 class_name。
            - material (dict|None): 材质信息（如果有）。
            - is_hidden (bool): 是否隐藏。
            - is_frozen (bool): 是否冻结。
            - wirecolor (list): 线框颜色 [r, g, b]。
            - vertex_count (int): 顶点数（如果是网格对象）。
            - face_count (int): 面数（如果是网格对象）。
            - message (str): 操作描述信息。

    示例调用：
        get_object_properties(object_name="Box001")

    示例调用：
        get_object_properties(object_name="MCP_Sphere")
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

        # 2. 基本信息
        class_name = str(rt.classOf(obj))
        super_class = str(rt.superClassOf(obj))

        # 3. 变换信息
        pos = obj.pos
        position = [float(pos.x), float(pos.y), float(pos.z)]

        # 旋转（转换为欧拉角度数）
        try:
            rot = obj.rotation
            euler = rt.quatToEuler(rot)
            rotation = [float(euler.x), float(euler.y), float(euler.z)]
        except Exception:
            rotation = [0.0, 0.0, 0.0]

        # 缩放
        try:
            scl = obj.scale
            scale = [float(scl.x), float(scl.y), float(scl.z)]
        except Exception:
            scale = [1.0, 1.0, 1.0]

        transform = {
            "position": position,
            "rotation": rotation,
            "scale": scale
        }

        # 4. 获取物体创建参数属性
        properties = {}
        try:
            # 获取基础对象的属性列表
            base_obj = rt.getProperty(obj, rt.Name("baseObject")) if rt.isProperty(obj, rt.Name("baseObject")) else obj
            prop_names = rt.getPropNames(base_obj)
            if prop_names:
                for prop_name in prop_names:
                    try:
                        val = rt.getProperty(base_obj, prop_name)
                        # 转换为 Python 可序列化类型
                        if isinstance(val, (int, float)):
                            properties[str(prop_name)] = float(val)
                        elif isinstance(val, bool):
                            properties[str(prop_name)] = bool(val)
                        elif isinstance(val, str):
                            properties[str(prop_name)] = val
                        else:
                            properties[str(prop_name)] = str(val)
                    except Exception:
                        pass
        except Exception:
            pass

        # 5. 修改器列表
        modifiers = []
        try:
            mod_count = obj.modifiers.count
            for i in range(1, mod_count + 1):
                mod = obj.modifiers[i]
                modifiers.append({
                    "name": str(mod.name),
                    "class_name": str(rt.classOf(mod))
                })
        except Exception:
            pass

        # 6. 材质信息
        material = None
        try:
            mat = obj.material
            if mat is not None:
                material = {
                    "name": str(mat.name),
                    "class_name": str(rt.classOf(mat))
                }
        except Exception:
            pass

        # 7. 显示属性
        try:
            is_hidden = bool(obj.isHidden)
        except Exception:
            is_hidden = False

        try:
            is_frozen = bool(obj.isFrozen)
        except Exception:
            is_frozen = False

        # 线框颜色
        try:
            wc = obj.wirecolor
            wirecolor = [int(wc.r), int(wc.g), int(wc.b)]
        except Exception:
            wirecolor = [0, 0, 0]

        # 8. 网格信息（顶点数/面数）
        vertex_count = 0
        face_count = 0
        try:
            # 尝试获取网格信息
            mesh = rt.snapshotAsMesh(obj)
            if mesh:
                vertex_count = int(rt.getNumVerts(mesh))
                face_count = int(rt.getNumFaces(mesh))
                rt.delete(mesh)
        except Exception:
            pass

        return {
            "success": True,
            "name": str(obj.name),
            "class_name": class_name,
            "super_class": super_class,
            "transform": transform,
            "properties": properties,
            "modifiers": modifiers,
            "material": material,
            "is_hidden": is_hidden,
            "is_frozen": is_frozen,
            "wirecolor": wirecolor,
            "vertex_count": vertex_count,
            "face_count": face_count,
            "message": f"物体 '{object_name}' 的属性信息获取成功。类型: {class_name}，位置: {position}，"
                       + f"修改器: {len(modifiers)} 个，"
                       + (f"材质: {material['name']}，" if material else "无材质，")
                       + f"顶点数: {vertex_count}，面数: {face_count}。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取物体属性失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
