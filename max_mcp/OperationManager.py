#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/2/4 11:02
# Usage     :
# Version   :
# Comment   :   管理工具脚本、资源与 MCP Tool 的注册信息。


# Import built-in modules
import os
import inspect
import importlib.util
from typing import Optional, List, get_origin, Any
# Import third-party modules
from mcp.types import Tool
from mcp.server.fastmcp.utilities.func_metadata import func_metadata
from mcp.server.fastmcp.server import Context
# Import local modules
from max_mcp.log import LogManager, log_file

logger = LogManager.get_logger('3dsMaxMCPServer',  __file__, log_file)

__all__ = ["OperationsManager"]


def _get_function_tool(max_tool_name: str, filename: str) -> Tool:
    """从脚本中解析函数并构建 MCP Tool 描述对象。

    Args:
        max_tool_name:
        filename:

    Returns:

    """
    try:
        spec = importlib.util.spec_from_file_location(max_tool_name, filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fn = getattr(module, max_tool_name)
    except Exception as e:
        logger.error(f"Unable to pre-load {max_tool_name} because: {e}")
        return None

    func_doc = fn.__doc__ or ""
    sig = inspect.signature(fn)
    context_kwarg = None
    for param_name, param in sig.parameters.items():
        if get_origin(param.annotation) is not None:
            continue
        if param.annotation is Any:
            continue
        if not isinstance(param.annotation, type):
            continue
        if issubclass(param.annotation, Context):
            context_kwarg = param_name
            break

    func_arg_metadata = func_metadata(fn, skip_names=[context_kwarg] if context_kwarg is not None else [], )
    parameters = func_arg_metadata.arg_model.model_json_schema()

    tool = Tool(name=max_tool_name, description=func_doc, inputSchema=parameters)
    return tool


class OperationsManager(object):
    def __init__(self, script_directory: str):
        """初始化工具与路径映射表。

        Args:
            script_directory: 需要扫描的脚本目录。
        """
        self._script_directory = script_directory
        self._paths = {}
        self._tools = {}

    def has_tool(self, name: str) -> bool:
        """判断指定工具是否已加载。"""
        return name in self._tools

    def get_tool(self, name: str) -> Optional[Tool]:
        """获取指定名称的 MCP Tool 实例。"""
        if name in self._tools:
            return self._tools[name]
        return None

    def get_file_path(self, name: str) -> Optional[str]:
        """获取工具对应的脚本文件路径。"""
        if name in self._paths:
            return self._paths[name]
        return None

    def get_tools(self) -> List[Tool]:
        """返回已加载的所有 MCP Tool 列表。"""
        return list(self._tools.values())

    def find_tools(self):
        """扫描 目录，加载所有可用的工具脚本。"""
        for root, dirs, files in os.walk(os.path.join(self._script_directory)):
            for file in files:
                if not file.endswith(".py"):
                    continue
                name, _ = os.path.splitext(file)
                path = os.path.join(root, file)
                tool = _get_function_tool(name, path)
                if not tool:
                    continue
                self._paths[name] = path
                self._tools[name] = tool
