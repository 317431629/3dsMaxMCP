#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 从 3ds Max 导出文件
# Version   : 1.0
# Comment   : 支持 FBX/OBJ 等格式，可导出全部或选中对象


def export_file(file_path: str, selected_only: str = "false") -> dict:
    """从 3ds Max 导出场景或选中的对象到文件。

    支持的格式包括 FBX、OBJ、STL、3DS 等。
    可以导出场景中的全部对象或仅导出选中的对象。

    Args:
        file_path: 导出文件的完整路径（包含扩展名）。
                   支持的格式：.fbx, .obj, .stl, .3ds, .dae 等。
        selected_only: 是否仅导出选中的对象。
                       "true" 表示只导出选中对象。
                       "false"（默认）表示导出场景中所有对象。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - file_path (str): 导出的文件路径。
            - selected_only (bool): 是否仅导出选中对象。
            - message (str): 操作描述信息。

    示例调用 - 导出全部对象为 FBX：
        export_file(file_path="C:/Export/scene.fbx")

    示例调用 - 仅导出选中对象为 OBJ：
        export_file(file_path="C:/Export/selected.obj", selected_only="true")
    """
    import pymxs
    import traceback
    import os

    rt = pymxs.runtime

    try:
        export_path = file_path.strip().replace("/", "\\")

        # 确保输出目录存在
        export_dir = os.path.dirname(export_path)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)

        is_selected_only = selected_only.strip().lower() == "true"

        if is_selected_only:
            # 检查是否有选中对象
            sel_count = rt.selection.count
            if sel_count == 0:
                return {
                    "success": False,
                    "message": "当前没有选中任何对象，无法执行仅导出选中对象操作。"
                }
            result = rt.exportFile(export_path, rt.Name("noPrompt"), selectedOnly=True)
        else:
            result = rt.exportFile(export_path, rt.Name("noPrompt"))

        if result:
            return {
                "success": True,
                "file_path": export_path,
                "selected_only": is_selected_only,
                "message": f"已成功导出到: {export_path}"
                           + (f"（仅选中对象）" if is_selected_only else "（全部对象）")
                           + "。"
            }
        else:
            return {
                "success": False,
                "file_path": export_path,
                "message": f"导出失败: {export_path}，请检查文件格式和路径是否正确。"
            }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"导出文件失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
