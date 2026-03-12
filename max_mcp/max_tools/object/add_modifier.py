#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 为 3ds Max 中的物体添加修改器
# Version   : 1.0
# Comment   : 支持常见修改器类型，并可通过参数字典设置修改器属性


def add_modifier(object_name: str, modifier_type: str, modifier_params: str = "") -> dict:
    """为 3ds Max 场景中的指定物体添加修改器(Modifier)。

    该工具可以为场景中已存在的物体添加各种修改器，如 Bend、Twist、Taper、
    TurboSmooth、Shell、UVW Map、Noise、Lattice、MeshSmooth 等。

    支持的常见修改器类型（modifier_type 参数）：
    - Bend: 弯曲修改器
    - Twist: 扭曲修改器
    - Taper: 锥化修改器
    - TurboSmooth: 涡轮平滑
    - MeshSmooth: 网格平滑
    - Shell: 壳修改器（给面片添加厚度）
    - Noise: 噪波修改器
    - Lattice: 晶格修改器
    - UVW_Map: UVW 贴图修改器（注意使用下划线代替空格）
    - Symmetry: 对称修改器
    - FFD_4x4x4: 自由变形修改器
    - Smooth: 平滑修改器
    - Relax: 松弛修改器
    - Push: 推力修改器
    - Stretch: 拉伸修改器
    - Squeeze: 挤压修改器
    - Ripple: 涟漪修改器
    - Wave: 波浪修改器
    - Skew: 倾斜修改器
    - Spherify: 球形化修改器
    - Edit_Poly: 编辑多边形修改器
    - Edit_Mesh: 编辑网格修改器
    以及 3ds Max 中任何可用的修改器类名。

    Args:
        object_name: 目标物体的名称（场景中已存在的对象）。
        modifier_type: 修改器类型名称，如 "Bend"、"Twist"、"TurboSmooth" 等。
                       对于名称含空格的修改器，使用下划线代替空格，如 "UVW_Map"。
        modifier_params: 修改器参数的 JSON 字符串，键为属性名，值为属性值。
                         例如: '{"angle": 90, "direction": 45}' 用于 Bend 修改器。
                         如果为空字符串则使用修改器默认参数。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - object_name (str): 物体名称。
            - modifier_type (str): 添加的修改器类型。
            - modifier_name (str): 修改器实例名称。
            - applied_params (dict): 成功应用的参数。
            - message (str): 操作描述信息。

    示例调用 - 为物体添加弯曲修改器：
        add_modifier(object_name="Box001", modifier_type="Bend", modifier_params='{"angle": 90}')

    示例调用 - 为物体添加涡轮平滑：
        add_modifier(object_name="Box001", modifier_type="TurboSmooth", modifier_params='{"iterations": 2}')

    示例调用 - 为物体添加壳修改器（添加厚度）：
        add_modifier(object_name="Plane001", modifier_type="Shell", modifier_params='{"innerAmount": 0, "outerAmount": 5}')
    """
    import pymxs
    import json
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

        # 2. 解析修改器类型
        # 将下划线替换为空格，以支持如 "UVW_Map" -> "UVW Map" 的写法
        max_modifier_name = modifier_type.replace("_", " ")

        # 尝试获取修改器类
        modifier_class = rt.execute(f'{modifier_type}()')
        if modifier_class is None:
            # 如果下划线版本不行，尝试空格版本
            modifier_class = rt.execute(f'("{max_modifier_name}")()')

        if modifier_class is None:
            return {
                "success": False,
                "message": f"无法创建修改器 '{modifier_type}'，请确认修改器类型名称是否正确。"
            }

        # 3. 添加修改器到物体
        rt.addModifier(obj, modifier_class)

        # 4. 设置修改器参数
        applied_params = {}
        if modifier_params and modifier_params.strip():
            try:
                params = json.loads(modifier_params)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"modifier_params JSON 解析失败: {str(e)}，请检查参数格式。"
                }

            if isinstance(params, dict):
                for key, value in params.items():
                    try:
                        # 通过 MAXScript 设置修改器属性
                        # 使用 setProperty 方法
                        rt.setProperty(modifier_class, rt.Name(key), value)
                        applied_params[key] = value
                    except Exception as param_err:
                        applied_params[key] = f"设置失败: {str(param_err)}"

        # 5. 获取修改器实例的名称
        mod_name = str(modifier_class.name) if hasattr(modifier_class, 'name') else modifier_type

        return {
            "success": True,
            "object_name": object_name,
            "modifier_type": modifier_type,
            "modifier_name": mod_name,
            "applied_params": applied_params,
            "message": f"已成功为物体 '{object_name}' 添加修改器 '{mod_name}'"
                       + (f"，并设置了 {len(applied_params)} 个参数" if applied_params else "")
                       + "。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"添加修改器失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
