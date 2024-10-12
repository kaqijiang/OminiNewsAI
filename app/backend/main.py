from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute
from api.main import api_router
from core.config import settings
from core.db import init_create_table
from core.get_redis import RedisUtil
from exceptions.handle import handle_exception
from exceptions.handle_sub_applications import handle_sub_applications
from utils.logging_config import LogManager
from middlewares.handle import handle_middleware

logger = LogManager.get_logger()


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'{settings.PROJECT_NAME}开始启动')
    await init_create_table()
    # Initialize Redis
    app.state.redis = await RedisUtil.create_redis_pool()

    try:
        # 将初始系统数据加载到redis
        await RedisUtil.init_sys_dict(app.state.redis)
        await RedisUtil.init_sys_config(app.state.redis)

        # 启动定时任务调度器
        # await SchedulerUtil.init_system_scheduler()
        # # 调用任务调度方法，添加所有的任务
        # await schedule_tasks()

        logger.info(f'{settings.PROJECT_NAME}启动成功')

        yield
    finally:

        # 关闭定时任务调度器
        # await SchedulerUtil.close_system_scheduler()  # 正确关闭调度器

        # 确保redis连接正确关闭
        await RedisUtil.close_redis_pool(app)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

# 挂载子应用
handle_sub_applications(app)
# 加载中间件处理方法
handle_middleware(app)

# 加载全局异常处理方法
handle_exception(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info(f"API LIST:")
for route in app.routes:
    if isinstance(route, APIRoute):
        methods = ", ".join(route.methods)
        logger.info(f"{route.path} -> {methods}")

if __name__ == '__main__':
    import uvicorn

    port = settings.BACKEND_PORT  # 从设置中读取端口
    # 工具页面
    logger.info(f"""

    Swagger UI: http://127.0.0.1:{port}/docs
    Redoc: http://127.0.0.1:{port}/redoc
    Root endpoint: http://127.0.0.1:{port}/api/v1/
    """)
    uvicorn.run(app, host="0.0.0.0", port=port)
