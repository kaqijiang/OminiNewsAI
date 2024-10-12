
from fastapi import APIRouter, Depends
from api.deps import SessionDep, get_current_active_superuser
from api.crud import create_publish_history, get_publish_history_by_id, get_all_publish_historys, update_publish_history, delete_publish_history
from api.models import PublishHistory, PublishHistoryCreate, PublishHistoryUpdate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[PublishHistory])
def read_publish_historys(session: SessionDep, skip: int = 0, limit: int = 10):
    return get_all_publish_historys(session=session, skip=skip, limit=limit)

@router.post("/", response_model=PublishHistory)
def create_publish_history_endpoint(session: SessionDep, publish_history_data: PublishHistoryCreate):
    return create_publish_history(session=session, publish_history_create=publish_history_data)

@router.get("/id", response_model=PublishHistory)
def get_publish_history_by_id(session: SessionDep, id: str):
    return get_publish_history_by_id(session=session, id=id)

@router.put("/id", response_model=PublishHistory, dependencies=[Depends(get_current_active_superuser)])
def update_publish_history_endpoint(session: SessionDep, id: str, publish_history_data: PublishHistoryUpdate):
    db_publish_history = get_publish_history_by_id(session=session, id=id)
    if db_publish_history:
        return update_publish_history(session=session, db_publish_history=db_publish_history, publish_history_update=publish_history_data)
    return {"message": "PublishHistory not found"}

@router.delete("/id", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
def delete_publish_history_endpoint(session: SessionDep, id: str):
    delete_publish_history(session=session, id=id)
    return {"message": "PublishHistory deleted"}
