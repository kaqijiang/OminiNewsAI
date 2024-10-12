
from fastapi import APIRouter, Depends
from api.deps import SessionDep, get_current_active_superuser
from api.crud import create_api_keys, get_api_keys_by_id, get_all_api_keyss, update_api_keys, delete_api_keys
from api.models import ApiKeys, ApiKeysCreate, ApiKeysUpdate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ApiKeys])
def read_api_keyss(session: SessionDep, skip: int = 0, limit: int = 10):
    return get_all_api_keyss(session=session, skip=skip, limit=limit)



@router.get("/id", response_model=ApiKeys)
def get_api_keys_by_id(session: SessionDep, id: str):
    return get_api_keys_by_id(session=session, id=id)

@router.post("/", response_model=ApiKeys, dependencies=[Depends(get_current_active_superuser)])
def create_api_keys_endpoint(session: SessionDep, api_keys_data: ApiKeysCreate):
    return create_api_keys(session=session, api_keys_create=api_keys_data)

@router.put("/id", response_model=ApiKeys, dependencies=[Depends(get_current_active_superuser)])
def update_api_keys_endpoint(session: SessionDep, id: str, api_keys_data: ApiKeysUpdate):
    db_api_keys = get_api_keys_by_id(session=session, id=id)
    if db_api_keys:
        return update_api_keys(session=session, db_api_keys=db_api_keys, api_keys_update=api_keys_data)
    return {"message": "ApiKeys not found"}

@router.delete("/id", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
def delete_api_keys_endpoint(session: SessionDep, id: str):
    delete_api_keys(session=session, id=id)
    return {"message": "ApiKeys deleted"}
