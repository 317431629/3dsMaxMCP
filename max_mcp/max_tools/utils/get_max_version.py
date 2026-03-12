#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/3/12
# Usage     : MCP Tool - 获取 3ds Max 版本信息
# Version   : 1.0
# Comment   : 返回 3ds Max 的版本号和相关环境信息


def get_max_version() -> dict:
    """获取当前 3ds Max 的版本信息和环境信息。

    该工具返回 3ds Max 的版本号、构建信息、Python 版本等环境信息，
    帮助了解运行环境。

    Returns:
        dict: 操作结果。
            - success (bool): 是否成功。
            - max_version (str): 3ds Max 版本号。
            - max_version_number (int): 3ds Max 版本数字。
            - python_version (str): Python 版本。
            - message (str): 描述信息。

    示例调用：
        get_max_version()
    """
    import pymxs
    import sys
    import traceback

    rt = pymxs.runtime

    try:
        # 获取 Max 版本
        max_version = str(rt.execute('(maxVersion())[1]'))
        max_version_number = int(rt.execute('(maxVersion())[1]'))

        # 获取更详细的版本信息
        try:
            max_version_str = str(rt.execute('getFileVersion "$max/3dsmax.exe"'))
        except Exception:
            max_version_str = max_version

        # Python 版本
        python_version = sys.version

        # 获取 3ds Max 产品名称
        try:
            product_name = str(rt.execute('maxFileName'))
        except Exception:
            product_name = ""

        return {
            "success": True,
            "max_version": max_version_str,
            "max_version_number": max_version_number,
            "python_version": python_version,
            "message": f"3ds Max 版本: {max_version_str}，Python 版本: {python_version}"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取版本信息失败: {str(e)}",
            "traceback": traceback.format_exc()
        }
