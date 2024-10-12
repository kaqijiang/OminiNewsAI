
from fastapi import APIRouter, Depends

from api.deps import get_redis, get_current_active_superuser
from api.deps import SessionDep
from api.crud import create_news_categories, get_news_categories_by_id, get_all_news_categoriess, update_news_categories, delete_news_categories, get_category_list
from api.models import NewsCategories, NewsCategoriesCreate, NewsCategoriesUpdate
from typing import List

from core.get_redis import RedisUtil

router = APIRouter()

@router.get("/all", response_model=List[NewsCategories])
async def read_news_categoriess(session: SessionDep, skip: int = 0, limit: int = 100):
    return await get_all_news_categoriess(session=session, skip=skip, limit=limit)

@router.post("/", response_model=NewsCategories)
def create_news_categories_endpoint(session: SessionDep, news_categories_data: NewsCategoriesCreate):
    return create_news_categories(session=session, news_categories_create=news_categories_data)

@router.get("/id", response_model=NewsCategories)
def get_news_categories_by_id(session: SessionDep, id: str):
    return get_news_categories_by_id(session=session, id=id)

@router.put("/id", response_model=NewsCategories, dependencies=[Depends(get_current_active_superuser)])
def update_news_categories_endpoint(session: SessionDep, id: str, news_categories_data: NewsCategoriesUpdate):
    db_news_categories = get_news_categories_by_id(session=session, id=id)
    if db_news_categories:
        return update_news_categories(session=session, db_news_categories=db_news_categories, news_categories_update=news_categories_data)
    return {"message": "NewsCategories not found"}

@router.delete("/id", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
def delete_news_categories_endpoint(session: SessionDep, id: str):
    delete_news_categories(session=session, id=id)
    return {"message": "NewsCategories deleted"}

@router.get("/list")
async def get_categorys_list(session: SessionDep, redis=Depends(get_redis)):
    """
    获取新闻项目，首先检查Redis缓存，如果没有则查询数据库。
    """
    cache_key = "category_list"

    # 尝试从 Redis 获取缓存
    cached_news = await RedisUtil.get_key(redis, cache_key)
    if cached_news:
        # 如果缓存存在，返回缓存内容
        return {"news_items": cached_news}

    # 如果缓存不存在，从数据库获取
    news_list = await get_category_list(session=session)  # 您的数据库查询逻辑
    # 假设 `news_list` 是可序列化的
    await RedisUtil.set_key(redis, cache_key, news_list, expire= 1 * 60 * 60)  # 将查询结果缓存，过期时间为 3600 秒

    return {"news_items": news_list}