import logging
import sys
from pathlib import Path
from loguru import logger
from ..config import settings


class InterceptHandler(logging.Handler):
    """
    Перехватчик стандартного логирования Python для интеграции с loguru
    """
    
    def emit(self, record):
        # Получаем соответствующий уровень loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Находим вызывающий код
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Настройка системы логирования
    """
    # Удаляем стандартный обработчик loguru
    logger.remove()
    
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настройка формата логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Логирование в консоль
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Логирование в файл
    logger.add(
        log_dir / "app.log",
        format=log_format,
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Логирование ошибок в отдельный файл
    logger.add(
        log_dir / "error.log",
        format=log_format,
        level="ERROR",
        rotation="10 MB",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Перехватываем стандартное логирование Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Перехватываем логи от uvicorn
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    
    # Перехватываем логи от fastapi
    logging.getLogger("fastapi").handlers = [InterceptHandler()]
    
    logger.info("Система логирования настроена")


def get_logger(name: str = None):
    """
    Получить логгер для модуля
    """
    if name:
        return logger.bind(name=name)
    return logger

