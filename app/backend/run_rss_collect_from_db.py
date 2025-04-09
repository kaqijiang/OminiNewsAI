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
from update_categories_rss import update_categories_rss

async def main():
    """
    主函数，首先更新数据库中的RSS订阅信息，然后启动RSS新闻收集流程
    """
    logger.info("========= 启动基于数据库的RSS新闻收集服务 =========")
    
    # 首先确保数据库中的RSS订阅信息是最新的
    logger.info("正在更新数据库中的RSS订阅信息...")
    await update_categories_rss()
    
    # 运行数据收集和新闻生成流程
    logger.info("开始执行数据收集任务...")
    await run_collect_data()
    logger.info("数据收集任务完成")
    
    logger.info("========= 基于数据库的RSS新闻收集服务结束 =========")

if __name__ == "__main__":
    # 配置日志
    logger.add("rss_collect_from_db.log", rotation="10 MB", level="INFO")
    
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