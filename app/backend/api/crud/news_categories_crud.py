
from typing import List, Optional, Any
from sqlmodel import Session, select
from api.models import NewsCategories, NewsCategoriesCreate, NewsCategoriesUpdate

def create_news_categories(*, session: Session, news_categories_create: NewsCategoriesCreate) -> NewsCategories:
    db_obj = NewsCategories.from_orm(news_categories_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_news_categories_by_id(*, session: Session, id: Any) -> Optional[NewsCategories]:
    statement = select(NewsCategories).where(NewsCategories.id == id)
    return session.exec(statement).first()

async def get_all_news_categoriess(*, session: Session, skip: int = 0, limit: int = 10) -> List[NewsCategories]:
    statement = select(NewsCategories).offset(skip).limit(limit)
    results = await session.execute(statement)

    category_list = results.scalars().all()  # scalars() 提取单一列的数据
    return category_list

async def get_category_list(*, session: Session) -> List[NewsCategories]:
    """ 获取分类列表 """
    # 使用 SQLModel 的 select 语句和 distinct() 方法
    statement = select(NewsCategories.category_name).distinct()
    # 执行查询，注意这里需要使用 await
    results = await session.execute(statement)

    category_list = results.scalars().all()  # scalars() 提取单一列的数据
    return category_list

def update_news_categories(*, session: Session, db_news_categories: NewsCategories, news_categories_update: NewsCategoriesUpdate) -> NewsCategories:
    update_data = news_categories_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_news_categories, key, value)
    session.add(db_news_categories)
    session.commit()
    session.refresh(db_news_categories)
    return db_news_categories

def delete_news_categories(*, session: Session, id: Any) -> None:
    db_obj = get_news_categories_by_id(session=session, id=id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
