#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中创建灯光
# Version   : 1.0
# Comment   : 支持创建 Omni/Spot/Directional/FreeLight 等灯光类型


def create_light(light_type: str = "Omni", name: str = "", position: str = "0,0,100", color: str = "255,255,255", intensity: str = "1.0", params: str = "") -> dict:
    """在 3ds Max 场景中创建一个灯光对象。

    支持的灯光类型（light_type 参数）：
    - Omni: 泛光灯（点光源），向四周均匀照射（默认）。
    - TargetSpot: 目标聚光灯，带目标点的锥形光源。
    - FreeSpot: 自由聚光灯，无目标点的锥形光源。
    - TargetDirect: 目标平行光，平行方向光照。
    - FreeLight: 自由灯光。
    - Skylight: 天光，模拟天空环境光照。
    - mr_Sky_Portal: Mental Ray 天空门户（需要 MR 插件）。
    以及 V-Ray、Arnold 等插件的灯光类型（如 VRayLight、aiAreaLight）。

    Args:
        light_type: 灯光类型名称。默认为 "Omni"。
        name: 灯光名称。如果为空则使用默认命名。
        position: 灯光位置，格式为 "x,y,z"。默认为 "0,0,100"。
        color: 灯光颜色，格式为 "r,g,b" (0-255)。默认为 "255,255,255"（白色）。
        intensity: 灯光强度/倍增器，默认 "1.0"。
        params: 灯光额外参数的 JSON 字符串。
                例如: '{"castShadows": true, "hotspot": 30, "falloff": 60}' 用于聚光灯。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - name (str): 创建的灯光名称。
            - light_type (str): 灯光类型。
            - position (list): 位置 [x, y, z]。
            - message (str): 操作描述信息。

    示例调用 - 创建泛光灯：
        create_light(light_type="Omni", name="MainLight", position="0,0,200", color="255,245,230", intensity="1.5")

    示例调用 - 创建聚光灯：
        create_light(light_type="FreeSpot", name="SpotLight01", position="100,0,150", params='{"hotspot": 30, "falloff": 60}')

    示例调用 - 创建天光：
        create_light(light_type="Skylight", intensity="0.8")
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
                return {"success": False, "message": f"位置参数需要 3 个值 (x,y,z)，实际得到 {len(pos_parts)} 个。"}
        except ValueError:
            return {"success": False, "message": f"位置参数 '{position}' 包含无效数值。"}

        # 2. 解析颜色
        try:
            rgb = [int(c.strip()) for c in color.split(",")]
            if len(rgb) != 3:
                return {"success": False, "message": f"颜色参数需要 3 个值 (r,g,b)，实际得到 {len(rgb)} 个。"}
        except ValueError:
            return {"success": False, "message": f"颜色参数 '{color}' 包含无效数值。"}

        # 3. 解析强度
        try:
            multiplier = float(intensity.strip())
        except ValueError:
            return {"success": False, "message": f"强度参数 '{intensity}' 不是有效数值。"}

        # 4. 灯光类型名称映射（常见简称 -> MAXScript 类名）
        light_type_alias = {
            "omni": "OmniLight",
            "omnilight": "OmniLight",
            "targetspot": "TargetSpot",
            "freespot": "FreeSpot",
            "targetdirect": "TargetDirectionalLight",
            "freedirect": "FreeDirectionalLight",
            "directionallight": "TargetDirectionalLight",
            "skylight": "Skylight",
        }
        actual_type = light_type_alias.get(light_type.lower(), light_type)

        # 5. 构建创建参数
        param_parts = [
            f'pos:(Point3 {pos_parts[0]} {pos_parts[1]} {pos_parts[2]})',
            f'color:(color {rgb[0]} {rgb[1]} {rgb[2]})',
            f'multiplier:{multiplier}'
        ]

        if name and name.strip():
            param_parts.append(f'name:"{name.strip()}"')

        # 6. 创建灯光 - 先使用映射后的类名，再尝试原始类名
        maxscript_cmd = f'{actual_type} {" ".join(param_parts)}'
        light_obj = rt.execute(maxscript_cmd)

        if light_obj is None and actual_type != light_type:
            # 用原始类名重试
            maxscript_cmd = f'{light_type} {" ".join(param_parts)}'
            light_obj = rt.execute(maxscript_cmd)

        if light_obj is None:
            return {
                "success": False,
                "message": f"无法创建类型为 '{light_type}' (尝试了 '{actual_type}') 的灯光，请确认灯光类型名称是否正确。"
            }

        # 6. 设置额外参数
        applied_params = {}
        if params and params.strip():
            try:
                extra_params = json.loads(params)
            except json.JSONDecodeError as e:
                return {"success": False, "message": f"params JSON 解析失败: {str(e)}"}

            if isinstance(extra_params, dict):
                for key, value in extra_params.items():
                    try:
                        rt.setProperty(light_obj, rt.Name(key), value)
                        applied_params[key] = value
                    except Exception as param_err:
                        applied_params[key] = f"设置失败: {str(param_err)}"

        # 7. 获取结果
        light_name = str(light_obj.name)
        light_pos = light_obj.pos
        actual_pos = [float(light_pos.x), float(light_pos.y), float(light_pos.z)]

        return {
            "success": True,
            "name": light_name,
            "light_type": light_type,
            "position": actual_pos,
            "color": rgb,
            "intensity": multiplier,
            "applied_params": applied_params,
            "message": f"已成功创建 {light_type} 灯光 '{light_name}'，位置: {actual_pos}，"
                       + f"颜色: RGB({rgb[0]},{rgb[1]},{rgb[2]})，强度: {multiplier}。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"创建灯光失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
