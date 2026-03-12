#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date      2026/1/4 11:02
# Usage     : 3ds Max Socket 通信层
# Version   : 2.0
# Comment   : 适配 3ds Max 的 Socket 通信协议，直接发送 Python 代码执行


# Import built-in modules
import socket
import json
import struct
from enum import Enum

# Import third-party modules

# Import local modules
from max_mcp.log import LogManager, log_file

logger = LogManager.get_logger('3dsMaxMCPServer', __file__, log_file)

# ============================================================
# 通信协议说明
# ============================================================
# 客户端（MCP Server）与 3ds Max 内的 Socket Server 通过 TCP 通信。
#
# 发送协议:
#   [4字节 大端序 uint32: 消息体长度] + [UTF-8编码的Python脚本]
#
# 接收协议:
#   [4字节 大端序 uint32: 消息体长度] + [UTF-8编码的JSON结果字符串]
#
# 3ds Max 端需要运行一个配套的 Socket Server 脚本来接收并执行命令。
# 参见 max_server_listener.py
# ============================================================

HEADER_SIZE = 4  # 消息头长度（4字节，存放消息体长度）
DEFAULT_RECV_BUFSIZE = 4096  # 默认接收缓冲区大小
SOCKET_TIMEOUT = 60  # Socket 超时时间（秒）


def _pack_message(data: str) -> bytes:
    """将字符串消息打包为带长度头的二进制数据。

    协议格式: [4字节大端序长度头] + [UTF-8编码的消息体]

    Args:
        data: 要发送的字符串消息

    Returns:
        打包后的二进制数据
    """
    encoded = data.encode('utf-8')
    header = struct.pack('>I', len(encoded))
    return header + encoded


def _recv_all(sock: socket.socket) -> str:
    """从 Socket 接收完整的带长度头的消息。

    先读取4字节头获取消息体长度，再读取完整消息体。

    Args:
        sock: 已连接的 Socket 对象

    Returns:
        解码后的字符串消息

    Raises:
        ConnectionError: 连接被关闭或数据不完整
    """
    # 读取消息头（4字节）
    header_data = b''
    while len(header_data) < HEADER_SIZE:
        chunk = sock.recv(HEADER_SIZE - len(header_data))
        if not chunk:
            raise ConnectionError("3ds Max 端连接已关闭，未能读取消息头。")
        header_data += chunk

    # 解析消息体长度
    msg_length = struct.unpack('>I', header_data)[0]
    if msg_length == 0:
        return ''

    # 读取完整消息体
    body_data = b''
    while len(body_data) < msg_length:
        remaining = msg_length - len(body_data)
        chunk = sock.recv(min(remaining, DEFAULT_RECV_BUFSIZE))
        if not chunk:
            raise ConnectionError(
                f"3ds Max 端连接已关闭，消息体不完整。"
                f"期望 {msg_length} 字节，实际收到 {len(body_data)} 字节。"
            )
        body_data += chunk

    return body_data.decode('utf-8')


def _update_script_to_capture_stdout(python_script: str) -> str:
    """将脚本包裹在 stdout 捕获上下文中，便于收集打印输出。"""
    spaced_python_script = '    ' + python_script.replace('\n', '\n    ')
    return f"""
import io
import contextlib
_mcp_io_buf = io.StringIO()
with contextlib.redirect_stdout(_mcp_io_buf):
{spaced_python_script}
_mcp_max_results = _mcp_io_buf.getvalue()
"""


class ScriptReturn(Enum):
    """脚本返回值类型枚举"""
    STDOUT = "stdout"   # 捕获 stdout 输出作为结果
    JSON = "json"       # 将结果解析为 JSON
    NONE = "none"       # 不关心返回值


