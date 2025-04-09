from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from api.crud import create_user
from api.models import User, UserCreate, NewsCategories
from core.config import settings, mysql_settings, dataBase_settings
from utils.logging_config import LogManager

# 获取日志记录器实例
logger = LogManager.get_logger()

# 检查是否已设置数据库连接URI，未设置则抛出异常
if mysql_settings.SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("SQLALCHEMY_DATABASE_URI is None. Please check the configuration.")

# 创建异步数据库引擎，配置连接池和SQL调试模式
async_engine = create_async_engine(
    mysql_settings.SQLALCHEMY_DATABASE_URI,
    echo=True,  # 启用SQL语句的打印，有助于调试
    pool_pre_ping=True,  # 在每次连接前ping数据库，以防连接丢失
    pool_recycle=dataBase_settings.db_pool_recycle,   # 连接池中连接的最大存活时间，防止数据库自动关闭长时间运行的连接
    pool_size=dataBase_settings.db_pool_size,        # 连接池的大小
    max_overflow=dataBase_settings.db_max_overflow,      # 连接池允许的最大溢出连接数
    pool_timeout=dataBase_settings.db_pool_timeout
)

# 创建异步会话工厂，用于生成数据库会话
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,  # 指定会话类型为异步会话
    expire_on_commit=False,  # 提交事务后不立即过期记录
    autocommit=False,         # 不自动提交事务
    autoflush=False           # 不自动刷新事务
)

async def check_mysql_db(db_engine) -> None:
    """
    尝试与数据库建立连接，以检查其是否已就绪。
    如果在预设次数内数据库未响应，则抛出异常。
    """
    async with db_engine.connect() as conn:
        try:
            # 执行异步查询来检查数据库连接
            await conn.execute(select(1))
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
async def init_create_table():
    """
    初始化数据库表并创建超级用户。
    """
    logger.info('初始化数据库连接并创建表...')
    # 开始一个新的数据库事务
    async with async_engine.begin() as conn:
        # 同步方式创建所有表，`run_sync`用于在异步环境中执行同步操作
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("数据库表创建成功。")

    # 初始化超级用户
    logger.info("检查并可能创建超级用户...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.FIRST_SUPERUSER))
        user = result.scalars().first()
        if not user:
            logger.info('超级用户不存在，正在创建...')
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True
            )
            # 调用 CRUD 操作创建用户
            user = await create_user(session=session, user_create=user_in)
            logger.info('超级用户创建成功。')
        
        # 初始化新闻分类
        logger.info("检查并初始化新闻分类...")
        result = await session.execute(select(NewsCategories))
        categories = result.scalars().all()
        if not categories:
            logger.info('新闻分类不存在，正在创建...')
            default_categories = [
                {"category_name": "AI", "category_value": "AI"},
                {"category_name": "汽车", "category_value": "汽车"},
                {"category_name": "科技", "category_value": "科技"},
                {"category_name": "创业", "category_value": "创业"},
                {"category_name": "金融", "category_value": "金融"}
            ]
            for category in default_categories:
                db_category = NewsCategories(**category)
                session.add(db_category)
            await session.commit()
            logger.info('新闻分类初始化成功。')
