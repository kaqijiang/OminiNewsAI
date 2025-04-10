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
from tasks.collect_data import REDIS_RSS_IDS_KEY

async def clean_redis_news_cache():
    """
    清理Redis中存储的RSS条目ID缓存
    - 限制缓存条目数量，保持在合理范围
    """
    logger.info("开始清理Redis RSS ID缓存...")
    
    # 获取Redis连接
    redis = await RedisUtil.create_redis_pool()
    
    try:
        # 清理RSS条目ID缓存
        recent_rss_ids = await RedisUtil.get_key(redis, REDIS_RSS_IDS_KEY) or []
        
        # 如果缓存超过2000条，保留最新的1000条
        if len(recent_rss_ids) > 2000:
            logger.info(f"RSS ID缓存超过限制({len(recent_rss_ids)}条)，保留最新的1000条")
            recent_rss_ids = recent_rss_ids[:1000]
            
            # 更新Redis缓存
            await RedisUtil.set_key(redis, REDIS_RSS_IDS_KEY, recent_rss_ids, expire=7*86400)  # 7天过期时间
            
            logger.info(f"清理完成，当前缓存RSS ID条数: {len(recent_rss_ids)}")
        else:
            logger.info(f"RSS ID缓存在合理范围内({len(recent_rss_ids)}条)，无需清理")
    except Exception as e:
        logger.error(f"清理Redis缓存时出错: {e}")
    finally:
        # 关闭Redis连接
        await redis.close()
        logger.info("Redis RSS ID缓存清理完成")

if __name__ == "__main__":
    logger.add("clean_redis_cache.log", rotation="10 MB", level="INFO")
    
    try:
        # 执行缓存清理
        asyncio.run(clean_redis_news_cache())
    except Exception as e:
        logger.error(f"执行缓存清理时出错: {e}")
        import traceback
        logger.error(traceback.format_exc()) 