import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import event

from api.deps import get_db, get_current_user
from core.db import async_engine  # 假设这是您定义的实际异步数据库引擎

from core.config import settings
from utils.logging_config import LogManager

# 获取单例日志记录器实例
logger = LogManager.get_logger()

# SQLAlchemy 事件监听器用于记录 SQL 查询
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.info("Start Query: %s", statement)
    logger.info("Parameters: %s", parameters)

def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.info("End Query: %s", statement)

# 创建日志依赖项
async def log_request(request: Request, call_next):
    request_time = time.time()
    client_host = request.client.host
    method = request.method
    url = str(request.url)
    headers = dict(request.headers)

    # 使用依赖项提取用户信息
    user_id = "Unknown"
    try:
        token = headers.get("Authorization").split(" ")[1] if "Authorization" in headers else None
        if token:
            async for session in get_db():
                user = get_current_user(session=session, token=token)
                user_id = user.id
    except Exception as e:
        logger.error(f"Error extracting user ID: {e}")

    try:
        body = await request.json()
    except:
        body = await request.body()

    logger.info(
        f"Received request: User ID={user_id}, Client Host={client_host}, Method={method}, URL={url}, Headers={headers}, Body={body}"
    )

    response = await call_next(request)
    response_time = time.time() - request_time
    logger.info(f"Sent response: Status Code={response.status_code}, Response Time={response_time:.4f}s")
    return response

class SQLQueryLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        sync_engine = async_engine.sync_engine  # 确保绑定的是 sync_engine
        try:
            event.listen(sync_engine, "before_cursor_execute", before_cursor_execute)
            event.listen(sync_engine, "after_cursor_execute", after_cursor_execute)
            response = await call_next(request)
        finally:
            if event.contains(sync_engine, "before_cursor_execute", before_cursor_execute):
                event.remove(sync_engine, "before_cursor_execute", before_cursor_execute)
            if event.contains(sync_engine, "after_cursor_execute", after_cursor_execute):
                event.remove(sync_engine, "after_cursor_execute", after_cursor_execute)
        return response

def handle_middleware(app: FastAPI):
    """
    全局中间件处理
    """
    # 加载跨域中间件
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 添加日志中间件
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request)
    # SQL 查询日志中间件
    app.add_middleware(SQLQueryLoggerMiddleware)

