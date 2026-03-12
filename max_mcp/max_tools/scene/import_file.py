#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 在 3ds Max 中导入外部文件
# Version   : 1.0
# Comment   : 支持 FBX/OBJ/Alembic 等格式


def import_file(file_path: str) -> dict:
    """在 3ds Max 中导入外部文件。

    支持的格式包括 FBX、OBJ、Alembic(ABC)、STL、3DS 等 3ds Max 能识别的文件格式。
    导入的对象将被添加到当前场景中。

    Args:
        file_path: 要导入的文件完整路径。
                   支持的常见格式：.fbx, .obj, .abc, .stl, .3ds, .dae 等。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - file_path (str): 导入的文件路径。
            - message (str): 操作描述信息。

    示例调用：
        import_file(file_path="C:/Models/character.fbx")

    示例调用：
        import_file(file_path="C:/Models/terrain.obj")
    """
    import pymxs
    import traceback
    import os

    rt = pymxs.runtime

    try:
        import_path = file_path.strip().replace("/", "\\")

        # 检查文件是否存在
        if not os.path.exists(import_path):
            return {
                "success": False,
                "message": f"文件不存在: {import_path}"
            }

        # 记录导入前的对象数
        before_count = len(list(rt.objects))

        # 使用 importFile 导入，quiet 模式不弹出对话框
        result = rt.importFile(import_path, rt.Name("noPrompt"), using=rt.execute('undefined'))

        # 记录导入后的对象数
        after_count = len(list(rt.objects))
        new_count = after_count - before_count

        if result or new_count > 0:
            return {
                "success": True,
                "file_path": import_path,
                "new_objects_count": new_count,
                "message": f"已成功导入文件: {import_path}，新增了 {new_count} 个对象。"
            }
        else:
            return {
                "success": False,
                "file_path": import_path,
                "message": f"导入文件失败或未导入任何对象: {import_path}"
            }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"导入文件失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
