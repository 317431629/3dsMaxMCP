#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 保存 3ds Max 当前场景
# Version   : 1.0
# Comment   : 支持保存和另存为操作


def save_scene(file_path: str = "") -> dict:
    """保存当前 3ds Max 场景文件。

    该工具可以将当前场景保存到文件，支持覆盖保存和另存为。

    Args:
        file_path: 保存的文件路径。
                   - 如果为空字符串，则保存到当前文件（覆盖保存）。
                     若当前场景未保存过则会失败。
                   - 如果指定了路径，则另存为到该路径。
                     路径必须以 .max 结尾，如 "C:/Projects/MyScene.max"。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - file_path (str): 保存的文件完整路径。
            - message (str): 操作描述信息。

    示例调用 - 覆盖保存：
        save_scene()

    示例调用 - 另存为：
        save_scene(file_path="C:/Projects/MyScene.max")
    """
    import pymxs
    import traceback
    import os

    rt = pymxs.runtime

    try:
        if file_path and file_path.strip():
            # 另存为
            save_path = file_path.strip().replace("/", "\\")

            # 确保目录存在
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            # 确保文件扩展名为 .max
            if not save_path.lower().endswith(".max"):
                save_path += ".max"

            result = rt.saveMaxFile(save_path)
            if result:
                return {
                    "success": True,
                    "file_path": save_path,
                    "message": f"场景已成功另存为: {save_path}"
                }
            else:
                return {
                    "success": False,
                    "file_path": save_path,
                    "message": f"另存为失败，请检查路径是否有效: {save_path}"
                }
        else:
            # 覆盖保存
            current_name = str(rt.maxFileName)
            current_path = str(rt.maxFilePath)

            if not current_name or not current_name.strip():
                return {
                    "success": False,
                    "message": "当前场景尚未保存过，请指定 file_path 参数进行另存为。"
                }

            full_path = os.path.join(current_path, current_name)
            result = rt.saveMaxFile(full_path)
            if result:
                return {
                    "success": True,
                    "file_path": full_path,
                    "message": f"场景已成功保存: {full_path}"
                }
            else:
                return {
                    "success": False,
                    "file_path": full_path,
                    "message": f"保存失败: {full_path}"
                }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"保存场景失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
