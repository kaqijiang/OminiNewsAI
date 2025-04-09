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

# RSS源和对应类别映射
RSS_CATEGORY_MAPPING = {
    # AI资讯类
    "https://www.google.com/alerts/feeds/12675972122981091542/10275026181448372090": {"name": "360AI News", "category_name": "AI资讯", "category_value": "360ai"},
    "https://www.google.com/alerts/feeds/12675972122981091542/10815484404368595628": {"name": "Claude News", "category_name": "AI资讯", "category_value": "claude"},
    "https://www.google.com/alerts/feeds/12675972122981091542/11259852593024214391": {"name": "GPT News", "category_name": "AI资讯", "category_value": "GPT"},
    "https://www.google.com/alerts/feeds/12675972122981091542/9649448576262545974": {"name": "OpenAI News", "category_name": "AI资讯", "category_value": "openai"},
    
    # 汽车资讯类
    "https://www.google.com/alerts/feeds/12675972122981091542/3216593478712850396": {"name": "上汽大众", "category_name": "汽车资讯", "category_value": "上汽大众"},
    
    # 健康和医疗类
    "https://www.google.com/alerts/feeds/12675972122981091542/4060774748412242252": {"name": "中医理疗", "category_name": "健康和医疗", "category_value": "中医理疗"}
}

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
        
        for rss_url, info in RSS_CATEGORY_MAPPING.items():
            category_value = info["category_value"]
            
            if category_value in category_map:
                cat_id = category_map[category_value]
                logger.info(f"更新类别 '{category_value}' (ID: {cat_id}) 的RSS订阅源: {rss_url}")
                
                # 更新数据库
                stmt = update(NewsCategories).where(NewsCategories.id == cat_id).values(rss_feed_url=rss_url)
                await session.execute(stmt)
                updated_count += 1
                
                # 收集用于Redis的数据
                rss_urls.append(rss_url)
                rss_categories[rss_url] = info["category_name"]
            else:
                logger.warning(f"找不到类别: {category_value}, 无法更新其RSS订阅源")
        
        # 提交数据库事务
        await session.commit()
        
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