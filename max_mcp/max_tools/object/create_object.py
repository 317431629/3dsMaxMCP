#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中创建基础几何体
# Version   : 1.0
# Comment   : 支持创建 Box/Sphere/Cylinder/Plane/Torus/Cone 等常见几何体


def create_object(object_type: str, name: str = "", position: str = "0,0,0", params: str = "") -> dict:
    """在 3ds Max 场景中创建一个基础几何体对象。

    支持的几何体类型（object_type 参数）：
    - Box: 长方体，参数: length, width, height, lengthsegs, widthsegs, heightsegs
    - Sphere: 球体，参数: radius, segments, smooth
    - Cylinder: 圆柱体，参数: radius, height, heightsegs, capsegs, sides, smooth
    - Plane: 平面，参数: length, width, lengthsegs, widthsegs
    - Torus: 圆环体，参数: radius1, radius2, segments, sides, smooth
    - Cone: 圆锥体，参数: radius1, radius2, height, heightsegs, capsegs, sides, smooth
    - Tube: 管状体，参数: radius1, radius2, height, heightsegs, capsegs, sides, smooth
    - Pyramid: 四棱锥，参数: width, depth, height
    - GeoSphere: 几何球体，参数: radius, segs
    - Teapot: 茶壶，参数: radius, segments, smooth
    - Hedra: 多面体，参数: radius, family, p, q
    - Torus_Knot: 圆环结，参数: radius, radius2, p, q, segments, sides
    以及 3ds Max 中任何可用的基础创建类名。

    Args:
        object_type: 几何体类型名称，如 "Box"、"Sphere"、"Cylinder" 等。
                     对于名称含空格的类型，使用下划线代替空格，如 "Torus_Knot"。
        name: 对象名称。如果为空字符串则使用 3ds Max 的默认命名。
        position: 对象的世界坐标位置，格式为 "x,y,z"，如 "0,0,0" 或 "100,50,0"。
                  默认值为 "0,0,0"（世界原点）。
        params: 对象创建参数的 JSON 字符串，键为属性名，值为属性值。
                例如: '{"radius": 30, "segments": 32}' 用于创建球体。
                例如: '{"length": 50, "width": 40, "height": 30}' 用于创建长方体。
                如果为空字符串则使用默认参数。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - name (str): 创建的对象名称。
            - object_type (str): 对象类型。
            - position (list): 对象的位置坐标 [x, y, z]。
            - applied_params (dict): 成功应用的参数。
            - message (str): 操作描述信息。

    示例调用 - 创建一个默认球体：
        create_object(object_type="Sphere")

    示例调用 - 在指定位置创建带参数的长方体：
        create_object(object_type="Box", name="MyBox", position="100,0,0", params='{"length": 50, "width": 40, "height": 30}')

    示例调用 - 创建圆柱体：
        create_object(object_type="Cylinder", name="MyCylinder", position="0,50,0", params='{"radius": 20, "height": 60, "sides": 24}')

    示例调用 - 创建平面：
        create_object(object_type="Plane", params='{"length": 200, "width": 200, "lengthsegs": 10, "widthsegs": 10}')
    """
    import pymxs
    import json
    import traceback

    rt = pymxs.runtime

    try:
        # 1. 解析位置
        try:
            pos_parts = [float(p.strip()) for p in position.split(",")]
            if len(pos_parts) != 3:
                return {
                    "success": False,
                    "message": f"位置参数格式错误，需要 3 个数值（x,y,z），实际得到 {len(pos_parts)} 个。"
                }
            pos = rt.Point3(pos_parts[0], pos_parts[1], pos_parts[2])
        except ValueError:
            return {
                "success": False,
                "message": f"位置参数 '{position}' 包含无效数值，请使用 'x,y,z' 格式。"
            }

        # 2. 解析创建参数
        create_params = {}
        if params and params.strip():
            try:
                create_params = json.loads(params)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"params JSON 解析失败: {str(e)}，请检查参数格式。"
                }

        # 3. 构建 MAXScript 创建命令
        # 将下划线替换为空格以支持如 "Torus_Knot" -> "Torus Knot"
        max_type_name = object_type.replace("_", " ")

        # 构建参数字符串
        param_parts = [f'pos:{rt.Point3(pos_parts[0], pos_parts[1], pos_parts[2])}']

        # 如果指定了名称，加入 name 参数
        if name and name.strip():
            param_parts.append(f'name:"{name.strip()}"')

        # 添加自定义创建参数
        for key, value in create_params.items():
            if isinstance(value, str):
                param_parts.append(f'{key}:"{value}"')
            elif isinstance(value, bool):
                param_parts.append(f'{key}:{"true" if value else "false"}')
            else:
                param_parts.append(f'{key}:{value}')

        # 使用 MAXScript 创建对象
        maxscript_cmd = f'{object_type} {" ".join(param_parts)}'
        obj = rt.execute(maxscript_cmd)

        if obj is None:
            # 尝试使用空格版本
            maxscript_cmd = f'"{max_type_name}" {" ".join(param_parts)}'
            obj = rt.execute(maxscript_cmd)

        if obj is None:
            return {
                "success": False,
                "message": f"无法创建类型为 '{object_type}' 的对象，请确认对象类型名称是否正确。"
            }

        # 4. 获取创建结果信息
        obj_name = str(obj.name)
        obj_pos = obj.pos
        actual_pos = [float(obj_pos.x), float(obj_pos.y), float(obj_pos.z)]

        # 收集实际应用的参数
        applied_params = {}
        for key in create_params:
            try:
                val = rt.getProperty(obj, rt.Name(key))
                applied_params[key] = float(val) if isinstance(val, (int, float)) else str(val)
            except Exception:
                applied_params[key] = create_params[key]

        return {
            "success": True,
            "name": obj_name,
            "object_type": object_type,
            "position": actual_pos,
            "applied_params": applied_params,
            "message": f"已成功创建 {object_type} 对象 '{obj_name}'，位置: [{actual_pos[0]}, {actual_pos[1]}, {actual_pos[2]}]。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"创建对象失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
