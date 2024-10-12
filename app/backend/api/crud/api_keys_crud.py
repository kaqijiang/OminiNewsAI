
from typing import List, Optional, Any
from sqlmodel import Session, select
from api.models import ApiKeys, ApiKeysCreate, ApiKeysUpdate

def create_api_keys(*, session: Session, api_keys_create: ApiKeysCreate) -> ApiKeys:
    db_obj = ApiKeys.from_orm(api_keys_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_api_keys_by_id(*, session: Session, id: Any) -> Optional[ApiKeys]:
    statement = select(ApiKeys).where(ApiKeys.id == id)
    return session.exec(statement).first()

def get_all_api_keyss(*, session: Session, skip: int = 0, limit: int = 10) -> List[ApiKeys]:
    statement = select(ApiKeys).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_api_keys(*, session: Session, db_api_keys: ApiKeys, api_keys_update: ApiKeysUpdate) -> ApiKeys:
    update_data = api_keys_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_api_keys, key, value)
    session.add(db_api_keys)
    session.commit()
    session.refresh(db_api_keys)
    return db_api_keys

def delete_api_keys(*, session: Session, id: Any) -> None:
    db_obj = get_api_keys_by_id(session=session, id=id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
