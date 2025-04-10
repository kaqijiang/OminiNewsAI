#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
from loguru import logger
import time
from typing import List, Dict, Any

def fetch_rss_content(url: str) -> str:
    """
    获取RSS源的XML内容
    
    Args:
        url: RSS源的URL地址
        
    Returns:
        str: RSS源的XML内容
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        return response.text
    except requests.RequestException as e:
        logger.error(f"获取RSS内容失败: {e}")
        return ""

def parse_rss_feed(xml_content: str) -> List[Dict[str, Any]]:
    """
    解析RSS源的XML内容，提取新闻条目
    
    Args:
        xml_content: RSS源的XML内容
        
    Returns:
        List[Dict[str, Any]]: 解析后的新闻条目列表
    """
    if not xml_content:
        return []
    
    try:
        # 解析XML内容
        root = ET.fromstring(xml_content)
        
        # 定义命名空间
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        news_items = []
        
        # 提取RSS源标题（用于分类）
        alert_title = root.find('atom:title', ns).text
        # 从"Google Alert - xxx"中提取关键词
        keyword = alert_title.replace('Google Alert - ', '').strip() if alert_title else "未知分类"
        
        # 遍历所有entry节点
        for entry in root.findall('atom:entry', ns):
            try:
                item = {}
                
                # 提取RSS条目ID
                id_element = entry.find('atom:id', ns)
                if id_element is not None and id_element.text is not None:
                    # 如果ID是类似 "tag:google.com,2013:googlealerts/feed:17848012798155773345" 的格式
                    # 只提取数字部分作为ID
                    if ':' in id_element.text:
                        short_id = id_element.text.split(':')[-1]
                        item['rss_entry_id'] = short_id
                
                # 提取标题（去除HTML标签）
                title_element = entry.find('atom:title', ns)
                if title_element is not None and title_element.text is not None:
                    title = title_element.text
                    # 移除HTML标签
                    title = title.replace('<b>', '').replace('</b>', '').replace('&#39;', "'")
                    item['title'] = title
                else:
                    item['title'] = "无标题"
                
                # 提取链接
                link_element = entry.find('atom:link', ns)
                if link_element is not None:
                    url = link_element.get('href')
                    # 提取真实URL（Google会重定向）
                    if '&url=' in url:
                        url = url.split('&url=')[1].split('&')[0]
                    item['url'] = url
                
                # 提取内容摘要
                content_element = entry.find('atom:content', ns)
                if content_element is not None and content_element.text is not None:
                    content = content_element.text
                    # 移除HTML标签
                    content = content.replace('<b>', '').replace('</b>', '').replace('&#39;', "'")
                    item['summary'] = content
                else:
                    item['summary'] = "无摘要"
                
                # 提取发布时间
                published_element = entry.find('atom:published', ns)
                if published_element is not None:
                    item['published'] = published_element.text
                
                # 添加关键词（用于分类）
                item['keyword'] = keyword
                
                news_items.append(item)
            except Exception as e:
                logger.error(f"解析RSS条目时出错: {e}")
                continue
        
        return news_items
    except Exception as e:
        logger.error(f"解析RSS内容失败: {e}")
        return []

def get_news_from_rss(rss_urls: List[str]) -> List[Dict[str, Any]]:
    """
    从多个RSS源获取新闻条目
    
    Args:
        rss_urls: RSS源URL列表
        
    Returns:
        List[Dict[str, Any]]: 所有RSS源的新闻条目列表
    """
    all_news_items = []
    
    for url in rss_urls:
        try:
            logger.info(f"正在获取RSS源: {url}")
            xml_content = fetch_rss_content(url)
            news_items = parse_rss_feed(xml_content)
            logger.info(f"从 {url} 获取到 {len(news_items)} 条新闻")
            
            # 为每个新闻条目添加source_feed属性，记录来源的RSS URL
            for item in news_items:
                item['source_feed'] = url
            
            all_news_items.extend(news_items)
        except Exception as e:
            logger.error(f"处理RSS源 {url} 时出错: {e}")
            continue
    
    return all_news_items

if __name__ == "__main__":
    # 测试代码
    rss_url = "https://www.google.com/alerts/feeds/12675972122981091542/10815484404368595628"
    xml_content = fetch_rss_content(rss_url)
    news_items = parse_rss_feed(xml_content)
    
    for item in news_items:
        print(f"标题: {item['title']}")
        print(f"链接: {item['url']}")
        print(f"摘要: {item.get('summary', 'N/A')}")
        print(f"发布时间: {item.get('published', 'N/A')}")
        print(f"关键词: {item['keyword']}")
        print("-" * 50) 