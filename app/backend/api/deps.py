from collections.abc import AsyncGenerator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import security
from core.config import settings
from api.models import TokenPayload, User
from core.db import AsyncSessionLocal

# 可重用的 OAuth2 密码流，tokenUrl 用于获取访问令牌
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# 数据库会话生成器，用于获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as current_db:
        yield current_db

def get_redis(request: Request):
    return request.app.state.redis

# 数据库会话依赖注入类型别名
SessionDep = Annotated[AsyncSession, Depends(get_db)]
# 访问令牌依赖注入类型别名
TokenDep = Annotated[str, Depends(reusable_oauth2)]

# 获取当前用户的函数
async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # 直接使用 session 来执行查询
    result = await session.execute(select(User).filter_by(id=token_data.sub))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

# 当前用户依赖注入类型别名
CurrentUser = Annotated[User, Depends(get_current_user)]

# 获取当前活跃超级用户的函数
def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
