import time
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from loguru import logger

from api.crud.news_list_crud import get_all_not_generate_news, update_news_item, create_news_list, check_news_exists
from api.models import PlatformConfig, NewsListCreate, NewsCategories
from core.config import settings
from core.db import AsyncSessionLocal
from core.get_redis import RedisUtil
from tasks.OpenAIProcessor import OpenAIProcessor
from tasks.get_news import process_all_feeds
from tasks.get_rss_news import get_news_from_rss
from utils.nodriver_parse import get_content_from_page
from update_categories_rss import REDIS_RSS_FEEDS_KEY, REDIS_RSS_CATEGORIES_KEY, update_categories_rss

# Redis中存储最近处理过的新闻条目的键名
REDIS_RECENT_NEWS_KEY = "recent_news_items"
# 记录最近新闻的过期时间（秒）
REDIS_RECENT_NEWS_EXPIRE = 604800  # 7天


def generate_news_hash(title: str, url: str) -> str:
    """
    根据新闻标题和URL生成唯一哈希值
    """
    content = f"{title}_{url}".encode('utf-8')
    return hashlib.md5(content).hexdigest()


async def collect_data(session: AsyncSession):
    """
    从RSS订阅中收集数据并插入数据库，然后请求 OpenAI API 进行总结
    """
    logger.info("自动获取信息中")
    
    # 尝试从Redis获取RSS订阅信息
    redis = await RedisUtil.create_redis_pool()
    
    # 获取RSS源列表和分类映射
    rss_urls = await RedisUtil.get_key(redis, REDIS_RSS_FEEDS_KEY)
    rss_categories = await RedisUtil.get_key(redis, REDIS_RSS_CATEGORIES_KEY)
    
    # 如果Redis中没有缓存，则从数据库获取
    if not rss_urls or not rss_categories:
        logger.info("Redis中没有RSS订阅信息缓存，尝试更新缓存...")
        
        # 更新Redis缓存
        await update_categories_rss()
        
        # 再次尝试获取
        rss_urls = await RedisUtil.get_key(redis, REDIS_RSS_FEEDS_KEY)
        rss_categories = await RedisUtil.get_key(redis, REDIS_RSS_CATEGORIES_KEY)
        
        # 如果仍然没有，则尝试从数据库直接获取
        if not rss_urls or not rss_categories:
            logger.warning("更新Redis缓存失败，尝试直接从数据库获取...")
            
            # 从数据库中获取带有RSS订阅源的分类
            result = await session.execute(select(NewsCategories).where(NewsCategories.rss_feed_url != None))
            categories_with_rss = result.scalars().all()
            
            if categories_with_rss:
                # 从数据库中构建RSS源列表和分类映射
                rss_urls = [cat.rss_feed_url for cat in categories_with_rss if cat.rss_feed_url]
                rss_categories = {cat.rss_feed_url: cat.category_name for cat in categories_with_rss if cat.rss_feed_url}
                
                logger.info(f"从数据库中获取到 {len(rss_urls)} 个RSS订阅源")
                for cat in categories_with_rss:
                    logger.info(f"  - {cat.category_name} ({cat.category_value}): {cat.rss_feed_url}")
            else:
                # 如果数据库中也没有，则使用配置文件中的默认值
                logger.warning("数据库中没有找到RSS订阅源配置，使用配置文件中的默认值")
                rss_urls = [feed["url"] for feed in settings.RSS_FEEDS]
                rss_categories = {feed["url"]: feed["category"] for feed in settings.RSS_FEEDS}
    else:
        logger.info(f"从Redis缓存中获取到 {len(rss_urls)} 个RSS订阅源")
    
    # 获取最近处理过的新闻哈希值列表（用于去重）
    recent_news_hashes = await RedisUtil.get_key(redis, REDIS_RECENT_NEWS_KEY) or []
    
    # 获取RSS订阅新闻
    rss_items = get_news_from_rss(rss_urls)
    logger.info(f"从RSS源获取到 {len(rss_items)} 条新闻")
    
    # 根据配置的分类覆盖关键词
    for item in rss_items:
        source_url = item.get('url')
        feed_url = None
        
        # 找出这条新闻来自哪个RSS源
        for rss_url in rss_urls:
            if rss_url in item.get('source_feed', ''):
                feed_url = rss_url
                break
        
        # 如果找到对应的RSS源，使用其分类
        if feed_url and feed_url in rss_categories:
            item['category'] = rss_categories[feed_url]
    
    # 获取其他渠道的新闻
    feed_items = process_all_feeds()
    logger.info(f"从Feed获取到 {len(feed_items)} 条新闻")
    
    # 合并所有来源的新闻
    new_items = []
    new_items.extend(rss_items)
    new_items.extend(feed_items)
    
    logger.info(f"获取完毕，总计 {len(new_items)} 条新闻")

    # 用于记录新处理的新闻哈希值
    processed_hashes = []
    # 统计新增和重复的新闻数量
    new_count = 0
    duplicate_count = 0

    for new_item in new_items:
        try:
            title = new_item.get('title')
            url = new_item.get('url')
            
            # 生成新闻的哈希值
            news_hash = generate_news_hash(title, url)
            
            # 检查是否是最近处理过的新闻
            if news_hash in recent_news_hashes:
                logger.info(f"跳过重复新闻(Redis缓存): {title}")
                duplicate_count += 1
                continue
            
            # 检查数据库中是否已存在相同的新闻（基于标题和URL）
            exists = await check_news_exists(session, title, url)
            if exists:
                logger.info(f"跳过重复新闻(数据库): {title}")
                # 将哈希值添加到Redis缓存中，提高下次去重效率
                processed_hashes.append(news_hash)
                duplicate_count += 1
                continue
            
            # 对于RSS新闻，可能已经有摘要内容，可以选择直接使用或获取完整内容
            if 'summary' in new_item and new_item.get('summary'):
                content = new_item.get('summary')
                logger.info(f"使用RSS提供的摘要内容，长度: {len(content)}")
                
                # 如果摘要内容太短，尝试获取完整页面内容
                if len(content) < 100:  # 设置一个合理的阈值
                    logger.info(f"摘要内容太短，尝试获取完整页面内容: {url}")
                    full_content = await get_content_from_page(url)
                    if full_content and len(full_content) > len(content):
                        content = full_content
            else:
                # 对于没有摘要的新闻，获取完整页面内容
                content = await get_content_from_page(url)
            
            if not content:
                logger.warning(f"未能获取到内容: {url}")
                continue

            insert_data = NewsListCreate()
            insert_data.title = title
            insert_data.source_url = url
            insert_data.original_content = content
            insert_data.create_time = int(time.time())
            insert_data.type = new_item.get('keyword') or new_item.get('category', '未分类')

            # 执行插入操作
            result = await create_news_list(session=session, news_list_create=insert_data)  # 确保这是一个异步操作
            if result:
                logger.success(f"数据插入成功！{insert_data.title}")
                # 记录已处理的新闻哈希值
                processed_hashes.append(news_hash)
                new_count += 1
            else:
                logger.error(f"数据插入失败。{insert_data}")
        except Exception as e:
            logger.error(f"处理新闻项目时出错: {e}, URL: {new_item.get('url', 'Unknown URL')}")
    
    # 更新Redis中的最近处理新闻列表
    if processed_hashes:
        # 合并新旧哈希值列表，保留最近的记录（限制数量为1000条）
        all_hashes = processed_hashes + recent_news_hashes
        if len(all_hashes) > 1000:
            all_hashes = all_hashes[:1000]
        
        # 更新Redis缓存
        await RedisUtil.set_key(redis, REDIS_RECENT_NEWS_KEY, all_hashes, expire=REDIS_RECENT_NEWS_EXPIRE)
    
    # 关闭Redis连接
    await redis.close()
    
    logger.info(f"本次处理总结: 新增 {new_count} 条新闻，跳过 {duplicate_count} 条重复新闻")


