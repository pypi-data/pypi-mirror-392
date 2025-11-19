import logging
logging.basicConfig(
    level=logging.INFO,  # 改为 DEBUG 以显示所有调试日志
    format='%(asctime)s | %(levelname)s | %(message)s'
    # handlers=[
    #     logging.FileHandler('mcp_server.log'),
    #     # 对于 STDIO 传输，可以注释掉控制台输出避免干扰
    #     # logging.StreamHandler()
    # ]
)
logger = logging.getLogger(__name__)
