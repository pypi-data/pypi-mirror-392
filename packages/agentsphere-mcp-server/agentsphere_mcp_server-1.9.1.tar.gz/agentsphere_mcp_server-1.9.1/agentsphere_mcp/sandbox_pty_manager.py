import os
import time
import socket
import threading
import select
import platform
import subprocess
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP, Context
from agentsphere_base import AsyncSandbox, Sandbox
import logging
import pathlib
from platformdirs import user_desktop_dir, user_documents_dir, user_downloads_dir
import asyncio
from .tlv_protocol import TLVProtocol, TLVSign, TLVMessage, TLVServer

# 导入 agentsphere 相关模块（用于 sandbox_is_running）
from agentsphere_base.api import AsyncApiClient, handle_api_exception
from agentsphere_base.api.client.api.sandboxes import get_sandboxes_sandbox_id
from agentsphere_base import ConnectionConfig
from agentsphere_base.sandbox.sandbox_api import SandboxApiBase
from .single_sandbox_manager import SingleSandboxManager
from .logger import logger

class TCPClientConnection:
    def __init__(self, client_socket: socket.socket, client_address: str, client_id: str):
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_id = client_id
        self.sandbox_id = client_id
        self.is_connected = True
        self.tlv_server = TLVServer(client_socket)
        self.output_buffer = []
        self.registered_at = None

    def send_tlv_message(self, message: TLVMessage):
        """发送TLV消息到客户端"""
        try:
            if self.is_connected:
                self.tlv_server.send_tlv_message(message)
                logger.debug(f"send_tlv_message - 已向客户端 {self.client_id} 发送TLV消息: {message}")
        except Exception as e:
            logger.error(f"向客户端 {self.client_id} 发送TLV消息失败: {str(e)}")
            self.is_connected = False

    def get_recent_output(self) -> List[str]:
        response = TLVMessage(
            sign=TLVSign.GET_OUTPUT,
            content={
                "client_id": self.client_id
            }
        )
        self.send_tlv_message(response)

    def clear_output(self):
        """清空输出历史"""
        self.output_buffer.clear()

    def close(self):
        """关闭连接"""

        self.is_connected = False
        self.tlv_server.close()
        logger.info(f"客户端 {self.client_id} 连接已关闭")

