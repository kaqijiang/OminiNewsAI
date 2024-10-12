from typing import Optional

# SQL 语句:
# CREATE TABLE `api_keys` (`id` int(11) NOT NULL AUTO_INCREMENT,`user_id` int(11) NOT NULL,`api_key` varchar(255) NOT NULL COMMENT 'API Key',PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

from sqlmodel import SQLModel, Field

class ApiKeysBase(SQLModel):
    id: int
    user_id: int
    api_key: str

class ApiKeysCreate(ApiKeysBase):
    pass

class ApiKeysUpdate(ApiKeysBase):
    pass

class ApiKeysInDBBase(ApiKeysBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class ApiKeys(ApiKeysInDBBase, table=True):
    __tablename__ = 'api_keys'

