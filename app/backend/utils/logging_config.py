from loguru import logger
import sys
import os

class LogManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            # 移除默认的logger配置
            logger.remove()
            # 获取项目根目录
            project_root = os.path.abspath(os.path.join(__file__, '../..'))
            # 添加新的logger配置，输出到控制台
            logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {file} | {name} | {line} | {message}", enqueue=True)
            # 确保日志文件路径是相对于项目根目录的
            log_path = os.path.join(project_root, 'logs/{time:YYYY-MM-DD}.log')
            # 添加新的logger配置，输出到文件，并每天轮换日志文件
            logger.add(log_path, rotation="00:00", level="INFO", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", enqueue=True)
            cls._logger = logger
        return cls._instance

    @staticmethod
    def get_logger():
        if LogManager._instance is None:
            LogManager()
        return LogManager._logger