# Sandbox PTY Manager类
class SandboxPtyManager:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 0
        self.server_socket = None
        self.client_connections: Dict[str, TCPClientConnection] = {}
        self.is_running = False
        self.server_thread = None


    def _handle_tlv_message(self, message: TLVMessage, client: TCPClientConnection):
        """处理TLV消息"""
        try:
            if message.sign == TLVSign.REGISTER:
                self._handle_tlv_register(message, client)
            elif message.sign == TLVSign.EXECUTE:
                self._handle_tlv_execute(message, client)
            elif message.sign == TLVSign.GET_OUTPUT:
                self._handle_tlv_get_output(message, client)
            else:
                logger.warning(f"未知的TLV消息类型: {message.sign}")
        except Exception as e:
            logger.error(f"处理TLV消息失败: {e}")
            error_response = TLVMessage(
                sign=TLVSign.REGISTER,  # 使用REGISTER类型返回错误
                content={"error": str(e), "success": False}
            )
            client.send_tlv_message(error_response)

    def _handle_tlv_register(self, message: TLVMessage, client: TCPClientConnection):
        """处理TLV注册消息"""
        sandbox_id = message.content.get("sandbox_id")
        if not sandbox_id:
            raise ValueError("注册消息缺少sandbox_id")

        client.sandbox_id = sandbox_id
        client.registered_at = time.time()

        # 添加到客户端连接映射
        self.client_connections[sandbox_id] = client

        # 发送注册成功响应
        response = TLVMessage(
            sign=TLVSign.REGISTER,
            content={
                "success": True,
                "message": f"客户端 {sandbox_id} 注册成功",
                "sandbox_id": sandbox_id,
                "timestamp": time.time()
            }
        )
        client.send_tlv_message(response)

        logger.info(f"客户端 {sandbox_id} 注册成功")
        # 测试 msg 消息
        # self.send_command_to_client(sandbox_id, "ls -al ")

        # time.sleep(4)
        # self.send_get_recent_output_to_client(sandbox_id)
        # time.sleep(4)
        # self.send_pty_close_to_client(sandbox_id)
        # time.sleep(4)

    def _handle_tlv_execute(self, message: TLVMessage, client: TCPClientConnection):
        """处理TLV执行命令消息"""
        sandbox_id = message.content.get("sandbox_id")
        command = message.content.get("command")

        if not sandbox_id or not command:
            raise ValueError("执行消息缺少sandbox_id或command")

        if client.sandbox_id != sandbox_id:
            raise ValueError(f"客户端sandbox_id不匹配: {client.sandbox_id} vs {sandbox_id}")

        # 模拟执行命令并将输出保存到客户端缓冲区
        logger.info(f"在沙箱 {sandbox_id} 中执行命令: {command}")

        # 模拟命令执行结果
        mock_output = f"执行命令: {command}\n输出结果: 这是命令 '{command}' 的模拟输出\n"

        # 添加到客户端输出缓冲区
        client.add_output(mock_output)

        # 发送执行成功响应
        response = TLVMessage(
            sign=TLVSign.EXECUTE,
            content={
                "success": True,
                "message": "命令执行成功",
                "sandbox_id": sandbox_id,
                "command": command,
                "timestamp": time.time(),
                "output_lines": len(client.output_buffer)
            }
        )
        client.send_tlv_message(response)

        logger.info(f"沙箱 {sandbox_id} 命令执行完成")

    def _handle_tlv_get_output(self, message: TLVMessage, client: TCPClientConnection):
        """处理TLV获取输出消息 - 接收客户端的输出响应

        工作流程：
        1. 服务器向客户端发送 GET_OUTPUT 请求
        2. 客户端接收请求后，发送包含输出内容的 GET_OUTPUT 响应
        3. 本方法接收并处理该响应
        """
        try:
            logger.debug("处理 GET_OUTPUT 消息")
            # 从消息中提取输出内容和时间戳
            output_content = message.content.get("output", "")
            timestamp = message.content.get("timestamp")

            if not output_content:
                logger.debug(f"客户端 {client.sandbox_id} 返回空输出")
                return

            # 存储输出内容到客户端对象
            if not hasattr(client, 'last_output'):
                client.last_output = ""
            client.last_output = output_content
            client.last_output_timestamp = timestamp

            # 记录输出大小
            output_size = len(output_content.encode('utf-8'))
            logger.info(f"接收到客户端 {client.sandbox_id} 的输出: {output_size} 字节，时间戳: {timestamp}")

            # 可选：打印输出内容的前 100 个字符用于调试
            if output_content:
                preview = output_content[:100].replace('\n', '\\n')
                logger.debug(f"输出预览: {preview}...")

        except Exception as e:
            logger.error(f"处理客户端 {client.sandbox_id} 的 GET_OUTPUT 响应失败: {str(e)}", exc_info=True)

    def _handle_client_connection(self, client_socket: socket.socket, client_address: str):
        """处理单个客户端连接"""
        logger.info(f"新客户端连接: {client_address}")

        client = TCPClientConnection(client_socket, client_address, f"client_{len(self.client_connections)}")

        try:
            while client.is_connected:
                # 使用select检查socket是否有数据可读
                readable, _, _ = select.select([client_socket], [], [], 1.0)

                if readable:
                    data = client_socket.recv(4096)
                    if not data:  # 连接已关闭
                        break

                    # TLV协议处理
                    try:
                        client.tlv_server.buffer += data
                        # 尝试解析TLV消息
                        logger.debug(f"receive_tlv_message from {client.client_id}")
                        message = client.tlv_server.receive_tlv_message(timeout=1.0)
                        logger.debug(f"_handle_tlv_message from {client.client_id}")
                        self._handle_tlv_message(message, client)
                    except ValueError as e:
                        # 数据不完整或格式错误，继续等待更多数据
                        continue
                    except TimeoutError:
                        # 接收超时，继续等待
                        continue
                    except Exception as e:
                        logger.error(f"TLV消息处理错误: {e}")
                        break

        except Exception as e:
            logger.error(f"处理客户端 {client_address} 时发生错误: {str(e)}")
        finally:
            client.close()
            # 从连接列表中移除
            client_ids_to_remove = []
            for client_id, conn in self.client_connections.items():
                if conn == client or not conn.is_connected:
                    client_ids_to_remove.append(client_id)

            for client_id in client_ids_to_remove:
                del self.client_connections[client_id]

            logger.info(f"客户端 {client_address} 连接结束，移除了 {len(client_ids_to_remove)} 个连接")

    def start_server(self):
        """启动TCP服务器

        支持跨平台自动端口分配：
        - 如果指定端口为 0，操作系统会自动分配可用端口
        - 支持 Linux、macOS、Windows
        - 成功绑定后会更新 self.port 为实际使用的端口
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 绑定到指定端口（如果为0则由系统自动分配）
            self.server_socket.bind((self.host, 0))

            # 获取实际绑定的端口（当指定为0时会自动分配）
            actual_host, actual_port = self.server_socket.getsockname()
            self.port = actual_port

            self.server_socket.listen(10)
            self.is_running = True

            logger.info(f"TCP服务器已启动，监听 {self.host}:{self.port}")

            # 在新线程中接受连接
            self.server_thread = threading.Thread(target=self._accept_connections)
            self.server_thread.daemon = True
            self.server_thread.start()

        except Exception as e:
            logger.error(f"启动TCP服务器失败: {str(e)}")
            self.is_running = False
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
                self.server_socket = None

    def _accept_connections(self):
        """接受客户端连接"""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_socket.settimeout(30.0)  # 设置连接超时
                client_thread = threading.Thread(
                    target=self._handle_client_connection,
                    args=(client_socket, client_address[0])
                )
                client_thread.daemon = True
                client_thread.start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    logger.error(f"接受客户端连接时发生错误: {str(e)}")
                break

    def stop_server(self):
        """停止TCP服务器"""
        self.is_running = False

        # 关闭所有客户端连接
        for client in self.client_connections.values():
            client.close()
        self.client_connections.clear()

        # 关闭服务器socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logger.error(f"关闭服务器socket失败: {str(e)}")

        # 等待服务器线程结束
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5.0)

        logger.info("TCP服务器已停止")

    def send_command_to_client(self, client_id: str, command: str) -> bool:
        tlv_msg = TLVMessage(
            sign=TLVSign.EXECUTE,
            content={
                "success": True,
                "message": "命令执行成功",
                "sandbox_id": client_id,
                "command": command,
                "timestamp": time.time(),
            }
        )
        client = self.client_connections[client_id]
        client.send_tlv_message(tlv_msg)
        return True

    def request_output_from_client(self, client_id: str) -> bool:
        """向客户端请求输出内容

        Args:
            client_id: 目标客户端 ID (sandbox_id)

        Returns:
            bool: 是否成功发送请求
        """
        try:
            if client_id not in self.client_connections:
                logger.error(f"[输出请求] 客户端 {client_id} 未注册")
                return False

            logger.debug(f"[输出请求] 向客户端 {client_id} 请求输出")

            # 创建 GET_OUTPUT 请求消息
            tlv_msg = TLVMessage(
                sign=TLVSign.GET_OUTPUT,
                content={
                    "sandbox_id": client_id,
                    "timestamp": time.time()
                }
            )

            # 发送请求
            client = self.client_connections[client_id]
            client.send_tlv_message(tlv_msg)

            logger.debug(f"[输出请求] 成功向客户端 {client_id} 发送输出请求")
            return True

        except Exception as e:
            logger.error(f"[输出请求错误] 向客户端 {client_id} 请求输出失败: {str(e)}", exc_info=True)
            return False

    def get_recent_output_from_client(self, client_id: str, timeout: float = 2.0) -> Optional[str]:
        """从客户端获取最近的输出内容

        工作流程：
        1. 向客户端发送 GET_OUTPUT 请求
        2. 等待客户端的响应（最多 timeout 秒）
        3. 返回输出内容

        Args:
            client_id: 目标客户端 ID (sandbox_id)
            timeout: 等待响应的超时时间（秒）

        Returns:
            输出内容字符串，如果失败返回 None
        """
        try:
            if client_id not in self.client_connections:
                logger.error(f"[获取输出] 客户端 {client_id} 未注册")
                return None

            client = self.client_connections[client_id]

            # 发送输出请求
            if not self.request_output_from_client(client_id):
                logger.error(f"[获取输出] 无法向客户端 {client_id} 发送请求")
                return None

            # 等待响应（简单的轮询）
            import time as time_module
            start_time = time_module.time()
            while time_module.time() - start_time < timeout:
                # 检查是否收到输出
                if hasattr(client, 'last_output') and client.last_output:
                    output = client.last_output
                    client.last_output = ""  # 清空已读的输出
                    logger.debug(f"[获取输出] 成功获取客户端 {client_id} 的输出")
                    return output

                time_module.sleep(0.1)  # 100ms 轮询间隔

            logger.warning(f"[获取输出] 从客户端 {client_id} 获取输出超时")
            return None

        except Exception as e:
            logger.error(f"[获取输出错误] 获取客户端 {client_id} 输出失败: {str(e)}", exc_info=True)
            return None

    def send_get_recent_output_to_client(self, client_id: str) -> bool:
        """已废弃：使用 request_output_from_client() 代替"""
        return self.request_output_from_client(client_id)

    def send_pty_close_to_client(self, client_id: str) -> bool:
        """发送 PTY_CLOSE 消息给客户端，通知其关闭 PTY 并退出

        当客户端接收到该消息时，应该：
        1. 调用 pty.send_input("exit\\n") 优雅地关闭 PTY
        2. 退出主程序

        Args:
            client_id: 目标客户端 ID (sandbox_id)

        Returns:
            bool: 是否成功发送消息
        """
        try:
            if client_id not in self.client_connections:
                logger.error(f"[PTY关闭] 客户端 {client_id} 未注册")
                return False

            logger.info(f"[PTY关闭] 向客户端 {client_id} 发送 PTY_CLOSE 消息")

            # 创建 PTY_CLOSE 消息
            tlv_msg = TLVProtocol.create_pty_close_message(client_id)

            # 发送消息
            client = self.client_connections[client_id]
            client.send_tlv_message(tlv_msg)

            logger.info(f"[PTY关闭] 成功向客户端 {client_id} 发送 PTY_CLOSE 消息")
            return True

        except Exception as e:
            logger.error(f"[PTY关闭错误] 发送 PTY_CLOSE 消息失败: {str(e)}", exc_info=True)
            return False

    def cleanup_client_connection(self, client_id: str) -> bool:
        """清理指定客户端的 TCP 连接

        Args:
            client_id: 目标客户端 ID (sandbox_id)

        Returns:
            bool: 是否成功清理连接
        """
        try:
            if client_id not in self.client_connections:
                logger.warning(f"[连接清理] 客户端 {client_id} 未在连接列表中")
                return False

            logger.info(f"[连接清理] 清理客户端 {client_id} 的 TCP 连接")

            # 获取客户端连接并关闭
            client = self.client_connections[client_id]
            client.close()

            # 从连接字典中移除
            del self.client_connections[client_id]

            logger.info(f"[连接清理] 成功清理客户端 {client_id} 的连接")
            return True

        except Exception as e:
            logger.error(f"[连接清理错误] 清理客户端 {client_id} 连接失败: {str(e)}", exc_info=True)
            return False
