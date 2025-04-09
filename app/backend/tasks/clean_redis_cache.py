#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from datetime import datetime, timedelta
from loguru import logger

# 将当前目录添加到 Python 路径中，以便正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.get_redis import RedisUtil
from tasks.collect_data import REDIS_RECENT_NEWS_KEY

async def clean_redis_news_cache():
    """
    清理Redis中存储的新闻缓存
    - 删除超过14天的新闻记录缓存
    - 限制缓存条目数量，保持在合理范围
    """
    logger.info("开始清理Redis新闻缓存...")
    
    # 获取Redis连接
    redis = await RedisUtil.create_redis_pool()
    
    try:
        # 获取当前缓存的新闻哈希值
        recent_news_hashes = await RedisUtil.get_key(redis, REDIS_RECENT_NEWS_KEY) or []
        
        # 如果缓存超过2000条，保留最新的1000条
        if len(recent_news_hashes) > 2000:
            logger.info(f"新闻缓存超过限制({len(recent_news_hashes)}条)，保留最新的1000条")
            recent_news_hashes = recent_news_hashes[:1000]
            
            # 更新Redis缓存
            await RedisUtil.set_key(redis, REDIS_RECENT_NEWS_KEY, recent_news_hashes, expire=7*86400)  # 7天过期时间
            
            logger.info(f"清理完成，当前缓存新闻条数: {len(recent_news_hashes)}")
        else:
            logger.info(f"新闻缓存在合理范围内({len(recent_news_hashes)}条)，无需清理")
    except Exception as e:
        logger.error(f"清理Redis缓存时出错: {e}")
    finally:
        # 关闭Redis连接
        await redis.close()
        logger.info("Redis新闻缓存清理完成")

if __name__ == "__main__":
    logger.add("clean_redis_cache.log", rotation="10 MB", level="INFO")
    
    try:
        # 执行缓存清理
        asyncio.run(clean_redis_news_cache())
    except Exception as e:
        logger.error(f"执行缓存清理时出错: {e}")
        import traceback
        logger.error(traceback.format_exc()) 