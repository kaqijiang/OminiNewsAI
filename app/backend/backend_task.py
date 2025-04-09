from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config import settings
from tasks.collect_data import run_collect_data
from tasks.clean_redis_cache import clean_redis_news_cache


def main():
    print(f"启动任务调度器，配置RSS采集任务和缓存清理任务")
    scheduler = AsyncIOScheduler()
    
    # 添加RSS数据收集任务，每20分钟执行一次
    scheduler.add_job(
        run_collect_data,
        trigger=CronTrigger(minute="*/20"),
        id="data_collect_task"
    )
    
    # 添加Redis缓存清理任务，每天凌晨3点执行
    scheduler.add_job(
        clean_redis_news_cache,
        trigger=CronTrigger(hour=3, minute=0),
        id="cache_clean_task"
    )
    
    scheduler.start()

    # 在这里可以加入一个无限循环来保持脚本运行
    try:
        import asyncio
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    main()