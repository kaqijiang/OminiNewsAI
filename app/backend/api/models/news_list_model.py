from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class NewsListBase(SQLModel):
    original_title: Optional[str] = Field(default=None, max_length=550)
    processed_title: Optional[str] = Field(default=None, max_length=550)
    original_content: Optional[str] = None
    processed_content: Optional[str] = None
    source_url: Optional[str] = Field(default=None, max_length=550)
    rss_entry_id: Optional[str] = Field(default=None, max_length=255, index=True)
    create_time: int = Field(default=0)
    type: Optional[str] = Field(default=None, max_length=550)
    generated: int = Field(default=0)
    send: int = Field(default=0)

class NewsListCreate(NewsListBase):
    pass

class NewsListUpdate(NewsListBase):
    pass

class NewsListInDBBase(NewsListBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class NewsList(NewsListInDBBase, table=True):
    __tablename__ = 'news_list'


class DeleteNews(BaseModel):
    ids: List[int]  # 确保 ids 是一个整数列表
