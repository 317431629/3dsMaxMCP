#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 获取 3ds Max 当前场景的综合信息
# Version   : 1.0
# Comment   : 返回场景文件名、对象统计、帧范围、单位设置等


def get_scene_info() -> dict:
    """获取当前 3ds Max 场景的综合信息。

    该工具返回当前场景的全面信息，包括文件路径、对象统计、时间范围、
    单位设置等，帮助 AI 了解场景的整体状态。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - file_path (str): 当前场景文件的完整路径（未保存时为空）。
            - file_name (str): 场景文件名。
            - is_saved (bool): 场景是否已保存。
            - object_counts (dict): 各类型对象数量统计。
                - total (int): 总对象数。
                - geometry (int): 几何体数量。
                - lights (int): 灯光数量。
                - cameras (int): 相机数量。
                - helpers (int): 辅助对象数量。
                - shapes (int): 样条线数量。
            - time_range (dict): 时间/帧范围。
                - start (int): 起始帧。
                - end (int): 结束帧。
                - current (int): 当前帧。
                - fps (float): 帧率。
            - units (dict): 单位设置。
                - system_type (str): 系统单位类型。
                - system_scale (float): 系统单位缩放。
                - display_type (str): 显示单位类型。
            - message (str): 描述信息。

    示例调用：
        get_scene_info()
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        # 1. 文件信息
        file_path = str(rt.maxFilePath) + str(rt.maxFileName) if rt.maxFileName else ""
        file_name = str(rt.maxFileName) if rt.maxFileName else ""
        is_saved = bool(file_name and file_name.strip())

        # 2. 对象统计
        all_objects = list(rt.objects)
        total = len(all_objects)

        geometry_count = 0
        light_count = 0
        camera_count = 0
        helper_count = 0
        shape_count = 0
        other_count = 0

        for obj in all_objects:
            try:
                if rt.isKindOf(obj, rt.GeometryClass):
                    geometry_count += 1
                elif rt.isKindOf(obj, rt.Light):
                    light_count += 1
                elif rt.isKindOf(obj, rt.Camera):
                    camera_count += 1
                elif rt.isKindOf(obj, rt.Helper):
                    helper_count += 1
                elif rt.isKindOf(obj, rt.Shape):
                    shape_count += 1
                else:
                    other_count += 1
            except Exception:
                other_count += 1

        object_counts = {
            "total": total,
            "geometry": geometry_count,
            "lights": light_count,
            "cameras": camera_count,
            "helpers": helper_count,
            "shapes": shape_count,
            "other": other_count
        }

        # 3. 时间/帧范围
        try:
            anim_range = rt.animationRange
            start_frame = int(anim_range.start / rt.ticksPerFrame)
            end_frame = int(anim_range.end / rt.ticksPerFrame)
        except Exception:
            start_frame = 0
            end_frame = 100

        try:
            current_frame = int(rt.currentTime / rt.ticksPerFrame)
        except Exception:
            current_frame = 0

        try:
            fps = float(rt.frameRate)
        except Exception:
            fps = 30.0

        time_range = {
            "start": start_frame,
            "end": end_frame,
            "current": current_frame,
            "fps": fps
        }

        # 4. 单位设置
        try:
            system_type = str(rt.units.SystemType)
            system_scale = float(rt.units.SystemScale)
            display_type = str(rt.units.DisplayType)
        except Exception:
            system_type = "unknown"
            system_scale = 1.0
            display_type = "unknown"

        units = {
            "system_type": system_type,
            "system_scale": system_scale,
            "display_type": display_type
        }

        return {
            "success": True,
            "file_path": file_path,
            "file_name": file_name,
            "is_saved": is_saved,
            "object_counts": object_counts,
            "time_range": time_range,
            "units": units,
            "message": f"场景: {file_name if file_name else '未保存'}，"
                       + f"共 {total} 个对象（几何体 {geometry_count}, 灯光 {light_count}, "
                       + f"相机 {camera_count}, 辅助 {helper_count}, 样条线 {shape_count}），"
                       + f"帧范围: {start_frame}-{end_frame}，当前帧: {current_frame}，帧率: {fps} FPS。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取场景信息失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
