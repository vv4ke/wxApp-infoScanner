import sys

from loguru import logger

# 添加控制台输出，输出级别为 INFO
logger.add(
    sink = sys.stdout,
    format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level = "INFO"
)

# 添加文件输出，输出级别为 WARNING
logger.add(
    sink = "./logs/warning.log",
    rotation = "1 week",
    retention = "4 weeks",
    compression = "zip",
    format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level = "WARNING"
)

# 记录日志
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")



import colorama
from colorama import Fore, Back, Style

# 初始化 colorama，可以让颜色代码在终端上生效
colorama.init()

print(Fore.RED + 'Hello, World!' + Style.RESET_ALL)
