#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from loguru import logger

# 将当前目录添加到 Python 路径中，以便正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from tasks.collect_data import run_collect_data
from core.config import settings

async def main():
    """
    主函数，启动RSS新闻收集流程
    """
    logger.info("========= 启动RSS新闻收集服务 =========")
    logger.info(f"已配置 {len(settings.RSS_FEEDS)} 个RSS订阅源:")
    for i, feed in enumerate(settings.RSS_FEEDS):
        logger.info(f"  {i+1}. {feed['name']}: {feed['url']} [分类: {feed['category']}]")
    
    # 运行数据收集和新闻生成流程
    logger.info("开始执行数据收集任务...")
    await run_collect_data()
    logger.info("数据收集任务完成")
    
    logger.info("========= RSS新闻收集服务结束 =========")

if __name__ == "__main__":
    # 配置日志
    logger.add("rss_collect.log", rotation="10 MB", level="INFO")
    
    try:
        # 执行主函数
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("用户中断执行")
    except Exception as e:
        logger.error(f"执行过程中出现错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("程序执行结束") 