async def run_collect_data():
    """
    运行数据收集任务 获取邮件+初步html解析
    """
    async with AsyncSessionLocal() as session:
        await collect_data(session)  # 传递 app 实例
        await generate_news(session)



async def generate_news(session: AsyncSession, redis=None):

    if not redis:
        redis = await RedisUtil.create_redis_pool()
    # 这里你需要获取需要处理的数据，可以根据你的逻辑来实现
    platforms_config: dict = await RedisUtil.get_key(redis, 'platforms_config')
    
    # 错误处理：如果Redis中没有配置，使用默认配置
    if not platforms_config:
        logger.warning("Redis中没有找到平台配置，使用默认配置")
        platforms_config = {
            "platform_name": "default_platform",
            "apikey": settings.OPENAI_API_KEY,  # 从环境变量中获取
            "prompt": "1.You are a professional news editor.\n2.Based on the provided link, title, and original content, assess the consistency of the content with the title.\n3.If the original content is consistent with the title, summarize the core content of the article;\n4.If the original content does not match the title, or if it is a page verification like Cloudflare, ignore the original content and base your summary solely on the title.\n5.Using the above rules, generate a new title and rehashed content from the provided title, link, and original content. The new content should be summarized in simplified Chinese and be approximately 350 Chinese characters long.\n6.Ensure the content is concise and accurate, while adhering to the required format. The content should follow the format below:\n标题: xxxx\n内容: xxxx.\n7.Ensure the generated content does not contain words like \"本文\" or \"文章\" or \"**\" or \"#\" and does not include any article links. Summarizing the gist of the article in the conclusion is not allowed.",
            "chat_model": "llama-3.1-70b-versatile",
            "create_time": int(time.time())
        }
    
    new_platforms_config = PlatformConfig(**platforms_config)
    news_items = await get_all_not_generate_news(session)  # 假设有一个方法来获取需要处理的新闻项目

    if not news_items:
        logger.info("No news items to process.")
        return

    openai_processor = OpenAIProcessor(api_key=new_platforms_config.apikey)
    prompt = new_platforms_config.prompt
    model = new_platforms_config.chat_model
    for result in news_items:

        try:
            new_title, summary = openai_processor.request_grop_api(
                prompt,
                title=result.title,
                original_content=result.original_content,
                source_url=result.source_url,
                model=model
            )

        except Exception as e:
            logger.error(f"Error generating content for {result.title}: {e}")
            continue

        if new_title and summary:
            update_data = {
                'processed_title': new_title,
                'processed_content': summary,
                'generated': 1
            }
            try:
                new_result = await update_news_item(session=session, news_item=result, update_data=update_data)
                logger.info(
                    f"Updated news item: {new_result.id or 'Unknown ID'} - {new_result.processed_title or 'Untitled'}")
            except Exception as e:
                logger.error(f"Error updating news item {result.id}: {e}")
                continue
        else:
            logger.warning(f"没有解析出标题: {str(result.title)}")
            continue



if __name__ == '__main__':
    logger.info("开始了")
    # schedule_tasks()
    run_collect_data()