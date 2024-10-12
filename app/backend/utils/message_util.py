from utils.logging_config import LogManager

# 配置日志记录
logger = LogManager.get_logger()
def message_service(sms_code: str):
    logger.info(f"短信验证码为{sms_code}")
