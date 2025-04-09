import time
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.crud.platforms_crud import get_platforms_by_user
from api.deps import SessionDep, get_current_active_superuser
from api.crud import create_platforms, get_platforms_by_id, update_platforms
from api.models import PlatformConfig, PlatformConfigUpdate, User

from api.deps import get_redis
from core.get_redis import RedisUtil

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/getByUser", response_model=PlatformConfig, dependencies=[Depends(get_current_active_superuser)])
async def get_platforms_by_ids(session: SessionDep, current_superuser: User = Depends(get_current_active_superuser)):
    try:
        logger.info(f"获取用户 {current_superuser.email} 的平台配置")
        db_platforms = await get_platforms_by_user(session=session, user=current_superuser.email)
        if not db_platforms:
            logger.warning(f"用户 {current_superuser.email} 的平台配置不存在，将创建新配置")
            # 如果没有配置，创建一个基本配置
            platform_create = PlatformConfigUpdate(
                platform_name=current_superuser.email,
                create_time=int(time.time())
            )
            db_platforms = await create_platforms(session=session, platforms_create=platform_create)
            logger.info(f"已为用户 {current_superuser.email} 创建新的平台配置")
        
        logger.info(f"成功获取用户 {current_superuser.email} 的平台配置: {db_platforms}")
        return db_platforms
    except Exception as e:
        logger.error(f"获取平台配置时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取平台配置失败: {str(e)}")

@router.get("/getAll", response_model=PlatformConfig, dependencies=[Depends(get_current_active_superuser)])
async def get_platforms_by_idss(session: SessionDep):
    return get_platforms_by_id(session=session)

@router.post("/updateConfig", response_model=PlatformConfig, dependencies=[Depends(get_current_active_superuser)])
async def update_platforms_endpoint(session: SessionDep, platforms_data: PlatformConfigUpdate, current_superuser: User = Depends(get_current_active_superuser),redis=Depends(get_redis)):

    db_platforms = await get_platforms_by_user(session=session, user=current_superuser.email)
    if db_platforms:
        # 使用 await 调用异步的 update_platforms 函数
        updated_platform = await update_platforms(session=session, db_platforms=db_platforms,
                                                  platforms_update=platforms_data)
    else:
        platforms_data.platform_name = current_superuser.email
        platforms_data.create_time = int(time.time())
        updated_platform = await create_platforms(session=session, platforms_create=platforms_data)

    # 将结果存入 Redis，并设置过期时间（如 3600 秒）
    await RedisUtil.set_key(redis, 'platforms_config', updated_platform, expire= 60 * 60 * 1 * 24 *7)
    return updated_platform

# @router.post("/delete", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
# def delete_platforms_endpoint(session: SessionDep, id: str):
#     delete_platforms(session=session, id=id)
#     return {"message": "Platforms deleted"}
