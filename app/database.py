from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from .core.logging import get_logger

# Логгер
logger = get_logger("Database")

# Создаем движок базы данных
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Отключаем SQL логирование в продакшене
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии базы данных
    """
    db = SessionLocal()
    try:
        logger.debug("Сессия базы данных создана")
        yield db
    except Exception as e:
        logger.error(f"Ошибка в сессии базы данных: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Сессия базы данных закрыта")


def create_tables():
    """
    Создание всех таблиц в базе данных
    """
    try:
        logger.info("Создание таблиц в базе данных...")
        # Импортируем все модели для регистрации в Base.metadata
        from .models import Product, ProductPhoto, SliderPhoto, Order
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы в базе данных успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {str(e)}")
        raise