class MaxConnection(object):
    """3ds Max Socket 通信连接器。

    通过 TCP Socket 连接到 3ds Max 内运行的 Python Socket Server，
    发送 Python 脚本并接收执行结果。

    3ds Max 端需要预先运行 max_server_listener.py 监听脚本。

    Attributes:
        _host: 连接地址，默认 127.0.0.1
        _port: 连接端口，默认 50007
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 50007):
        super(MaxConnection, self).__init__()
        self._host = host
        self._port = port

    def _send_python_command(self, python_script: str) -> str:
        """通过 Socket 将 Python 脚本发送给 3ds Max，并读取返回结果。

        使用带长度头的协议确保数据完整传输：
        1. 建立 TCP 连接
        2. 发送 [长度头 + Python脚本]
        3. 接收 [长度头 + 执行结果]
        4. 关闭连接

        Args:
            python_script: 要在 3ds Max 中执行的 Python 脚本

        Returns:
            3ds Max 返回的结果字符串

        Raises:
            ConnectionRefusedError: 无法连接到 3ds Max（可能未启动监听）
            ConnectionError: 通信过程中连接断开
            socket.timeout: 等待响应超时
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(SOCKET_TIMEOUT)

        try:
            client.connect((self._host, self._port))
            logger.debug(f"已连接到 3ds Max ({self._host}:{self._port})")

            # 发送 Python 脚本（带长度头）
            message = _pack_message(python_script)
            client.sendall(message)
            logger.debug(f"已发送脚本，长度: {len(python_script)} 字符")

            # 接收执行结果（带长度头）
            result = _recv_all(client)
            logger.debug(f"收到结果，长度: {len(result)} 字符")

            return result

        except ConnectionRefusedError:
            error_msg = (
                f"无法连接到 3ds Max ({self._host}:{self._port})。"
                f"请确保 3ds Max 已启动，且 max_server_listener.py 监听脚本正在运行。"
            )
            logger.error(error_msg)
            raise ConnectionRefusedError(error_msg)

        except socket.timeout:
            error_msg = f"等待 3ds Max 响应超时（{SOCKET_TIMEOUT}秒）。脚本可能执行时间过长。"
            logger.error(error_msg)
            raise

        except Exception as e:
            logger.error(f"与 3ds Max 通信出错: {e}")
            raise

        finally:
            client.close()

    def run_python_script(self, python_script: str, *, returns: ScriptReturn = ScriptReturn.JSON):
        """执行 Python 脚本并按指定返回类型处理结果。

        根据 returns 参数决定如何处理脚本和返回值：
        - JSON: 在脚本中初始化 _mcp_max_results 变量，将结果解析为 JSON
        - STDOUT: 包裹 stdout 捕获逻辑，返回打印输出
        - NONE: 直接执行，不处理返回值

        Args:
            python_script: 要执行的 Python 脚本
            returns: 返回值类型，默认为 JSON

        Returns:
            根据 returns 类型返回:
            - JSON: 解析后的 Python 对象（dict/list等）
            - STDOUT: stdout 输出字符串
            - NONE: 原始结果字符串
        """
        if returns == ScriptReturn.STDOUT:
            python_script = _update_script_to_capture_stdout(python_script)
        elif returns == ScriptReturn.JSON:
            python_script = "_mcp_max_results = None\n" + python_script

        result = self._send_python_command(python_script)
        logger.debug(f"send_python_command result: {result[:500] if result else result}")

        # 清理结果字符串中的多余字符
        if result:
            result = result.strip()

        # 如果直接执行没有返回结果，尝试读取 _mcp_max_results 变量
        if returns != ScriptReturn.NONE and (not result or result in ('', 'None', '\n')):
            logger.debug("首次结果为空，尝试读取 _mcp_max_results 变量")
            result = self._send_python_command("_mcp_max_results")
            if result:
                result = result.strip()

        # 按返回类型解析结果
        if returns != ScriptReturn.NONE and result:
            try:
                result = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                # 无法解析为 JSON，按原样返回
                logger.debug(f"结果无法解析为 JSON，按原样返回: {result[:200] if result else result}")

        return result
