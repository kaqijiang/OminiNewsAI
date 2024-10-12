from apscheduler.jobstores.base import ConflictingIdError

from core.config import redis_settings
from utils.logging_config import LogManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor  # 引入异步执行器

logger = LogManager.get_logger()


class SchedulerUtil:
    """管理定时任务的工具类"""
    scheduler = AsyncIOScheduler()

    @classmethod
    async def init_system_scheduler(cls):
        """在应用启动时初始化定时任务"""
        logger.info('开始启动定时任务...')

        job_stores = {
            'default': RedisJobStore(
                host=redis_settings.redis_host,
                port=redis_settings.redis_port,
                username=redis_settings.redis_username,
                password=redis_settings.redis_password,
                db=redis_settings.redis_database,
            ),
        }

        executors = {
            'default': AsyncIOExecutor(),  # 使用AsyncIO执行异步任务
            'processpool': ProcessPoolExecutor(5),
        }

        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
        }

        cls.scheduler.configure(jobstores=job_stores, executors=executors, job_defaults=job_defaults)
        cls.scheduler.start()  # 启动调度器

        logger.info('定时任务初始化完成。')

    @classmethod
    async def add_scheduler_job(cls, job_id, func, trigger,jobstore="default", executor="default"):
        """外部调用此方法添加定时任务"""
        try:
            cls.scheduler.add_job(
                func=func,  # 直接传递函数引用
                trigger=trigger,
                id=job_id,
                jobstore=jobstore,
                executor=executor,
                replace_existing=True  # 确保存在相同 ID 的任务时进行替换
            )
            logger.info(f"任务 {job_id} 已添加")
        except ConflictingIdError as e:
            logger.error(f"任务ID冲突：{e}")

    @classmethod
    async def close_system_scheduler(cls):
        """在应用关闭时关闭定时任务"""
        cls.scheduler.shutdown()  # 关闭调度器，停止所有任务
        logger.info('定时任务已成功关闭。')
