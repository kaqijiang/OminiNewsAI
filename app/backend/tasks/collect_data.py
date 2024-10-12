import time

from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger

from api.crud.news_list_crud import get_all_not_generate_news, update_news_item, create_news_list
from api.models import PlatformConfig, NewsListCreate
from core.config import settings
from core.db import AsyncSessionLocal
from core.get_redis import RedisUtil
from tasks.OpenAIProcessor import OpenAIProcessor
from tasks.get_news import process_all_feeds
from utils.email_manager import get_new_email
from utils.nodriver_parse import get_content_from_page


async def collect_data(session: AsyncSession):
    """
    从邮件中收集数据并插入数据库，然后请求 OpenAI API 进行总结
    """
    logger.info("自动获取信息中")
    username = settings.EMAIL_USERNAME
    password = settings.EMAIL_PASSWORD
    # new_items = get_new_email(username, password, num_emails=100)
    new_items = process_all_feeds()
    logger.info(f"获取完毕{len(new_items)}")

    for new_item in new_items:
        try:
            url = new_item.get('url')
            content = await get_content_from_page(url)

            insert_data = NewsListCreate()
            insert_data.title = new_item.get('title')
            insert_data.source_url = url
            insert_data.original_content = content
            insert_data.create_time = int(time.time())
            insert_data.type = new_item.get('keyword')

            # 执行插入操作
            result = await create_news_list(session=session, news_list_create=insert_data)  # 确保这是一个异步操作
            if result:
                logger.success("数据插入成功！")
            else:
                logger.error(f"数据插入失败。{insert_data}")
        except Exception as e:
            logger.error(e)


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
