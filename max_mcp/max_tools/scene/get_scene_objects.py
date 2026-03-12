#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 获取 3ds Max 场景中的对象列表
# Version   : 1.0
# Comment   : 支持按类型过滤，返回对象名称、类型、位置等信息


def get_scene_objects(object_type: str = "", name_filter: str = "") -> dict:
    """获取当前 3ds Max 场景中的所有对象信息。

    该工具可以列出场景中的所有对象，或者按类型/名称进行过滤。
    返回每个对象的名称、类型、位置、是否隐藏等基本信息。

    支持的过滤类型（object_type 参数）：
    - "": 返回所有对象（默认）
    - "Geometry": 仅返回几何体对象（Box、Sphere、Mesh 等）
    - "Light": 仅返回灯光对象
    - "Camera": 仅返回相机对象
    - "Helper": 仅返回辅助对象（Dummy、Point 等）
    - "Shape": 仅返回样条线/形状对象（Line、Circle、Rectangle 等）
    - "SpaceWarp": 仅返回空间扭曲对象
    - "Bone": 仅返回骨骼对象
    也支持具体的类名，如 "Box"、"Sphere"、"Editable_Mesh" 等。

    Args:
        object_type: 按类型过滤对象，可以是超类名（如 "Geometry"）或具体类名（如 "Box"）。
                     如果为空字符串则返回所有对象。
        name_filter: 按名称过滤对象，支持通配符 "*"。
                     例如: "Box*" 匹配所有以 "Box" 开头的对象。
                     如果为空字符串则不按名称过滤。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - objects (list): 对象信息列表，每个元素包含：
                - name (str): 对象名称。
                - class_name (str): 对象类名。
                - super_class (str): 对象超类名。
                - position (list): 位置坐标 [x, y, z]。
                - is_hidden (bool): 是否隐藏。
                - is_frozen (bool): 是否冻结。
            - count (int): 返回的对象数量。
            - total_in_scene (int): 场景中的总对象数量。
            - message (str): 描述信息。

    示例调用 - 获取所有对象：
        get_scene_objects()

    示例调用 - 仅获取几何体：
        get_scene_objects(object_type="Geometry")

    示例调用 - 按名称过滤：
        get_scene_objects(name_filter="Box*")

    示例调用 - 按类型和名称组合过滤：
        get_scene_objects(object_type="Geometry", name_filter="Wall*")
    """
    import pymxs
    import traceback
    import fnmatch

    rt = pymxs.runtime

    try:
        all_objects = list(rt.objects)
        total_count = len(all_objects)

        # 超类映射（用于按大类过滤）
        super_class_map = {
            "geometry": rt.GeometryClass,
            "light": rt.Light,
            "camera": rt.Camera,
            "helper": rt.Helper,
            "shape": rt.Shape,
            "spacewarp": rt.SpacewarpObject,
        }

        filtered_objects = []

        for obj in all_objects:
            # 按类型过滤
            if object_type and object_type.strip():
                type_lower = object_type.strip().lower()

                # 检查是否是超类过滤
                if type_lower in super_class_map:
                    if not rt.isKindOf(obj, super_class_map[type_lower]):
                        continue
                elif type_lower == "bone":
                    # 骨骼特殊处理
                    if not (rt.isKindOf(obj, rt.BoneGeometry) or
                            (hasattr(rt, 'Biped_Object') and rt.isKindOf(obj, rt.Biped_Object))):
                        continue
                else:
                    # 按具体类名过滤
                    class_name = str(rt.classOf(obj))
                    if class_name.lower().replace(" ", "_") != type_lower.replace(" ", "_"):
                        continue

            # 按名称过滤（支持通配符）
            if name_filter and name_filter.strip():
                obj_name = str(obj.name)
                if not fnmatch.fnmatch(obj_name, name_filter.strip()):
                    continue

            # 收集对象信息
            try:
                obj_pos = obj.pos
                position = [float(obj_pos.x), float(obj_pos.y), float(obj_pos.z)]
            except Exception:
                position = [0, 0, 0]

            try:
                is_hidden = bool(obj.isHidden)
            except Exception:
                is_hidden = False

            try:
                is_frozen = bool(obj.isFrozen)
            except Exception:
                is_frozen = False

            obj_info = {
                "name": str(obj.name),
                "class_name": str(rt.classOf(obj)),
                "super_class": str(rt.superClassOf(obj)),
                "position": position,
                "is_hidden": is_hidden,
                "is_frozen": is_frozen,
            }
            filtered_objects.append(obj_info)

        filter_desc = ""
        if object_type:
            filter_desc += f"类型='{object_type}'"
        if name_filter:
            filter_desc += f"{' 且 ' if filter_desc else ''}名称匹配='{name_filter}'"

        return {
            "success": True,
            "objects": filtered_objects,
            "count": len(filtered_objects),
            "total_in_scene": total_count,
            "message": f"场景共 {total_count} 个对象"
                       + (f"，按 {filter_desc} 过滤后得到 {len(filtered_objects)} 个对象" if filter_desc else "")
                       + "。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取场景对象失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
