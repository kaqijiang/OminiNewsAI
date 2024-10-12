import os
import re
from typing import Dict, Tuple
from utils.logging_config import LogManager

# 获取单例日志记录器实例
logger = LogManager().get_logger()

def parse_sql_table(sql: str) -> Tuple[str, Dict[str, str], str]:
    table_name_match = re.search(r'CREATE TABLE `(\w+)`', sql)
    if not table_name_match:
        logger.error("无法解析表名")
        raise ValueError("无法解析表名")
    table_name = table_name_match.group(1)
    logger.info(f"解析到的表名: {table_name}")

    fields_matches = re.findall(r'`(\w+)` (\w+)(.*?)[,\)]', sql)
    fields = {}
    primary_key = None
    for field_name, field_type, field_constraints in fields_matches:
        column_type = ""
        if field_type.lower() in ["varchar", "char", "text"]:
            column_type = "str"
        elif field_type.lower() in ["int", "integer"]:
            column_type = "int"
        elif field_type.lower() in ["float", "double"]:
            column_type = "float"
        elif field_type.lower() in ["boolean", "bool"]:
            column_type = "bool"
        else:
            column_type = "str"

        constraints = []
        if "PRIMARY KEY" in field_constraints:
            constraints.append("primary_key=True")
            primary_key = field_name
        if "NOT NULL" in field_constraints:
            constraints.append("nullable=False")

        if constraints:
            fields[field_name] = f"{column_type} = Field({', '.join(constraints)})"
        else:
            fields[field_name] = column_type

    if primary_key is None:
        primary_key = next(iter(fields))

    return table_name, fields, primary_key
def generate_sqlmodel(table_name: str, fields: Dict[str, str], sql: str) -> Tuple[str, str]:
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    fields_str = "\n".join([f'    {name}: {type_}' for name, type_ in fields.items()])
    model = f"""
from typing import Optional
from sqlmodel import SQLModel, Field

# SQL 语句:
# {sql}

class {class_name}Base(SQLModel):
{fields_str}

class {class_name}Create({class_name}Base):
    pass

class {class_name}Update({class_name}Base):
    pass

class {class_name}InDBBase({class_name}Base):
    id: Optional[int] = Field(default=None, primary_key=True)

class {class_name}({class_name}InDBBase, table=True):
    __tablename__ = '{table_name}'

"""
    model_init = f"from .{table_name}_model import {class_name}, {class_name}Create, {class_name}Update"
    return model, model_init
def generate_crud(table_name: str, primary_key: str) -> Tuple[str, str]:
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    crud = f"""
from typing import List, Optional, Any
from sqlmodel import Session, select
from app.api.models import {class_name}, {class_name}Create, {class_name}Update

def create_{table_name}(*, session: Session, {table_name}_create: {class_name}Create) -> {class_name}:
    db_obj = {class_name}.from_orm({table_name}_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_{table_name}_by_{primary_key}(*, session: Session, {primary_key}: Any) -> Optional[{class_name}]:
    statement = select({class_name}).where({class_name}.{primary_key} == {primary_key})
    return session.exec(statement).first()

def get_all_{table_name}s(*, session: Session, skip: int = 0, limit: int = 10) -> List[{class_name}]:
    statement = select({class_name}).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_{table_name}(*, session: Session, db_{table_name}: {class_name}, {table_name}_update: {class_name}Update) -> {class_name}:
    update_data = {table_name}_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_{table_name}, key, value)
    session.add(db_{table_name})
    session.commit()
    session.refresh(db_{table_name})
    return db_{table_name}

def delete_{table_name}(*, session: Session, {primary_key}: Any) -> None:
    db_obj = get_{table_name}_by_{primary_key}(session=session, {primary_key}={primary_key})
    if db_obj:
        session.delete(db_obj)
        session.commit()
"""
    crud_init = f"from .{table_name}_crud import create_{table_name}, get_{table_name}_by_{primary_key}, get_all_{table_name}s, update_{table_name}, delete_{table_name}"
    return crud, crud_init
def generate_router(table_name: str, primary_key: str) -> str:
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    router_code = f"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.api.deps import SessionDep
from app.api.crud import create_{table_name}, get_{table_name}_by_{primary_key}, get_all_{table_name}s, update_{table_name}, delete_{table_name}
from app.api.models import {class_name}, {class_name}Create, {class_name}Update
from typing import List

router = APIRouter()

@router.get("/", response_model=List[{class_name}])
def read_{table_name}s(session: SessionDep, skip: int = 0, limit: int = 10):
    return get_all_{table_name}s(session=session, skip=skip, limit=limit)

@router.post("/", response_model={class_name})
def create_{table_name}_endpoint(session: SessionDep, {table_name}_data: {class_name}Create):
    return create_{table_name}(session=session, {table_name}_create={table_name}_data)

@router.get("/{primary_key}", response_model={class_name})
def get_{table_name}_by_id(session: SessionDep, {primary_key}: str):
    return get_{table_name}_by_{primary_key}(session=session, {primary_key}={primary_key})

@router.put("/{primary_key}", response_model={class_name})
def update_{table_name}_endpoint(session: SessionDep, {primary_key}: str, {table_name}_data: {class_name}Update):
    db_{table_name} = get_{table_name}_by_{primary_key}(session=session, {primary_key}={primary_key})
    if db_{table_name}:
        return update_{table_name}(session=session, db_{table_name}=db_{table_name}, {table_name}_update={table_name}_data)
    return {{"message": "{class_name} not found"}}

@router.delete("/{primary_key}", response_model=dict)
def delete_{table_name}_endpoint(session: SessionDep, {primary_key}: str):
    delete_{table_name}(session=session, {primary_key}={primary_key})
    return {{"message": "{class_name} deleted"}}
"""
    return router_code


def write_file(directory, filename, content, import_str):
    """检查目录存在并写入文件。如果目录不存在，抛出错误。"""
    # 断言目录存在
    assert os.path.exists(directory), f"目录不存在：{directory}"

    # 文件全路径
    file_path = os.path.join(directory, filename)
    # 写入文件
    with open(file_path, "w") as file:
        file.write(content)
    logger.info(f"文件已成功写入：{file_path}")

    if import_str:
        update_init_file(directory, import_str)

def update_init_file(directory, import_str):
    """在指定目录的 __init__.py 文件中添加新模块的引用。"""
    init_file_path = os.path.join(directory, '__init__.py')
    with open(init_file_path, 'a') as init_file:
        init_file.write(f"{import_str}\n")
def main():
    sql = input("请输入创建表的SQL语句：")
    logger.info(f"输入的SQL语句: {sql}")
    table_name, fields, primary_key = parse_sql_table(sql)

    sqlalchemy_model, model_init = generate_sqlmodel(table_name, fields, sql)
    crud_operations, crud_init = generate_crud(table_name, primary_key)
    router_code = generate_router(table_name, primary_key)

    # 为模型、CRUD、路由器指定目录
    model_directory = os.path.abspath(os.path.join(os.getcwd(), "../api/models"))
    crud_directory = os.path.abspath(os.path.join(os.getcwd(), "../api/crud"))
    router_directory = os.path.abspath(os.path.join(os.getcwd(), "../api/routers"))

    # 保存模型、CRUD操作和路由器代码
    write_file(model_directory, f"{table_name}_model.py", sqlalchemy_model, model_init)
    write_file(crud_directory, f"{table_name}_crud.py", crud_operations, crud_init)
    write_file(router_directory, f"{table_name}.py", router_code, None)

    logger.info(f"已生成 {table_name}_model.py, {table_name}_crud.py, {table_name}.py")

if __name__ == "__main__":
    main()
