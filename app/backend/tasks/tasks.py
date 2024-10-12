from apscheduler.triggers.cron import CronTrigger
from core.get_scheduler import SchedulerUtil
from tasks.collect_data import run_collect_data

async def schedule_tasks():
    """定义所有需要添加的任务"""
    # 添加数据收集任务，每50分钟执行一次
    await SchedulerUtil.add_scheduler_job(
        job_id="data_collect_task",
        func=run_collect_data,  # 任务函数
        trigger=CronTrigger(minute="*/50")  # 每50分钟执行一次
    )

    # 可以在这里继续添加其他任务
    # SchedulerUtil.add_scheduler_job(
    #     job_id="another_task",
    #     func=another_task_function,
    #     trigger=CronTrigger(hour="*/1"),  # 每小时执行一次
    # )

