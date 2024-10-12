from fastapi import APIRouter

from api.routers import users, utils, items, hello, publish_history, news_list, news_categories
from api.routers import platforms, login

api_router = APIRouter()
api_router.include_router(hello.router, prefix="/hello", tags=["hello"])
api_router.include_router(login.router, tags=["login登录模块"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(news_list.router, prefix="/news", tags=["newsList"])
api_router.include_router(news_categories.router, prefix="/newsCategories", tags=["newsCategories"])
api_router.include_router(publish_history.router, prefix="/history", tags=["history"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["platforms"])

