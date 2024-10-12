import json
from redis import asyncio as aioredis
from redis.exceptions import AuthenticationError, TimeoutError, RedisError
from fastapi import FastAPI
from core.config import redis_settings
from utils.logging_config import LogManager

logger = LogManager.get_logger()

class RedisUtil:
    """
    Redis相关方法
    """

    @classmethod
    async def check_redis(cls) -> None:
        """
        测试Redis连接是否成功。
        """
        try:
            redis = await aioredis.from_url(
                f"redis://{redis_settings.redis_host}:{redis_settings.redis_port}",
                username=redis_settings.redis_username,
                password=redis_settings.redis_password,
                db=redis_settings.redis_database,
                encoding='utf-8',
                decode_responses=True
            )
            await redis.ping()
            logger.info("Redis连接成功")
            await redis.close()
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise

    @classmethod
    async def create_redis_pool(cls) -> aioredis.Redis:
        """
        应用启动时初始化redis连接

        :return: Redis连接对象
        """
        logger.info('开始连接redis...')
        redis = await aioredis.from_url(
            f"redis://{redis_settings.redis_host}:{redis_settings.redis_port}",
            username=redis_settings.redis_username,
            password=redis_settings.redis_password,
            db=redis_settings.redis_database,
            encoding='utf-8',
            decode_responses=True,
        )
        try:
            connection = await redis.ping()
            if connection:
                logger.info('redis连接成功')
            else:
                logger.error('redis连接失败')
        except AuthenticationError as e:
            logger.error(f'redis用户名或密码错误，详细错误信息：{e}')
        except TimeoutError as e:
            logger.error(f'redis连接超时，详细错误信息：{e}')
        except RedisError as e:
            logger.error(f'redis连接错误，详细错误信息：{e}')
            await redis.close()
            raise
        return redis

    @classmethod
    async def close_redis_pool(cls, app: FastAPI):
        """
        应用关闭时关闭redis连接

        :param app: fastapi对象
        :return:
        """
        if hasattr(app.state, 'redis'):
            await app.state.redis.close()
            logger.info('关闭redis连接成功')

    @classmethod
    async def init_sys_dict(cls, redis: aioredis.Redis):
        """
        应用启动时缓存字典表

        :param redis: redis对象
        :return:
        """
        # async with AsyncSessionLocal() as session:
        #     await DictDataService.init_cache_sys_dict_services(session, redis)

    @classmethod
    async def init_sys_config(cls, redis: aioredis.Redis):
        """
        应用启动时缓存参数配置表

        :param redis: redis对象
        :return:
        """
        # async with AsyncSessionLocal() as session:
        #     await ConfigService.init_cache_sys_config_services(session, redis)

    @classmethod
    async def set_key(cls, redis, key: str, value: any, expire: int = None):
        """
        设置键值对到Redis
        :param redis: Redis 连接对象
        :param key: 键
        :param value: 值，支持字符串、整数、列表、字典等
        :param expire: 过期时间，秒
        :return:
        """
        try:
            # 序列化对象列表
            if isinstance(value, list) and all(hasattr(item, 'dict') for item in value):
                value = json.dumps([item.dict() for item in value],ensure_ascii=False)
            # 序列化单个对象
            elif hasattr(value, 'dict'):
                value = json.dumps(value.dict(),ensure_ascii=False)
            # 序列化其他数据类型
            elif isinstance(value, (list, dict)):
                value = json.dumps(value,ensure_ascii=False)

            if expire:
                await redis.setex(key, expire, value)
            else:
                await redis.set(key, value)
            logger.info(f"设置Redis键值对: {key} = {value}")
        except RedisError as e:
            logger.error(f"设置Redis键值对失败: {e}")
            raise

    @classmethod
    async def get_key(cls, redis, key: str) -> any:
        """
        从Redis获取值
        :param redis: Redis 连接对象
        :param key: 键
        :return: 值，自动尝试将JSON字符串转换为列表或字典
        """
        try:
            value = await redis.get(key)
            if value:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # 如果转换失败，保持原来的值（字符串）
            return value
        except RedisError as e:
            logger.error(f"获取Redis键值失败: {e}")
            raise

    @classmethod
    async def delete_key(cls, redis, key: str):
        """
        从Redis删除键
        :param redis: Redis 连接对象
        :param key: 键
        :return:
        """
        try:
            await redis.delete(key)
            logger.info(f"删除Redis键: {key}")
        except RedisError as e:
            logger.error(f"删除Redis键失败: {e}")
            raise
