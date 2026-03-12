#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3ds Max MCP Server - 通过 MCP 协议远程控制 3ds Max

一个基于 Model Context Protocol (MCP) 的 3ds Max 远程控制服务器，
支持通过 MCP 客户端对 3ds Max 进行场景管理、对象操作、材质编辑、
灯光设置、动画关键帧等操作。
"""

__version__ = "0.1.0"

from .server import main

__all__ = ["main", "__version__"]
