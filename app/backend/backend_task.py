from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config import settings
from tasks.collect_data import run_collect_data


def main():
    print(settings.EMAIL_PASSWORD)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_collect_data,
        trigger=CronTrigger(minute="*/20"),
        id="data_collect_task"
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