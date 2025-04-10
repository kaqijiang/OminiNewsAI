import asyncio
from random import sample
import json

from fastapi import APIRouter, Depends, HTTPException
from api.crud.news_list_crud import update_items_send_status, update_news_item, get_all_news_list
from api.crud.platforms_crud import get_platforms_by_user
from api.deps import get_redis
from api.deps import SessionDep, get_current_active_superuser
from api.crud import get_news_list_by_id, delete_news_list, get_news_by_category, fetch_all_hot_news
from api.models import NewsList, User
from typing import List, Optional

from api.models.news_list_model import DeleteNews
from api.models.platforms_model import PublishNewsRequest, PlatformConfig
from core.get_redis import RedisUtil
from exceptions.handle_sub_applications import get_connection_manager
from tasks.OpenAIProcessor import OpenAIProcessor
from tasks.collect_data import collect_data, generate_news
from utils.WebSocketManager import ConnectionManager
from utils.publisher import Publisher

router = APIRouter()


# Public API

@router.get("/readNewsByCategory")
async def read_news_by_category(
        session: SessionDep,
        category_name: str,
        skip: int = 0,
        limit: int = 20,
        redis=Depends(get_redis)
):
    """根据类别获取内容列表（支持分页）"""
    # 优先从数据库获取总数，并缓存
    total_key = f"news_by_category_total_{category_name}"
    cached_total = await RedisUtil.get_key(redis, total_key)
    
    if cached_total is None:
        # 如果总数不存在，从数据库获取总数
        total = await get_news_count_by_category(session=session, name=category_name)
        await RedisUtil.set_key(redis, total_key, total, expire=3600)
    else:
        total = cached_total
    
    # 生成当前分页的缓存键
    page_key = f"news_by_category_{category_name}_{skip}_{limit}"
    
    # 尝试从Redis获取当前分页数据
    cached_page = await RedisUtil.get_key(redis, page_key)
    
    if cached_page is not None:
        # 如果缓存存在，直接返回
        return {
            "data": cached_page,
            "total": total
        }
    
    # 缓存不存在，从数据库获取当前分页数据
    news_items = await get_news_by_category(session=session, name=category_name, skip=skip, limit=limit)
    
    # 缓存当前分页数据，设置较短的过期时间
    await RedisUtil.set_key(redis, page_key, news_items, expire=300)  # 5分钟过期
    
    return {
        "data": news_items,
        "total": total
    }


@router.get("/hotNewsItems")
async def get_hot_news_list(session: SessionDep, redis=Depends(get_redis)):
    """获取随机10条热搜"""
    # 生成缓存的键，包含类别名、页码（skip）和每页数量（limit）
    cache_key = f"hot_news_30"

    # 尝试从 Redis 中获取缓存数据
    cached_news = await RedisUtil.get_key(redis, cache_key)
    if cached_news:
        return sample(cached_news, min(len(cached_news), 10))

    # 如果缓存不存在，从数据库获取数据
    news_list = await fetch_all_hot_news(session=session, limit=30)

    # 将结果存入 Redis，并设置过期时间（如 300 秒）
    await RedisUtil.set_key(redis, cache_key, news_list, expire=5 * 60)

    # 随机选取10条资讯
    return sample(news_list, min(len(news_list), 10))


# 登录后接口
@router.get("/aiList", response_model=List[NewsList])
async def get_ai_news_list(session: SessionDep, skip: int = 0, limit: int = 100):
    """"AI资讯列表"""
    return await get_news_by_category(session=session, skip=skip, limit=limit, name='AI资讯')


@router.get("/carList", response_model=List[NewsList])
async def get_car_news_list(session: SessionDep, skip: int = 0, limit: int = 100):
    """"汽车资讯列表"""
    return await get_news_by_category(session=session, skip=skip, limit=limit, name='汽车资讯')

@router.get("/allList", response_model=List[NewsList])
async def get_all_news_list_endpoint(session: SessionDep, skip: int = 0, limit: int = 2000, name:Optional[str] = None):
    """"汽车资讯列表"""
    return await get_all_news_list(session=session, skip=skip, limit=limit, name=name)
