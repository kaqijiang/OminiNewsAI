from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class PlatformConfigBase(SQLModel):
    platform_name: Optional[str] = Field(default=None, max_length=100, description="平台名称，如 wechat, xing_qiu, jue_jin, zhi_hu")
    wechat_appid: Optional[str] = Field(default=None, max_length=200, description="微信 AppID")
    wechat_secret: Optional[str] = Field(default=None, max_length=500, description="微信 Secret")
    xing_qiu_access_token: Optional[str] = Field(default=None, max_length=500, description="小星球 Access Token")
    xing_qiu_session_id: Optional[str] = Field(default=None, max_length=500, description="Session ID，适用于小星球、掘金等")
    xing_qiu_group_id: Optional[str] = Field(default=None, max_length=100, description="小星球 Group ID")
    zhi_hu_cookie: Optional[str] = Field(default=None, max_length=1000, description="知乎 Cookie")
    jue_jin_session_id: Optional[str] = Field(default=None, max_length=1000, description="掘金session")
    apikey: Optional[str] = Field(default=None, max_length=1000, description="apikey")
    prompt: Optional[str] = Field(default=None, max_length=2000, description="prompt")
    chat_model: Optional[str] = Field(default='llama-3.1-70b-versatile', description="模型")
    create_time: Optional[int] = Field(default=0, description="配置创建时间的时间戳")
    update_time: Optional[int] = Field(default=None, description="配置更新时间的时间戳")

class PlatformConfigCreate(PlatformConfigBase):
    pass

class PlatformConfigUpdate(PlatformConfigBase):
    pass

class PlatformConfigInDBBase(PlatformConfigBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class PlatformConfig(PlatformConfigInDBBase, table=True):
    __tablename__ = 'platform_config'

class DeletePlatformConfig(BaseModel):
    ids: List[int]  # 批量删除时，确保 ids 是一个整数列表



# 定义请求体模型
class PublishNewsRequest(BaseModel):
    news_ids: List[int]
    platforms: List[str]
    type: str
