from typing import Optional

# SQL 语句:
# CREATE TABLE `publish_history` (`id` int(11) NOT NULL AUTO_INCREMENT,`user_id` int(11) NOT NULL,`news_id` int(11) NOT NULL,`publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',PRIMARY KEY (`id`),FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY (`news_id`) REFERENCES `news_list` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

from sqlmodel import SQLModel, Field

class PublishHistoryBase(SQLModel):
    id: int
    user_id: int
    news_id: int
    publish_time: str = Field(nullable=False)

class PublishHistoryCreate(PublishHistoryBase):
    pass

class PublishHistoryUpdate(PublishHistoryBase):
    pass

class PublishHistoryInDBBase(PublishHistoryBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class PublishHistory(PublishHistoryInDBBase, table=True):
    __tablename__ = 'publish_history'