@router.get("/getLatestNews")
async def fetch_latest_news(session: SessionDep, skip: int = 0, limit: int = 100):
    """"获取最新资讯"""
    await collect_data(session)

    return {"message": "获取成功"}


@router.get("/generateNews")
async def gen_news_items(session: SessionDep, skip: int = 0, limit: int = 100,redis=Depends(get_redis)):
    """"生成资讯"""
    # 4.生成资讯
    await generate_news(session, redis)
    return {"message": "生成成功"}


@router.get("/id", response_model=NewsList)
async def get_news_list_by_id_endpoint(session: SessionDep, id: str):
    """ 获取新闻 """
    return await get_news_list_by_id(session=session, id=id)


@router.get("/updateNews", response_model=NewsList)
async def updateNews_news_list_by_id_endpoint(session: SessionDep, id: str, redis=Depends(get_redis)):
    """ 获取新闻 """

    platforms_config: dict = await RedisUtil.get_key(redis, 'platforms_config')
    new_platforms_config = PlatformConfig(**platforms_config)

    news_item = await get_news_list_by_id(session=session, id=id)
    if not news_item:
        raise HTTPException(status_code=404, detail="找不到新闻项目")

    # 请求 OpenAI API 接口总结资讯
    openai_processor = OpenAIProcessor(api_key=new_platforms_config.apikey)
    prompt = new_platforms_config.prompt
    model = new_platforms_config.chat_model
    new_title, summary = openai_processor.request_grop_api(prompt=prompt, title=news_item.title,
                                                           source_url=news_item.source_url,
                                                           original_content=news_item.original_content,model=model)
    if new_title and summary:
        update_data = {
            'processed_title': new_title,
            'processed_content': summary,
            'generated': 1
        }
    # 更新数据库中的新闻项目
    new_result = await update_news_item(session=session, news_item=news_item, update_data=update_data)

    return new_result


@router.post("/delete", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
async def delete_news_list_endpoint(session: SessionDep, deleteNews: DeleteNews):
    """ 删除 ids """

    await delete_news_list(session=session, ids=deleteNews.ids)
    return {"message": "NewsList deleted"}


@router.post("/publish", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
async def publish_news_endpoint(session: SessionDep, news_request: PublishNewsRequest,
                                current_superuser: User = Depends(get_current_active_superuser),
                                manager: ConnectionManager = Depends(get_connection_manager)):
    """ 推送 news_ids """

    news_ids = news_request.news_ids
    platforms = news_request.platforms
    type = news_request.type
    if not type:
        type = '综合资讯'
    selected_news = []
    for index, news_id in enumerate(news_ids):
        news_item = await get_news_list_by_id(session=session, id=news_id)
        if not news_item:
            raise HTTPException(status_code=404, detail=f"找不到ID为{news_id}的新闻项目")
        selected_news.append((str(index + 1) + '.' + news_item.processed_title, news_item.processed_content))

    # 获取平台配置信息
    platform_configs = await get_platforms_by_user(session=session, user=current_superuser.email)
    publisher_manager = Publisher(platform_configs)

    results = {}
    for platform in platforms:
        try:
            await manager.send_message(f"{platform}: 正在发布")
            isok, msg = await publish_to_platform(platform, publisher_manager, selected_news, type)
            if isok:
                await manager.send_message(f"{platform}: 成功")
                results[platform] = "成功"
            else:
                await manager.send_message(f"{platform}: 失败=> {msg}")
                results[platform] = "失败"
            await asyncio.sleep(1)  # 增加1秒延迟
        except Exception as e:
            results[platform] = "失败"
            await manager.send_message(f"{platform}: 失败: {e}")

    # 更新状态
    await update_items_send_status(session=session, news_item_ids=news_ids)

    return results


async def publish_to_platform(platform, publisher_manager, selected_news, type):
    """根据平台发布内容"""
    if platform == "微信":
        return publisher_manager.post_to_wechat(selected_news, type)
    elif platform == "知识星球":
        return publisher_manager.post_to_xing_qiu(selected_news, type)
    elif platform == "掘金":
        return publisher_manager.post_to_jue_jin(selected_news, type)
    elif platform == "知乎":
        return publisher_manager.post_to_zhi_hu(selected_news, type)
    else:
        return False, f"未知平台: {platform}"
