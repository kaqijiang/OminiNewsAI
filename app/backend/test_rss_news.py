#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from loguru import logger

# 将当前目录添加到 Python 路径中，以便正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from tasks.get_rss_news import fetch_rss_content, parse_rss_feed, get_news_from_rss

# 手动定义RSS源列表，避免配置文件问题
RSS_FEEDS = [
    {
        "name": "Claude News", 
        "url": "https://www.google.com/alerts/feeds/12675972122981091542/10815484404368595628",
        "category": "AI资讯"
    },
    {
        "name": "OpenAI News",
        "url": "https://www.google.com/alerts/feeds/12675972122981091542/9649448576262545974",
        "category": "AI资讯"
    }
]

async def test_single_rss():
    """测试单个RSS源的获取和解析"""
    if not RSS_FEEDS:
        logger.error("没有配置RSS源")
        return
    
    # 测试 OpenAI RSS源
    feed = RSS_FEEDS[1]  # 使用OpenAI RSS源
    url = feed["url"]
    logger.info(f"测试RSS源: {feed['name']} ({url})")
    
    # 获取RSS内容
    xml_content = fetch_rss_content(url)
    if not xml_content:
        logger.error(f"无法获取RSS内容: {url}")
        return
    
    logger.info(f"成功获取RSS内容，长度: {len(xml_content)} 字符")
    
    # 解析RSS内容
    news_items = parse_rss_feed(xml_content)
    logger.info(f"解析到 {len(news_items)} 条新闻")
    
    # 打印每条新闻
    for i, item in enumerate(news_items):
        logger.info(f"新闻 {i+1}:")
        logger.info(f"  标题: {item.get('title', 'N/A')}")
        logger.info(f"  链接: {item.get('url', 'N/A')}")
        logger.info(f"  摘要: {item.get('summary', 'N/A')[:100]}..." if item.get('summary') else "  摘要: N/A")
        logger.info(f"  关键词: {item.get('keyword', 'N/A')}")
        logger.info(f"  发布时间: {item.get('published', 'N/A')}")
        logger.info("-" * 50)

async def test_all_rss():
    """测试所有配置的RSS源"""
    urls = [feed["url"] for feed in RSS_FEEDS]
    if not urls:
        logger.error("没有配置RSS源")
        return
    
    logger.info(f"开始测试 {len(urls)} 个RSS源")
    
    # 获取所有RSS新闻
    news_items = get_news_from_rss(urls)
    logger.info(f"共获取到 {len(news_items)} 条新闻")
    
    # 按关键词分组统计
    keyword_counts = {}
    for item in news_items:
        keyword = item.get('keyword', 'unknown')
        if keyword not in keyword_counts:
            keyword_counts[keyword] = 0
        keyword_counts[keyword] += 1
    
    logger.info("按关键词统计:")
    for keyword, count in keyword_counts.items():
        logger.info(f"  {keyword}: {count} 条")

if __name__ == "__main__":
    # 配置日志
    logger.add("test_rss.log", rotation="10 MB", level="INFO")
    logger.info("开始测试RSS功能...")
    
    # 创建事件循环并运行测试
    try:
        # 测试单个RSS源 (OpenAI)
        asyncio.run(test_single_rss())
        
        # 测试所有RSS源
        asyncio.run(test_all_rss())
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
    
    logger.info("测试结束") 