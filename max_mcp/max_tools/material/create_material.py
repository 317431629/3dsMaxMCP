#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中创建材质
# Version   : 1.0
# Comment   : 支持创建 Standard/Physical 等材质类型


def create_material(material_type: str = "Standard", name: str = "", diffuse_color: str = "", params: str = "") -> dict:
    """在 3ds Max 中创建一个材质。

    该工具可以创建各种类型的材质，并设置基本属性如颜色等。
    创建的材质会被放入 3ds Max 的材质编辑器中。

    支持的材质类型（material_type 参数）：
    - Standard: 标准材质（默认），支持 Blinn/Phong/Metal 等着色器。
    - Physical: 物理材质（PBR），适合写实渲染。
    - VRayMtl: V-Ray 材质（需要安装 V-Ray 插件）。
    - Multi_Sub: 多维子材质（Multi/Sub-Object）。
    - Blend: 混合材质。
    以及其他 3ds Max 中可用的材质类名。

    Args:
        material_type: 材质类型名称，默认为 "Standard"。
        name: 材质名称。如果为空字符串则使用默认命名。
        diffuse_color: 漫反射颜色，格式为 "r,g,b"（0-255），如 "255,0,0" 为红色。
                       留空则使用默认颜色。
        params: 材质额外参数的 JSON 字符串。
                例如: '{"opacity": 50, "specularLevel": 80}' 用于 Standard 材质。
                留空则使用默认值。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - name (str): 创建的材质名称。
            - material_type (str): 材质类型。
            - slot_index (int): 材质编辑器中的槽位索引。
            - message (str): 操作描述信息。

    示例调用 - 创建红色标准材质：
        create_material(material_type="Standard", name="RedMaterial", diffuse_color="255,0,0")

    示例调用 - 创建物理材质：
        create_material(material_type="Physical", name="MetalMat", diffuse_color="180,180,180")

    示例调用 - 创建带参数的标准材质：
        create_material(material_type="Standard", name="GlassMat", diffuse_color="200,220,255", params='{"opacity": 30, "specularLevel": 90}')
    """
    import pymxs
    import json
    import traceback

    rt = pymxs.runtime

    try:
        # 1. 创建材质
        mat_type_name = material_type.replace("_", " ")

        # Physical 材质在 MAXScript 中的类名是 PhysicalMaterial
        type_alias = {
            "physical": "PhysicalMaterial",
            "multi_sub": "MultiMaterial",
        }
        actual_type = type_alias.get(material_type.lower(), material_type)

        mat = rt.execute(f'{actual_type}()')

        if mat is None:
            mat = rt.execute(f'"{mat_type_name}"()')

        if mat is None:
            return {
                "success": False,
                "message": f"无法创建类型为 '{material_type}' 的材质，请确认材质类型名称是否正确。"
            }

        # 2. 设置名称
        if name and name.strip():
            mat.name = name.strip()

        # 3. 设置漫反射颜色
        if diffuse_color and diffuse_color.strip():
            try:
                rgb = [int(c.strip()) for c in diffuse_color.split(",")]
                if len(rgb) != 3:
                    return {"success": False, "message": f"颜色参数需要 3 个值 (r,g,b)，实际得到 {len(rgb)} 个。"}

                color = rt.Color(rgb[0], rgb[1], rgb[2])

                # 不同材质类型，颜色属性名称不同
                # 依次尝试可能的颜色属性名
                color_props = []
                if material_type.lower() == "physical":
                    color_props = ["base_color", "Base_Color", "baseColor", "diffuse", "color"]
                else:
                    color_props = ["diffuse", "color", "base_color"]

                color_set = False
                for prop_name in color_props:
                    try:
                        rt.setProperty(mat, rt.Name(prop_name), color)
                        color_set = True
                        break
                    except Exception:
                        continue
            except ValueError:
                return {"success": False, "message": f"颜色参数 '{diffuse_color}' 包含无效数值。"}

        # 4. 设置额外参数
        applied_params = {}
        if params and params.strip():
            try:
                extra_params = json.loads(params)
            except json.JSONDecodeError as e:
                return {"success": False, "message": f"params JSON 解析失败: {str(e)}"}

            if isinstance(extra_params, dict):
                for key, value in extra_params.items():
                    try:
                        rt.setProperty(mat, rt.Name(key), value)
                        applied_params[key] = value
                    except Exception as param_err:
                        applied_params[key] = f"设置失败: {str(param_err)}"

        # 5. 放入材质编辑器的空槽位
        slot_index = -1
        try:
            for i in range(1, 25):  # 材质编辑器有 24 个槽位
                slot_mat = rt.meditMaterials[i]
                slot_name = str(slot_mat.name) if slot_mat else ""
                slot_class = str(rt.classOf(slot_mat)) if slot_mat else ""
                # 只覆盖真正的默认材质（格式如 "01 - Default"、"02 - Default" 等）
                is_default = (slot_mat is None
                              or "- Default" in slot_name
                              or (slot_class == "Standardmaterial" and slot_name.endswith("Default")))
                if is_default:
                    rt.meditMaterials[i] = mat
                    slot_index = i
                    break
            if slot_index == -1:
                # 所有槽位都被占用，使用下一个可用的末尾槽位
                rt.meditMaterials[24] = mat
                slot_index = 24
        except Exception:
            slot_index = -1

        mat_name = str(mat.name)

        return {
            "success": True,
            "name": mat_name,
            "material_type": material_type,
            "slot_index": slot_index,
            "applied_params": applied_params,
            "message": f"已成功创建 {material_type} 材质 '{mat_name}'"
                       + (f"，已放入材质编辑器第 {slot_index} 号槽位" if slot_index > 0 else "")
                       + "。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"创建材质失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
