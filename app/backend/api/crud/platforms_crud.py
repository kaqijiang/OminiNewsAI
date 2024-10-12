from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.models import PlatformConfig
from api.models.platforms_model import PlatformConfigUpdate, PlatformConfigInDBBase


# 创建平台配置
async def create_platforms(*, session: AsyncSession, platforms_create: PlatformConfigUpdate) -> PlatformConfig:
    db_obj = PlatformConfig.from_orm(platforms_create)
    session.add(db_obj)
    # 异步提交事务
    await session.commit()
    # 异步刷新对象
    await session.refresh(db_obj)
    return db_obj

# 根据 ID 获取平台配置
async def get_platforms_by_id(*, session: AsyncSession, id: Any) -> Optional[PlatformConfig]:
    statement = select(PlatformConfig).where(PlatformConfig.id == id)
    # 异步执行查询
    result = await session.execute(statement)
    # 获取查询结果的第一条记录
    return result.scalars().first()

# 根据用户名获取平台配置
async def get_platforms_by_user(*, session: AsyncSession, user: str) -> Optional[PlatformConfig]:
    statement = select(PlatformConfig).where(PlatformConfig.platform_name == user)
    # 异步执行查询
    result = await session.execute(statement)
    # 获取查询结果的第一条记录
    return result.scalars().first()

# 获取所有平台配置，支持分页
async def get_all_platformss(*, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[PlatformConfig]:
    statement = select(PlatformConfig).offset(skip).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()

# 更新平台配置
async def update_platforms(*, session: AsyncSession, db_platforms: PlatformConfigInDBBase, platforms_update: PlatformConfigUpdate) -> PlatformConfig:
    # 只更新传入的数据，未传入的保持原值
    update_data = platforms_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_platforms, key, value)

    session.add(db_platforms)
    # 异步提交事务
    await session.commit()
    # 异步刷新对象并返回
    await session.refresh(db_platforms)
    return db_platforms

# 删除平台配置
async def delete_platforms(*, session: AsyncSession, id: Any) -> None:
    db_obj = await get_platforms_by_id(session=session, id=id)  # 异步获取平台配置
    if db_obj:
        await session.delete(db_obj)  # 异步删除对象
        # 异步提交事务
        await session.commit()
