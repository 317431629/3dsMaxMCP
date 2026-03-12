#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 设置 3ds Max 的时间/帧范围和当前帧
# Version   : 1.0
# Comment   : 支持设置动画范围、当前帧和帧率


def set_time_range(start_frame: str = "", end_frame: str = "", current_frame: str = "", fps: str = "") -> dict:
    """设置 3ds Max 的时间/帧范围参数。

    该工具可以设置动画的帧范围、当前帧位置和帧率。
    所有参数都是可选的，只设置你需要修改的参数。

    Args:
        start_frame: 动画起始帧。留空不修改。
        end_frame: 动画结束帧。留空不修改。
        current_frame: 当前帧（时间滑块位置）。留空不修改。
        fps: 帧率。常见值: "24"(电影)、"25"(PAL)、"30"(NTSC)。留空不修改。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - time_range (dict): 设置后的时间范围信息。
            - message (str): 操作描述信息。

    示例调用 - 设置帧范围：
        set_time_range(start_frame="0", end_frame="100")

    示例调用 - 设置当前帧：
        set_time_range(current_frame="50")

    示例调用 - 设置帧率和范围：
        set_time_range(start_frame="0", end_frame="240", fps="24")
    """
    import pymxs
    import traceback

    rt = pymxs.runtime

    try:
        changes = []

        # 设置帧率
        if fps and fps.strip():
            try:
                new_fps = float(fps.strip())
                rt.frameRate = new_fps
                changes.append(f"帧率: {new_fps}")
            except ValueError:
                return {"success": False, "message": f"帧率参数 '{fps}' 不是有效数值。"}

        # 设置帧范围
        if (start_frame and start_frame.strip()) or (end_frame and end_frame.strip()):
            try:
                current_range = rt.animationRange
                start = int(start_frame.strip()) if start_frame and start_frame.strip() else int(current_range.start / rt.ticksPerFrame)
                end = int(end_frame.strip()) if end_frame and end_frame.strip() else int(current_range.end / rt.ticksPerFrame)

                # 使用 MAXScript 设置动画范围
                rt.animationRange = rt.Interval(start * rt.ticksPerFrame, end * rt.ticksPerFrame)
                changes.append(f"帧范围: {start}-{end}")
            except ValueError:
                return {"success": False, "message": "帧范围参数包含无效数值。"}

        # 设置当前帧
        if current_frame and current_frame.strip():
            try:
                frame = int(current_frame.strip())
                rt.sliderTime = frame * rt.ticksPerFrame
                changes.append(f"当前帧: {frame}")
            except ValueError:
                return {"success": False, "message": f"当前帧参数 '{current_frame}' 不是有效数值。"}

        # 获取当前状态
        anim_range = rt.animationRange
        result_start = int(anim_range.start / rt.ticksPerFrame)
        result_end = int(anim_range.end / rt.ticksPerFrame)
        result_current = int(rt.currentTime / rt.ticksPerFrame)
        result_fps = float(rt.frameRate)

        time_range = {
            "start": result_start,
            "end": result_end,
            "current": result_current,
            "fps": result_fps
        }

        if not changes:
            return {
                "success": True,
                "time_range": time_range,
                "message": f"未指定任何修改参数。当前状态: 帧范围 {result_start}-{result_end}，"
                           + f"当前帧 {result_current}，帧率 {result_fps} FPS。"
            }

        return {
            "success": True,
            "time_range": time_range,
            "message": f"已成功设置: {', '.join(changes)}。"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"设置时间范围失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
