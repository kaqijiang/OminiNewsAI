from datetime import datetime, timedelta
from random import sample
from typing import List, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from api.models import NewsList, NewsListCreate, NewsListUpdate, NewsCategories


async def get_all_not_generate_news(session: AsyncSession) -> list[NewsList]:
    # 计算昨天午夜的 Unix 时间戳
    yesterday_midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    yesterday_midnight_timestamp = int(yesterday_midnight.timestamp())

    # 构建查询
    query = (
        select(NewsList)
        .where(
            NewsList.generated == 0,
            NewsList.create_time >= yesterday_midnight_timestamp
        )
    )

    # 执行查询并获取结果
    result = await session.execute(query)
    news_items = result.scalars().all()  # 确保获取的是一个列表

    return news_items

async def check_news_exists(session: AsyncSession, title: str, url: str) -> bool:
    """
    检查给定标题和URL的新闻是否已存在于数据库中
    
    Args:
        session: 数据库会话
        title: 新闻标题
        url: 新闻URL
    
    Returns:
        bool: 如果新闻已存在返回True，否则返回False
    """
    # 构建查询，先检查URL（更精确）
    query = select(NewsList).where(NewsList.source_url == url)
    result = await session.execute(query)
    news_item = result.scalars().first()
    
    # 如果URL匹配则直接返回True
    if news_item:
        return True
    
    # 否则检查标题是否匹配
    query = select(NewsList).where(NewsList.title == title)
    result = await session.execute(query)
    news_item = result.scalars().first()
    
    return news_item is not None

async def create_news_list(session: AsyncSession, news_list_create: NewsListCreate) -> NewsList:
    db_obj = NewsList.from_orm(news_list_create)
    session.add(db_obj)     # 构建插入的SQL语句
    await session.commit()  # 使用 await 等待异步提交
    await session.refresh(db_obj)  # 使用 await 等待异步刷新
    return db_obj

async def get_news_list_by_id(*, session: AsyncSession, id: Any) -> Optional[NewsList]:
    statement = select(NewsList).where(NewsList.id == id)
    result = await session.execute(statement)

    return result.scalars().first()
async def get_news_lists_by_ids(*, session: AsyncSession, ids: list[int]) -> list[NewsList]:
    """" 获取新闻 根据ids """
    statement = select(NewsList).where(NewsList.id.in_(ids))
    result = await session.execute(statement)
    return result.scalars().all()

async def update_news_list(*, session: AsyncSession, db_news_list: NewsList, news_list_update: NewsListUpdate) -> NewsList:
    update_data = news_list_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_news_list, key, value)
    session.add(db_news_list)
    await session.commit()
    await session.refresh(db_news_list)
    return db_news_list

async def update_news_item(session: AsyncSession, news_item: NewsList, update_data: dict):
    for key, value in update_data.items():
        setattr(news_item, key, value)
    session.add(news_item)
    await session.commit()  # 使用 await 进行异步提交
    await session.refresh(news_item)  # 使用 await 进行异步刷新
    return news_item

async def delete_news_list(*, session: AsyncSession, ids: List[int]) -> None:
    db_objs = await get_news_lists_by_ids(session=session, ids=ids)
    for db_obj in db_objs:
        await session.delete(db_obj)
    await session.commit()

async def update_items_send_status(*, session: AsyncSession, news_item_ids: List[int]) -> int:
    # 查询需要更新的记录
    statement = select(NewsList).where(NewsList.id.in_(news_item_ids))
    result = await session.execute(statement)
    news_items = result.scalars().all()

    # 更新每条记录的 send 状态
    for item in news_items:
        item.send = 1  # 设置 send 状态为 1

    # 提交事务
    await session.commit()

    # 返回更新的记录数
    return len(news_items)


async def get_all_news_list(*, session: AsyncSession, name: Optional[str] = None, skip: int = 0, limit: int = 100) -> \
List[NewsList]:
    """获取资讯列表，根据类别或全部"""

    # 计算昨天午夜的 Unix 时间戳
    yesterday_midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    yesterday_midnight_timestamp = int(yesterday_midnight.timestamp())

    # 如果 name 有值，则构建类别子查询
    if name:
        category_subquery = (
            select(NewsCategories.category_value)
            .filter(NewsCategories.category_name == name)
            .subquery()
        )

        # 主查询：获取符合条件的 NewsList，按类别筛选
        query = (
            select(NewsList)
            .where(
                NewsList.type.in_(category_subquery),
                NewsList.generated == 1,
                NewsList.create_time >= yesterday_midnight_timestamp
            )
            .order_by(desc(NewsList.id))
            .offset(skip)
            .limit(limit)
        )
    else:
        # 如果 name 为空，查询全部类型的资讯
        query = (
            select(NewsList)
            .where(
                NewsList.generated == 1,
                NewsList.create_time >= yesterday_midnight_timestamp
            )
            .order_by(desc(NewsList.id))
            .offset(skip)
            .limit(limit)
        )

    # 执行查询并获取结果
    result = await session.execute(query)
    news_items = result.scalars().all()

    return news_items


async def get_news_by_category(*, session: AsyncSession, name: str, skip: int = 0, limit: int = 100) -> List[NewsList]:
    """通过类别获取资讯"""
    # 计算昨天午夜的 Unix 时间戳
    yesterday_midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    yesterday_midnight_timestamp = int(yesterday_midnight.timestamp())

    # 子查询：根据 category_name 获取 category_value
    category_subquery = (
        select(NewsCategories.category_value)
        .filter(NewsCategories.category_name == name)
        .subquery()
    )

    # 主查询：获取符合条件的 NewsList
    query = (
        select(NewsList)
        .where(
            NewsList.type.in_(category_subquery),
            NewsList.generated == 1,
            NewsList.create_time >= yesterday_midnight_timestamp
        )
        .order_by(desc(NewsList.id))
        .offset(skip)
        .limit(limit)
    )

    # 执行查询并获取结果
    result = await session.execute(query)
    news_items = result.scalars().all()

    return news_items

async def fetch_all_hot_news(*, session: AsyncSession, limit: int = 10) -> List[NewsList]:
    # 计算昨天午夜的 Unix 时间戳
    yesterday_midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    yesterday_midnight_timestamp = int(yesterday_midnight.timestamp())

    # 查询昨天和今天生成的所有新闻
    query = (
        select(NewsList)
        .where(
            NewsList.generated == 1,
            NewsList.create_time >= yesterday_midnight_timestamp
        )
        .order_by(desc(NewsList.id))
    )

    # 执行查询并获取结果
    result = await session.execute(query)
    news_items = result.scalars().all()

    # 随机选取指定数量（默认10条）的资讯
    if len(news_items) > limit:
        news_items = sample(news_items, limit)

    return news_items