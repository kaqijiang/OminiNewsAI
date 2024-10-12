import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from core import db
from core.db import async_engine
from core.get_redis import RedisUtil
from utils.logging_config import LogManager

# 日志设置
logger = LogManager.get_logger()

max_tries = 60 * 1  # 1分钟
wait_seconds = 1  # 每次重试等待1秒

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_services() -> None:
    """
    初始化服务，包括数据库和Redis的连接测试。
    """
    await db.check_mysql_db(async_engine)
    await RedisUtil.check_redis()


async def main() -> None:
    logger.info("初始化服务")
    await init_services()
    logger.info("服务初始化完成")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
