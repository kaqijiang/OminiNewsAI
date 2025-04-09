#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import time
from loguru import logger

# 将当前目录添加到 Python 路径中，以便正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入任务
from tasks.collect_data import run_collect_data, collect_data, generate_news
from core.db import AsyncSessionLocal
from api.models import PlatformConfig
from core.get_redis import RedisUtil
from core.config import settings

async def test_collect_data():
    """测试RSS订阅收集数据函数"""
    logger.info("开始测试RSS订阅数据收集")
    
    # 检查RSS配置
    if not settings.RSS_FEEDS:
        logger.warning("没有配置RSS订阅源，请先在config.py中配置RSS_FEEDS")
        return
    
    logger.info(f"已配置 {len(settings.RSS_FEEDS)} 个RSS订阅源:")
    for i, feed in enumerate(settings.RSS_FEEDS):
        logger.info(f"  {i+1}. {feed['name']}: {feed['url']} [分类: {feed['category']}]")
    
    # 执行数据收集
    async with AsyncSessionLocal() as session:
        await collect_data(session)
    
    logger.info("RSS数据收集测试完成")

async def test_generate_news():
    """测试生成新闻摘要函数"""
    logger.info("开始测试新闻摘要生成")
    
    redis = await RedisUtil.create_redis_pool()
    async with AsyncSessionLocal() as session:
        await generate_news(session, redis)
    
    logger.info("新闻摘要生成测试完成")

async def test_full_process():
    """测试完整的数据收集和生成摘要流程"""
    logger.info("开始测试完整流程")
    
    # 执行完整流程
    await run_collect_data()
    
    logger.info("完整流程测试完成")

if __name__ == "__main__":
    # 配置日志
    logger.add("test_collect_data.log", rotation="10 MB", level="INFO")
    logger.info("开始测试数据收集与处理功能...")
    
    try:
        # 只测试数据收集
        asyncio.run(test_collect_data())
        
        # 只测试摘要生成
        # asyncio.run(test_generate_news())
        
        # 测试完整流程
        # asyncio.run(test_full_process())
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
    
    logger.info("测试结束") 