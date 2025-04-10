#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from loguru import logger

# 将当前目录添加到 Python 路径中，以便正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.config import settings
from core.db import AsyncSessionLocal
from core.get_redis import RedisUtil
from sqlmodel import select, update
from api.models import NewsCategories

# Redis缓存键名
REDIS_RSS_FEEDS_KEY = "rss_feeds"
REDIS_RSS_CATEGORIES_KEY = "rss_categories"
# Redis缓存过期时间（秒）
REDIS_CACHE_EXPIRE = 86400  # 24小时

async def update_categories_rss():
    """更新数据库中的RSS订阅信息并同步到Redis缓存"""
    logger.info("开始更新news_categories表中的RSS订阅信息...")
    
    # 获取Redis连接
    redis = await RedisUtil.create_redis_pool()
    
    async with AsyncSessionLocal() as session:
        # 获取所有新闻类别
        result = await session.execute(select(NewsCategories))
        categories = result.scalars().all()
        
        # 创建category_value到id的映射
        category_map = {cat.category_value: cat.id for cat in categories}
        logger.info(f"已有类别: {category_map}")
        
        # 更新RSS订阅信息
        updated_count = 0
        rss_urls = []
        rss_categories = {}
        
        # 遍历所有类别，收集有RSS订阅源的类别
        for category in categories:
            if category.rss_feed_url:
                logger.info(f"找到RSS订阅源: {category.category_name} ({category.category_value}): {category.rss_feed_url}")
                rss_urls.append(category.rss_feed_url)
                rss_categories[category.rss_feed_url] = category.category_name
                updated_count += 1
        
        # 更新Redis缓存
        logger.info(f"正在更新Redis缓存...")
        # 保存RSS URL列表
        await RedisUtil.set_key(redis, REDIS_RSS_FEEDS_KEY, rss_urls, expire=REDIS_CACHE_EXPIRE)
        # 保存RSS分类映射
        await RedisUtil.set_key(redis, REDIS_RSS_CATEGORIES_KEY, rss_categories, expire=REDIS_CACHE_EXPIRE)
        
        logger.info(f"成功更新 {updated_count} 个类别的RSS订阅信息，并同步到Redis缓存")
    
    # 关闭Redis连接
    await redis.close()

if __name__ == "__main__":
    logger.add("update_categories_rss.log", rotation="10 MB", level="INFO")
    
    # 运行更新脚本
    asyncio.run(update_categories_rss())
    
    logger.info("RSS订阅信息更新完成") 