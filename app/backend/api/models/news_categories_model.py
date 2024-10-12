from typing import Optional

# SQL 语句:
# CREATE TABLE `news_categories` (`id` int(11) NOT NULL AUTO_INCREMENT,`category_name` varchar(25) NOT NULL,`category_value` varchar(100) NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4;

from sqlmodel import SQLModel, Field

class NewsCategoriesBase(SQLModel):
    id: int
    category_name: str
    category_value: str

class NewsCategoriesCreate(NewsCategoriesBase):
    pass

class NewsCategoriesUpdate(NewsCategoriesBase):
    pass

class NewsCategoriesInDBBase(NewsCategoriesBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class NewsCategories(NewsCategoriesInDBBase, table=True):
    __tablename__ = 'news_categories'

