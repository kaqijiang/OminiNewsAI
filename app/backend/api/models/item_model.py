from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from api.models.user_model import User

class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)

class ItemCreate(ItemBase):
    title: str = Field(min_length=1, max_length=255)

class ItemUpdate(ItemBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)  # type: ignore

class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id", nullable=False)
    owner: Optional[User] = Relationship(back_populates="items")

class ItemPublic(ItemBase):
    id: int
    owner_id: int

class ItemsPublic(SQLModel):
    data: List[ItemPublic]
    count: int
