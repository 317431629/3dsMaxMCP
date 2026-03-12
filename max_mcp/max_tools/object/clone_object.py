#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 克隆 3ds Max 场景中的物体
# Version   : 1.0
# Comment   : 支持 Copy/Instance/Reference 三种克隆模式


def clone_object(object_name: str, clone_type: str = "copy", new_name: str = "", offset: str = "0,0,0") -> dict:
    """克隆 3ds Max 场景中的指定物体。

    支持三种克隆模式：
    - Copy: 完全独立的副本（默认）。
    - Instance: 实例，与原对象共享修改器和参数。
    - Reference: 引用，可以在原对象基础上添加新修改器。

    Args:
        object_name: 要克隆的源物体名称。
        clone_type: 克隆类型，可选 "copy"、"instance"、"reference"。默认为 "copy"。
        new_name: 克隆体的名称。如果为空，则使用 3ds Max 默认命名。
        offset: 克隆体相对于原物体的偏移量，格式为 "x,y,z"。
                默认为 "0,0,0"（与原物体重叠）。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - source_name (str): 源物体名称。
            - clone_name (str): 克隆体名称。
            - clone_type (str): 克隆类型。
            - position (list): 克隆体位置 [x, y, z]。
            - message (str): 操作描述信息。

    示例调用 - 复制一个 Box：
        clone_object(object_name="Box001")

    示例调用 - 实例化克隆并偏移：
        clone_object(object_name="Box001", clone_type="instance", offset="50,0,0")

    示例调用 - 带名称的引用克隆：
        clone_object(object_name="Box001", clone_type="reference", new_name="Box001_Ref", offset="100,0,0")
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        # 1. 查找源物体
        obj = rt.getNodeByName(object_name)
        if obj is None:
            return {
                "success": False,
                "message": f"未找到名为 '{object_name}' 的物体，请确认物体名称是否正确。"
            }

        # 2. 解析偏移量
        try:
            off_parts = [float(p.strip()) for p in offset.split(",")]
            if len(off_parts) != 3:
                return {"success": False, "message": f"偏移参数需要 3 个值 (x,y,z)，实际得到 {len(off_parts)} 个。"}
        except ValueError:
            return {"success": False, "message": f"偏移参数 '{offset}' 包含无效数值。"}

        # 3. 确定克隆类型
        clone_type_lower = clone_type.strip().lower()
        type_map = {
            "copy": "#copy",
            "instance": "#instance",
            "reference": "#reference"
        }
        if clone_type_lower not in type_map:
            return {
                "success": False,
                "message": f"不支持的克隆类型 '{clone_type}'，可选值: copy, instance, reference。"
            }

        # 4. 执行克隆（通过 MAXScript）
        max_clone_type = type_map[clone_type_lower]

        # 使用 maxOps.cloneNodes 方法
        maxscript = f"""
(
    local srcObj = getNodeByName "{object_name}"
    local newNodes = #()
    maxOps.cloneNodes srcObj cloneType:{max_clone_type} newNodes:&newNodes
    newNodes[1]
)
"""
        cloned_obj = rt.execute(maxscript)

        if cloned_obj is None:
            return {
                "success": False,
                "message": f"克隆物体 '{object_name}' 失败，请检查物体是否可克隆。"
            }

        # 5. 设置名称
        if new_name and new_name.strip():
            cloned_obj.name = new_name.strip()

        # 6. 设置位置（原物体位置 + 偏移）
        src_pos = obj.pos
        cloned_obj.pos = rt.Point3(
            src_pos.x + off_parts[0],
            src_pos.y + off_parts[1],
            src_pos.z + off_parts[2]
        )

        # 7. 获取结果信息
        clone_name = str(cloned_obj.name)
        clone_pos = cloned_obj.pos
        position = [float(clone_pos.x), float(clone_pos.y), float(clone_pos.z)]

        return {
            "success": True,
            "source_name": object_name,
            "clone_name": clone_name,
            "clone_type": clone_type_lower,
            "position": position,
            "message": f"已成功将物体 '{object_name}' 以 {clone_type_lower} 模式克隆为 '{clone_name}'，"
                       + f"位置: [{position[0]}, {position[1]}, {position[2]}]。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"克隆物体失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
