#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 将材质赋予 3ds Max 中的物体
# Version   : 1.0
# Comment   : 支持按材质名称或材质编辑器槽位赋予


def assign_material(object_name: str, material_name: str = "", slot_index: str = "0") -> dict:
    """将材质赋予 3ds Max 场景中的指定物体。

    该工具可以将已存在的材质赋予物体，支持通过材质名称或材质编辑器槽位索引来指定材质。

    Args:
        object_name: 目标物体名称。支持通配符 "*"，如 "Box*" 会赋予所有以 Box 开头的物体。
                     也支持用英文逗号分隔多个名称，如 "Box001,Sphere001"。
        material_name: 材质名称。在场景的所有材质中查找匹配的材质。
                       与 slot_index 二选一，优先使用 material_name。
        slot_index: 材质编辑器的槽位索引（1-24）。当 material_name 为空时使用此参数。
                    默认为 "0"（不使用槽位）。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - assigned (list): 成功赋予材质的物体列表。
            - material_name (str): 使用的材质名称。
            - message (str): 操作描述信息。

    示例调用 - 按材质名称赋予：
        assign_material(object_name="Box001", material_name="RedMaterial")

    示例调用 - 按槽位赋予：
        assign_material(object_name="Box001", slot_index="1")

    示例调用 - 批量赋予：
        assign_material(object_name="Box*", material_name="WoodMaterial")
    """
    import pymxs
    import traceback
    import fnmatch

    rt = pymxs.runtime

    try:
        # 1. 获取材质
        mat = None
        mat_name = ""

        if material_name and material_name.strip():
            # 按名称查找材质
            target_name = material_name.strip()

            # 先在材质编辑器中查找
            for i in range(1, 25):
                try:
                    slot_mat = rt.meditMaterials[i]
                    if slot_mat and str(slot_mat.name) == target_name:
                        mat = slot_mat
                        mat_name = target_name
                        break
                except Exception:
                    continue

            # 如果材质编辑器中没找到，遍历场景中的材质
            if mat is None:
                for obj in rt.objects:
                    try:
                        if obj.material and str(obj.material.name) == target_name:
                            mat = obj.material
                            mat_name = target_name
                            break
                    except Exception:
                        continue

            if mat is None:
                return {
                    "success": False,
                    "message": f"未找到名为 '{target_name}' 的材质，请先创建材质或确认名称是否正确。"
                }

        elif slot_index and slot_index.strip() and slot_index.strip() != "0":
            # 按槽位获取材质
            try:
                idx = int(slot_index.strip())
                if idx < 1 or idx > 24:
                    return {"success": False, "message": f"槽位索引范围为 1-24，当前值: {idx}"}
                mat = rt.meditMaterials[idx]
                if mat is None:
                    return {"success": False, "message": f"材质编辑器第 {idx} 号槽位为空。"}
                mat_name = str(mat.name)
            except ValueError:
                return {"success": False, "message": f"slot_index 参数 '{slot_index}' 不是有效数字。"}
        else:
            return {
                "success": False,
                "message": "请指定 material_name 或 slot_index 参数。"
            }

        # 2. 查找目标物体并赋予材质
        assigned = []
        not_found = []

        names = [n.strip() for n in object_name.split(",")]

        for name_pattern in names:
            if not name_pattern:
                continue

            has_wildcard = "*" in name_pattern or "?" in name_pattern

            if has_wildcard:
                for obj in list(rt.objects):
                    if fnmatch.fnmatch(str(obj.name), name_pattern):
                        try:
                            obj.material = mat
                            assigned.append(str(obj.name))
                        except Exception as e:
                            not_found.append(f"{str(obj.name)} (赋予失败: {str(e)})")
            else:
                obj = rt.getNodeByName(name_pattern)
                if obj is None:
                    not_found.append(name_pattern)
                else:
                    try:
                        obj.material = mat
                        assigned.append(str(obj.name))
                    except Exception as e:
                        not_found.append(f"{name_pattern} (赋予失败: {str(e)})")

        # 3. 构建结果
        msg_parts = []
        if assigned:
            msg_parts.append(f"已将材质 '{mat_name}' 赋予 {len(assigned)} 个物体: {', '.join(assigned)}")
        if not_found:
            msg_parts.append(f"未找到或赋予失败: {', '.join(not_found)}")

        return {
            "success": len(assigned) > 0,
            "assigned": assigned,
            "material_name": mat_name,
            "not_found": not_found,
            "message": "。".join(msg_parts) + "。" if msg_parts else "未匹配到任何物体。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"赋予材质失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
