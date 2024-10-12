from typing import Any, Optional
from sqlmodel import Session, select

from core.security import get_password_hash, verify_password
from api.models.user_model import User, UserUpdate, UserCreate

async def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

async def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)  # 使用 await 进行异步查询
    session_user = result.scalars().first()  # 获取查询结果
    return session_user
# 认证函数
async def authenticate(*, session: Session, email: str, password: str) -> Optional[User]:
    db_user = await get_user_by_email(session=session, email=email)  # 假设 get_user_by_email 是异步的
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):  # 假设 verify_password 是同步的
        return None
    return db_user