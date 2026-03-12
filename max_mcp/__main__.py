#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3ds Max MCP Server 命令行入口。

支持通过以下方式运行：
    python -m max_mcp
    uvx max-mcp
"""

from .server import main

if __name__ == "__main__":
    main()
