import feedparser
import time
import schedule
import logging
import sqlite3
import requests
import re
import os
from datetime import datetime, timezone
import redis
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    filename='../monitor_rss.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 多个 Google Alerts RSS Feed URL
RSS_FEED_URLS = [
    
]

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # 如果有密码，填写密码

def init_redis():
    """初始化 Redis 连接"""
    try:
        pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True  # 自动将字节转换为字符串
        )
        r = redis.Redis(connection_pool=pool)
        # 测试连接
        r.ping()
        logger.info("成功连接到 Redis。")
        return r
    except redis.RedisError as e:
        logger.error(f"连接 Redis 失败: {e}")
        raise

# 提取关键词
def extract_keyword_bs(entry):
    try:
        title = entry.get('title', '')
        soup = BeautifulSoup(title, 'html.parser')
        b_tag = soup.find('b')
        if b_tag:
            return b_tag.text

        # 检查 content
        contents = entry.get('content', [])
        for content in contents:
            soup = BeautifulSoup(content.get('value', ''), 'html.parser')
            b_tag = soup.find('b')
            if b_tag:
                return b_tag.text

        # 检查 summary
        summary = entry.get('summary', '')
        soup = BeautifulSoup(summary, 'html.parser')
        b_tag = soup.find('b')
        if b_tag:
            return b_tag.text

        return None
    except Exception as e:
        print(f"提取关键词时出错: {e}")
        return None

# 去除HTML标签，提取纯文本标题
def clean_title(title):
    # 使用BeautifulSoup去除<b>标签
    soup = BeautifulSoup(title, 'html.parser')
    return soup.get_text()
# 提取url中的实际目标网址
def extract_real_url(entry):
    link = entry.links[0].get('href')
    # 使用正则表达式提取 &url= 后面的内容
    match = re.search(r'&url=([^&]+)', link)
    return match.group(1) if match else None
def convert_to_timestamp(published_time):
    # 将字符串转换为 datetime 对象，并设置为 UTC 时区
    dt = datetime.strptime(published_time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    timestamp = int(dt.timestamp())
    return timestamp
def process_feed(feed_url,new_items):
    """处理单个 RSS Feed，提取新条目并保存到数据库"""
    redis_client = init_redis()
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            logger.error(f"解析 RSS Feed 失败: {feed_url} - {feed.bozo_exception}")
            return

        for entry in feed.entries:
            # # 获取条目的唯一 ID
            entry_id = entry.get('id') or entry.get('guid') or entry.get('link')
            if not entry_id:
                logger.warning(f"条目缺少唯一标识符，跳过: {entry}")
                continue

            # 检查 Redis 是否已经处理过该条目
            if redis_client.exists(entry_id):
                logger.info(f"条目已存在，跳过: {entry_id}")
                continue  # 跳过已处理的条目

            # 提取信息
            keyword = extract_keyword_bs(entry)
            title = clean_title(entry.title)
            url = extract_real_url(entry)
            published_time = convert_to_timestamp(entry.published)
            summary = entry.summary
            new_items.append(
                {"keyword": keyword, "title": title.strip(), "url": url,
                 "date": published_time})
            # 打印新消息
            print(f"新消息来自 {feed_url}:")
            print(f"标题: {title}")
            print(f"关键词: {keyword}")
            print(f"链接: {url}")
            print(f"summary: {summary}")
            print(f"发布时间: {published_time}\n")


            # 更新 Redis 中的最新条目 ID
            redis_client.set(entry_id, 1, ex=1*24*60*60)

    except Exception as e:
        logger.error(f"处理 RSS Feed 时发生错误: {feed_url} - {e}")

def process_all_feeds():
    """处理所有配置的 RSS Feed"""
    logger.info("开始处理所有 RSS Feed。")
    new_items = []
    for feed_url in RSS_FEED_URLS:
        logger.info(f"正在处理 RSS Feed: {feed_url}")
        process_feed(feed_url, new_items)

    logger.info("所有 RSS Feed 处理完成。")
    return new_items


if __name__ == "__main__":
    # 初始化 Redis
    process_all_feeds()
