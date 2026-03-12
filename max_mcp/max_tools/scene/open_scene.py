#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中打开场景文件
# Version   : 1.0
# Comment   : 支持打开 .max 场景文件


def open_scene(file_path: str, force: str = "false") -> dict:
    """在 3ds Max 中打开一个场景文件。

    该工具将加载指定的 .max 场景文件。

    Args:
        file_path: 要打开的场景文件完整路径，必须是 .max 文件。
                   例如: "C:/Projects/MyScene.max"
        force: 是否强制打开（不提示保存当前场景）。
               "true" 表示强制打开（不保存当前更改），
               "false"（默认）表示如果当前场景有更改会先尝试保存。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - file_path (str): 打开的文件路径。
            - message (str): 操作描述信息。

    示例调用：
        open_scene(file_path="C:/Projects/MyScene.max")

    示例调用 - 强制打开（不保存当前场景）：
        open_scene(file_path="C:/Projects/MyScene.max", force="true")
    """
    import pymxs
    import traceback
    import os

    rt = pymxs.runtime

    try:
        open_path = file_path.strip().replace("/", "\\")

        # 检查文件是否存在
        if not os.path.exists(open_path):
            return {
                "success": False,
                "message": f"文件不存在: {open_path}"
            }

        # 检查文件扩展名
        if not open_path.lower().endswith(".max"):
            return {
                "success": False,
                "message": f"不支持的文件格式，请指定 .max 文件。当前文件: {open_path}"
            }

        is_force = force.lower().strip() == "true"

        if is_force:
            # 强制打开，不提示保存
            rt.execute('setSaveRequired false')

        # 使用 loadMaxFile 打开文件
        # useFileUnits:true 使用文件的单位设置，quiet:true 不弹出对话框
        result = rt.loadMaxFile(open_path, rt.Name("useFileUnits"), True, rt.Name("quiet"), True)

        if result:
            return {
                "success": True,
                "file_path": open_path,
                "message": f"已成功打开场景文件: {open_path}"
            }
        else:
            return {
                "success": False,
                "file_path": open_path,
                "message": f"打开场景文件失败: {open_path}"
            }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"打开场景失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
