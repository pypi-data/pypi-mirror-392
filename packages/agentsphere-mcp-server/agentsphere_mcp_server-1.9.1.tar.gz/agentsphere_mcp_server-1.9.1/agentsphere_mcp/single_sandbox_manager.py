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
import pathlib
from platformdirs import user_desktop_dir, user_documents_dir, user_downloads_dir

from agentsphere_base.api import AsyncApiClient, handle_api_exception
from agentsphere_base.api.client.api.sandboxes import get_sandboxes_sandbox_id
from agentsphere_base import ConnectionConfig
from agentsphere_base.sandbox.sandbox_api import SandboxApiBase
from .logger import logger

class SingleSandboxManager:

    def __init__(self):
        # 存储沙箱实例和相关信息
        self._sandbox: Optional[AsyncSandbox] = None
        self._sandbox_info: Optional[Dict[str, Any]] = None
        self._api_key: Optional[str] = None
        self._domain: str = os.getenv("AGENTSPHERE_DOMAIN", "agentsphere.run")
        logger.info("单沙箱管理器初始化完成")

    def _get_api_key(self) -> str:
        """从环境变量获取 API key"""
        if self._api_key:
            return self._api_key

        # 尝试从环境变量获取 API key
        api_key = os.getenv("AGENTSPHERE_API_KEY")

        if not api_key:
            raise Exception("AGENTSPHERE_API_KEY not found, please set environment variable")

        self._api_key = api_key
        logger.info(f"成功获取 API key: ***{api_key[-4:]}")
        return api_key

    async def get_sandbox(self) -> AsyncSandbox:
        """获取或创建沙箱实例"""
        current_time = time.time()
        logger.debug("获取沙箱实例")

        # 检查是否已有沙箱实例
        if self._sandbox is not None:
            logger.debug("找到现有沙箱实例")

            # 检查沙箱是否仍然运行中
            try:
                if await self._sandbox.is_running(request_timeout=5.0):
                    # 更新最后使用时间
                    if self._sandbox_info:
                        self._sandbox_info["last_used"] = current_time
                    logger.info(f"复用现有沙箱: {self._sandbox.sandbox_id}")
                    return self._sandbox
                else:
                    # 沙箱已经停止，清除缓存
                    logger.info("现有沙箱已停止，将创建新沙箱")
                    self._sandbox = None
                    self._sandbox_info = None
            except Exception as e:
                # 沙箱连接异常，清除缓存
                logger.error(f"沙箱连接异常: {str(e)}")
                self._sandbox = None
                self._sandbox_info = None

        # 获取或创建沙箱实例
        api_key = self._get_api_key()
        target_template = "agentsphere-code-interpreter-v1"

        # 尝试获取并连接到现有沙箱
        existing_sandbox = await self._try_connect_existing_sandbox(api_key, target_template, current_time)
        if existing_sandbox:
            return existing_sandbox

        # 没有找到合适的现有沙箱，创建新的
        return await self._create_new_sandbox(api_key, target_template, current_time)

    async def _try_connect_existing_sandbox(self, api_key: str, target_template: str, current_time: float) -> Optional[AsyncSandbox]:
        """
        尝试连接到现有的相同template沙箱

        :param api_key: API密钥
        :param target_template: 目标模板ID
        :param current_time: 当前时间戳
        :return: 成功连接的沙箱实例，如果没有找到或连接失败则返回None
        """
        try:
            logger.info("检查云端现有沙箱...")
            existing_sandboxes = await AsyncSandbox.list(
                api_key=api_key,
                domain=self._domain
            )

            # 筛选出相同template且运行中的沙箱
            target_sandboxes = [
                sbx for sbx in existing_sandboxes
                if sbx.name == target_template and sbx.state.lower() == "running"
            ]

            if not target_sandboxes:
                logger.info("未找到运行中的相同template沙箱")
                return None

            # 按启动时间降序排序，选择最新的
            latest_sandbox = max(target_sandboxes, key=lambda x: x.started_at)
            logger.info(f"找到现有沙箱: {latest_sandbox.sandbox_id} (启动于 {latest_sandbox.started_at})")

            # 尝试连接到现有沙箱
            connected_sandbox = await AsyncSandbox.connect(
                sandbox_id=latest_sandbox.sandbox_id,
                api_key=api_key,
                domain=self._domain
            )

            # 设置沙箱信息
            self._sandbox = connected_sandbox
            self._sandbox_info = {
                "sandbox_id": connected_sandbox.sandbox_id,
                "created_at": latest_sandbox.started_at.timestamp(),
                "last_used": current_time
            }

            logger.info(f"成功连接到现有沙箱: {connected_sandbox.sandbox_id}")
            return connected_sandbox

        except Exception as e:
            logger.warning(f"尝试连接现有沙箱失败: {str(e)}")
            return None

    async def _create_new_sandbox(self, api_key: str, target_template: str, current_time: float) -> AsyncSandbox:
        """
        创建新的沙箱实例

        :param api_key: API密钥
        :param target_template: 模板ID
        :param current_time: 当前时间戳
        :return: 新创建的沙箱实例
        """
        try:
            logger.info("创建新沙箱...")
            new_sandbox = await AsyncSandbox.create(
                api_key=api_key,
                template=target_template,
                domain=self._domain,
                timeout=43200  # 12小时超时
            )

            self._sandbox = new_sandbox
            self._sandbox_info = {
                "sandbox_id": new_sandbox.sandbox_id,
                "created_at": current_time,
                "last_used": current_time
            }

            logger.info(f"成功创建新沙箱: {new_sandbox.sandbox_id}")
            return new_sandbox

        except Exception as e:
            logger.error(f"创建沙箱失败: {str(e)}")
            raise Exception(f"Failed to create sandbox: {str(e)}")

    def get_sandbox_info(self) -> Optional[Dict[str, Any]]:
        """获取沙箱信息"""
        if self._sandbox_info:
            logger.debug(f"获取沙箱信息: {self._sandbox_info}")
            return self._sandbox_info.copy()
        logger.debug("没有沙箱信息")
        return None

    async def cleanup(self):
        """清理沙箱资源"""
        if self._sandbox:
            try:
                logger.info(f"正在清理沙箱: {self._sandbox.sandbox_id}")
                await self._sandbox.kill()
                logger.info("沙箱清理完成")
            except Exception as e:
                logger.error(f"沙箱清理失败: {str(e)}")
            finally:
                self._sandbox = None
                self._sandbox_info = None
