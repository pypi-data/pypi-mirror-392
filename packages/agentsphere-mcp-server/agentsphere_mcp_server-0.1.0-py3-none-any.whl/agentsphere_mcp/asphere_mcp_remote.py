import os
import time
from typing import Optional, Dict, List, Any
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers
from agentsphere import AsyncSandbox
import httpx

# 添加 loguru 日志配置
from loguru import logger

# 添加日志文件输出
logger.add(
    "logs/asphere_mcp_remote.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="50 MB",  # 文件大小超过50MB时轮转
    retention="30 days",  # 保留30天的日志文件
    compression="zip",  # 压缩旧日志文件
    encoding="utf-8"
)

mcp = FastMCP("Agent Sphere Streamable-HTTP MCP Server")


# 多用户沙箱管理器
class SandboxManager:
    def __init__(self):
        # 存储每个用户的沙箱实例 {user_id: {sandbox: AsyncSandbox, last_used: float}}
        self._user_sandboxes: Dict[str, Dict[str, Any]] = {}
        logger.info("沙箱管理器初始化完成")

    async def get_sandbox(self, user_id: str, api_key: str) -> AsyncSandbox:
        """获取或创建用户专属的沙箱实例"""
        current_time = time.time()
        logger.debug(f"为用户 {user_id} 获取沙箱实例")

        # 检查是否已有该用户的沙箱
        if user_id in self._user_sandboxes:
            sandbox_info = self._user_sandboxes[user_id]
            sandbox = sandbox_info["sandbox"]
            logger.debug(f"找到用户 {user_id} 的现有沙箱")

            # 检查沙箱是否仍然运行中
            try:
                if await sandbox.is_running(request_timeout=5.0):
                    # 更新最后使用时间
                    sandbox_info["last_used"] = current_time
                    logger.info(f"复用用户 {user_id} 的现有沙箱: {sandbox.sandbox_id}")
                    return sandbox
                else:
                    # 沙箱已经停止，从缓存中移除
                    logger.info(f"用户 {user_id} 的沙箱已停止，将创建新沙箱")
                    del self._user_sandboxes[user_id]
            except Exception as e:
                # 沙箱连接异常，从缓存中移除
                logger.error(f"用户 {user_id} 的沙箱连接异常: {str(e)}")
                del self._user_sandboxes[user_id]

        # 创建新的沙箱实例，使用用户的 API key
        try:
            logger.info(f"为用户 {user_id} 创建新沙箱...")
            new_sandbox = await AsyncSandbox.create(
                api_key=api_key,
                template="agentsphere-code-interpreter-v1",
                domain="agentsphere.run",
                timeout=3600  # 60分钟超时
            )
            self._user_sandboxes[user_id] = {
                "sandbox": new_sandbox,
                "last_used": current_time,
                "created_at": current_time
            }
            logger.success(f"成功为用户 {user_id} 创建沙箱: {new_sandbox.sandbox_id}")
            return new_sandbox
        except Exception as e:
            logger.error(f"为用户 {user_id} 创建沙箱失败: {str(e)}")
            raise Exception(f"创建沙箱失败: {str(e)}")

    def get_user_sandbox_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户沙箱信息"""
        if user_id in self._user_sandboxes:
            sandbox_info = self._user_sandboxes[user_id]
            info = {
                "sandbox_id": sandbox_info["sandbox"].sandbox_id,
                "created_at": sandbox_info["created_at"],
                "last_used": sandbox_info["last_used"]
            }
            logger.debug(f"获取用户 {user_id} 沙箱信息: {info}")
            return info
        logger.debug(f"用户 {user_id} 没有沙箱信息")
        return None


# 全局沙箱管理器实例
sandbox_manager = SandboxManager()


def get_user_info(ctx: Context) -> tuple[str, str]:  # FastMCP 会自动注入，Context 参数对客户端不可见，用户不会看到也不需要传递这个参数
    """从上下文中提取用户ID和API key"""
    try:
        # 从 HTTP headers 中获取 Authorization 信息
        headers = get_http_headers()
        auth_header = headers.get("authorization", "")

        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]  # 移除 "Bearer " 前缀

            # 使用 API key 作为唯一用户标识
            user_id = api_key

            logger.debug(f"提取用户信息成功: user_id={user_id}, api_key=***{api_key[-4:]}")
            return user_id, api_key
        else:
            logger.error("Authorization header 中未找到有效的 Bearer token")
            raise Exception("未找到有效的 Bearer token")

    except Exception as e:
        logger.error(f"获取用户认证信息失败: {str(e)}")
        raise Exception(f"获取用户认证信息失败: {str(e)}")


@mcp.tool
async def exec_command(
        cmd: str,
        ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见，用户不会看到也不需要传递这个参数
) -> Dict[str, Any]:
    """在 sandbox 中执行 linux 系统命令

       注意：
        - 如果执行的命令会占用命令行窗口（如启动 web 服务），函数会一直等待
        - 对于需要持续运行的服务，建议使用 nohup 后台启动方式：
          * Next.js 示例: "nohup npm run dev > nextjs.log 2>&1 &"
        - 命令执行超时时间为 90 秒

    Args:
        cmd: 要执行的命令

    Returns:
        命令执行结果，包含 stdout、stderr 和 success 字段
    """
    try:
        user_id, api_key = get_user_info(ctx)

        # MCP 协议日志 - 发送给客户端
        await ctx.info(f"用户 {user_id} 请求执行命令: {cmd}")
        # loguru 日志 - 服务器端可见
        logger.info(f"[MCP工具调用 exec_command] 用户 {user_id} 请求执行命令: {cmd}")

        # 获取用户专属沙箱
        sandbox = await sandbox_manager.get_sandbox(user_id, api_key)

        # 执行命令
        logger.debug(f"开始执行命令: {cmd}")
        result = await sandbox.commands.run(cmd=cmd, timeout=90, request_timeout=90)

        # 记录执行结果
        logger.info(
            f"命令执行完成 - 退出码: {result.exit_code}, stdout长度: {len(result.stdout)}, stderr长度: {len(result.stderr)}")
        if result.stdout:
            logger.debug(f"命令输出 (stdout): {result.stdout}")
        if result.stderr:
            logger.warning(f"命令错误输出 (stderr): {result.stderr}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": "true" if result.exit_code == 0 else "false"
        }

    except Exception as e:
        # MCP 协议错误日志 - 发送给客户端
        await ctx.error(f"命令执行失败: {str(e)}")
        # loguru 错误日志 - 服务器端可见，包含完整堆栈信息
        logger.error(f"[MCP工具错误] 命令执行失败: {str(e)}", exc_info=True)

        return {
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


@mcp.tool
async def get_preview_link(
    port: int,
    ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见，用户不会看到也不需要传递这个参数
) -> Dict[str, Any]:
    """获取 sandbox 中 web 服务的 url。
       注意：需要先通过 exec_command 创建和启动 next.js, streamlit 等等 web 服务。
       请确保启动的 web 服务端口号没有被占用。
       因为沙箱有网络安全策略，所有 web 服务无法直接通过 ip + 端口号访问，需要调用此方法才能拿到外部可以访问的 url。

    Args:
        port: 端口号

    Returns:
        url 链接
    """
    try:
        user_id, api_key = get_user_info(ctx)

        # MCP 协议日志 - 发送给客户端
        await ctx.info(f"用户 {user_id} 请求获取端口 {port} 的预览链接")
        # loguru 日志 - 服务器端可见
        logger.info(f"[MCP工具调用 get_preview_link] 用户 {user_id} 请求获取端口 {port} 的预览链接")

        # 获取用户专属沙箱
        sandbox = await sandbox_manager.get_sandbox(user_id, api_key)

        # 获取主机地址
        host = sandbox.get_host(port)
        
        # 构建完整的 URL
        preview_url = f"https://{host}"

        logger.info(f"成功生成预览链接: {preview_url}")

        return {
            "url": preview_url
        }

    except Exception as e:
        # MCP 协议错误日志 - 发送给客户端
        await ctx.error(f"获取预览链接失败: {str(e)}")
        # loguru 错误日志 - 服务器端可见，包含完整堆栈信息
        logger.error(f"[MCP工具错误] 获取预览链接失败: {str(e)}", exc_info=True)

        return {
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


@mcp.tool
async def sandbox_is_running(
    sandbox_id: str,
    ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见，用户不会看到也不需要传递这个参数
) -> Dict[str, Any]:
    """检查指定 sandbox 是否正在运行

    此方法通过调用 API 获取沙箱状态，而不是通过 envd 健康检查。
    这样可以更准确地反映沙箱在控制平面的实际状态。

    Args:
        sandbox_id: 沙箱 ID

    Returns:
        包含沙箱运行状态的字典
    """
    try:
        user_id, api_key = get_user_info(ctx)

        # MCP 协议日志 - 发送给客户端
        await ctx.info(f"用户 {user_id} 请求检查沙箱状态: {sandbox_id}")
        # loguru 日志 - 服务器端可见
        logger.info(f"[MCP工具调用 sandbox_is_running] 用户 {user_id} 检查沙箱状态: {sandbox_id}")

        # 从环境变量或配置中获取 domain
        domain = os.getenv("AGENTSPHERE_DOMAIN", "agentsphere.run")

        # 使用 API 获取沙箱详细信息
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.{domain}/sandboxes/{sandbox_id}",
                headers={"X-API-Key": api_key},
                timeout=10.0
            )

            if response.status_code == 404:
                logger.warning(f"沙箱不存在: {sandbox_id}")
                return {
                    "result": False,
                    "message": "沙箱不存在或已被删除"
                }

            if response.status_code != 200:
                logger.error(f"API 请求失败: {response.status_code}, {response.text}")
                return {
                    "result": False,
                    "error": {
                        "name": "APIError",
                        "value": f"API 返回状态码 {response.status_code}"
                    }
                }

            data = response.json()
            sandbox_state = data.get("state", "unknown")

            # 检查状态是否为 running
            is_running = sandbox_state == "running"

            logger.info(f"沙箱 {sandbox_id} 状态: {sandbox_state}, 是否运行: {is_running}")

            return {
                "result": is_running,
                "state": sandbox_state,
                "sandbox_id": sandbox_id
            }

    except Exception as e:
        # MCP 协议错误日志 - 发送给客户端
        await ctx.error(f"检查沙箱状态失败: {str(e)}")
        # loguru 错误日志 - 服务器端可见，包含完整堆栈信息
        logger.error(f"[MCP工具错误] 检查沙箱状态失败: {str(e)}", exc_info=True)

        return {
            "result": False,
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


if __name__ == "__main__":
    # MCP 服务器配置参数
    TRANSPORT = "streamable-http"
    HOST = "0.0.0.0"
    PORT = 9000

    logger.info("启动 Agent Sphere Remote MCP 服务器...")
    logger.info(f"服务器配置: transport={TRANSPORT}, host={HOST}, port={PORT}")

    try:
        mcp.run(transport=TRANSPORT, host=HOST, port=PORT)
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}", exc_info=True)
    finally:
        logger.info("MCP 服务器已停止")