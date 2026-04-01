"""日志配置"""
import sys
from loguru import logger
from pathlib import Path

from app.core.config import settings


def setup_logging():
    """配置日志系统"""

    # 移除默认的 handler
    logger.remove()

    # 控制台输出格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 控制台日志
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # 文件日志 - 所有日志
    logger.add(
        settings.LOG_DIR / "smartpaper_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # 文件日志 - 错误日志
    logger.add(
        settings.LOG_DIR / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    logger.info("日志系统初始化完成")
    logger.info(f"日志目录: {settings.LOG_DIR}")


# 导出 logger 实例
__all__ = ["logger", "setup_logging"]
