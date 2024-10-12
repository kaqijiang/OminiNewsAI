import os
import secrets
from pydantic import BeforeValidator, computed_field, Field, AnyUrl, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Literal, Annotated
from utils.logging_config import LogManager

logger = LogManager.get_logger()

# 公共函数：加载环境配置
def load_config_settings(env_file_path: str = None):
    if env_file_path and os.path.exists(env_file_path):
        # 如果本地存在 env 文件，手动加载
        return SettingsConfigDict(env_file=env_file_path, env_ignore_empty=True, extra="ignore")
    else:
        # 如果在 Docker 环境中，依赖 Docker 自动注入的环境变量
        return SettingsConfigDict(env_ignore_empty=True, extra="ignore")

# 定义基础路径和环境变量文件
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_FILE_PATH = os.path.join(BASE_DIR, '.env')

# 自动判断是否在 Docker 环境中
if os.getenv("DOCKER_ENV"):
    logger.info("在 Docker 环境中，使用环境变量注入")
    ENV_FILE_PATH = None  # 在 Docker 环境中不手动加载 .env 文件
else:
    logger.info(f"在本地环境中，加载本地的 .env 文件: {ENV_FILE_PATH}")

# 解析 CORS
def parse_cors(v: Any) -> list[str]:
    try:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
    except Exception as e:
        logger.error(f"解析 CORS 配置时出错: {e}")
        return []
    raise ValueError(f"无法解析 CORS 配置，输入值为: {v}")

class DataBaseConfig(BaseSettings):
    db_echo: bool = Field(default=False, env='DB_ECHO')
    db_pre_ping: bool = Field(default=False, env='PRE_PING')
    db_max_overflow: int = Field(default=10, env='DB_MAX_OVERFLOW')
    db_pool_size: int = Field(default=5, env='DB_POOL_SIZE')
    db_pool_recycle: int = Field(default=3600, env='DB_POOL_RECYCLE')
    db_pool_timeout: int = Field(default=30, env='DB_POOL_TIMEOUT')
    model_config = load_config_settings(ENV_FILE_PATH)

class RedisSettings(BaseSettings):
    redis_host: str = Field(default='127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(default=6379, env='REDIS_PORT')
    redis_username: str = Field(default='', env='REDIS_USERNAME')
    redis_password: str = Field(default='', env='REDIS_PASSWORD')
    redis_database: int = Field(default=0, env='REDIS_DB')
    model_config = load_config_settings(ENV_FILE_PATH)

class MySQLSettings(BaseSettings):
    MYSQL_SERVER: str = Field(..., env='MYSQL_SERVER')
    MYSQL_PORT: int = Field(..., env='MYSQL_PORT')
    MYSQL_USER: str = Field(..., env='MYSQL_USER')
    MYSQL_PASSWORD: str = Field(..., env='MYSQL_PASSWORD')
    MYSQL_DB: str = Field(..., env='MYSQL_DB')
    model_config = load_config_settings(ENV_FILE_PATH)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

class SMTPSettings(BaseSettings):
    SMTP_TLS: bool = Field(default=True, env='SMTP_TLS')
    SMTP_SSL: bool = Field(default=False, env='SMTP_SSL')
    SMTP_PORT: int = Field(default=587, env='SMTP_PORT')
    SMTP_HOST: str | None = Field(default=None, env='SMTP_HOST')
    SMTP_USER: str | None = Field(default=None, env='SMTP_USER')
    SMTP_PASSWORD: str | None = Field(default=None, env='SMTP_PASSWORD')
    EMAILS_FROM_EMAIL: str | None = Field(default=None, env='EMAILS_FROM_EMAIL')
    EMAILS_FROM_NAME: str | None = Field(default=None, env='EMAILS_FROM_NAME')
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = Field(default=48, env='EMAIL_RESET_TOKEN_EXPIRE_HOURS')
    model_config = load_config_settings(ENV_FILE_PATH)

    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

class Settings(BaseSettings):
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    SECRET_KEY: str = Field(default=secrets.token_urlsafe(32), env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 8, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    DOMAIN: str = Field(default="localhost", env="DOMAIN")
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(default="local", env="ENVIRONMENT")
    FIRST_SUPERUSER: str = Field(..., env="FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = Field(..., env="FIRST_SUPERUSER_PASSWORD")
    USERS_OPEN_REGISTRATION: bool = Field(default=False, env="USERS_OPEN_REGISTRATION")
    PROJECT_NAME: str = Field(default="Default Project Name", env="PROJECT_NAME")
    CachePathConfig_Path: str = Field(default=os.path.join(BASE_DIR, 'caches'), env="CachePathConfig_Path")

    EMAIL_USERNAME: str = Field(..., env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(..., env="EMAIL_PASSWORD")

    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")

    # 计算服务器的完整主机URL
    @computed_field
    @property
    def server_host(self) -> str:
        return f"https://{self.DOMAIN}" if self.ENVIRONMENT != "local" else f"http://{self.DOMAIN}"

    # CORS设置
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = Field(default=[], env='BACKEND_CORS_ORIGINS')

    model_config = load_config_settings(ENV_FILE_PATH)

# 初始化和打印配置信息
settings = Settings()
redis_settings = RedisSettings()
mysql_settings = MySQLSettings()
smtp_settings = SMTPSettings()
dataBase_settings = DataBaseConfig()

logger.info(f"\n\n应用配置: {settings.dict()}\n\n")
logger.info(f"\n\nRedis 配置: {redis_settings.dict()}\n\n")
logger.info(f"\n\nMySQL 配置: {mysql_settings.dict()}\n\n")
logger.info(f"\n\nSMTP 配置: {smtp_settings.dict()}\n\n")
