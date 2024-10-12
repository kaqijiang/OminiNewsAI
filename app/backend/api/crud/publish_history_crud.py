
from typing import List, Optional, Any
from sqlmodel import Session, select
from api.models import PublishHistory, PublishHistoryCreate, PublishHistoryUpdate

def create_publish_history(*, session: Session, publish_history_create: PublishHistoryCreate) -> PublishHistory:
    db_obj = PublishHistory.from_orm(publish_history_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_publish_history_by_id(*, session: Session, id: Any) -> Optional[PublishHistory]:
    statement = select(PublishHistory).where(PublishHistory.id == id)
    return session.exec(statement).first()

def get_all_publish_historys(*, session: Session, skip: int = 0, limit: int = 10) -> List[PublishHistory]:
    statement = select(PublishHistory).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_publish_history(*, session: Session, db_publish_history: PublishHistory, publish_history_update: PublishHistoryUpdate) -> PublishHistory:
    update_data = publish_history_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_publish_history, key, value)
    session.add(db_publish_history)
    session.commit()
    session.refresh(db_publish_history)
    return db_publish_history

def delete_publish_history(*, session: Session, id: Any) -> None:
    db_obj = get_publish_history_by_id(session=session, id=id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
