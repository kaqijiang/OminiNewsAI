import time

from fastapi import APIRouter, Depends

from api.crud.platforms_crud import get_platforms_by_user
from api.deps import SessionDep, get_current_active_superuser
from api.crud import create_platforms, get_platforms_by_id, update_platforms
from api.models import PlatformConfig, PlatformConfigUpdate, User

from api.deps import get_redis
from core.get_redis import RedisUtil
router = APIRouter()
@router.get("/getByUser", response_model=PlatformConfig, dependencies=[Depends(get_current_active_superuser)])
async def get_platforms_by_ids(session: SessionDep, current_superuser: User = Depends(get_current_active_superuser)):
    db_platforms = await get_platforms_by_user(session=session, user=current_superuser.email)
    return db_platforms

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
