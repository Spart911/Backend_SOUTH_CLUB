from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .config import settings
from .database import create_tables
from .api.v1 import auth, products, photos, slider, feedback, orders
from .core.exceptions import (
    ProductNotFoundException,
    PhotoNotFoundException,
    SliderPhotoNotFoundException,
    InvalidFileTypeException,
    FileSizeExceededException,
    TelegramBotException
)
from .core.logging import setup_logging, get_logger

# Инициализируем логирование
setup_logging()
logger = get_logger("Main")

# Создаем экземпляр FastAPI
app = FastAPI(
    title="SOUTH CLUB Backend API",
    description=(
        "API бекенда SOUTH CLUB.\n\n"
        "Основные возможности:\n"
        "- Управление товарами (мульти-размеры: поле size — массив чисел 0-4).\n"
        "- Загрузка и управление фотографиями товаров.\n"
        "- Слайдер: файловое хранилище с манифестом (id, name, order_number).\n"
        "- Система заказов с интеграцией ЮKassa для оплаты.\n"
        "- Уведомления в Telegram о новых заказах.\n"
        "- Авторизация админа и защищенные операции."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Подключаем статические файлы для загрузок по требуемому префиксу
if os.path.exists(settings.upload_dir):
    # Доступно по URL: /app/uploads/<subdir>/<filename>
    app.mount("/app/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Подключаем API роуты
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(photos.router, prefix="/api/v1")
app.include_router(slider.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")

# Обработчики исключений
@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(request, exc):
    logger.warning(f"ProductNotFoundException: {exc.detail}")
    return {"detail": exc.detail, "status_code": exc.status_code}

@app.exception_handler(PhotoNotFoundException)
async def photo_not_found_handler(request, exc):
    logger.warning(f"PhotoNotFoundException: {exc.detail}")
    return {"detail": exc.detail, "status_code": exc.status_code}

@app.exception_handler(SliderPhotoNotFoundException)
async def slider_photo_not_found_handler(request, exc):
    logger.warning(f"SliderPhotoNotFoundException: {exc.detail}")
    return {"detail": exc.detail, "status_code": exc.status_code}

@app.exception_handler(InvalidFileTypeException)
async def invalid_file_type_handler(request, exc):
    logger.warning(f"InvalidFileTypeException: {exc.detail}")
    return {"detail": exc.detail, "status_code": exc.status_code}

@app.exception_handler(FileSizeExceededException)
async def file_size_exceeded_handler(request, exc):
    logger.warning(f"FileSizeExceededException: {exc.detail}")
    return {"detail": exc.detail, "status_code": exc.status_code}

@app.exception_handler(TelegramBotException)
async def telegram_bot_exception_handler(request, exc):
    logger.error(f"TelegramBotException: {exc.detail}")
    return {"detail": exc.detail, "status_code": exc.status_code}

# События жизненного цикла
@app.on_event("startup")
async def startup_event():
    """
    Событие при запуске приложения
    """
    logger.info("Запуск SOUTH CLUB Backend...")
    try:
        # Создаем таблицы в БД
        create_tables()
        logger.info("База данных инициализирована")
        
        # Отладка маршрутов
        logger.info("=== ОТЛАДКА: Доступные маршруты ===")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                logger.info(f"Путь: {route.path}, Методы: {route.methods}")
        logger.info("=== Конец отладки маршрутов ===")
        
        logger.info("🚀 SOUTH CLUB Backend успешно запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Событие при остановке приложения
    """
    logger.info("SOUTH CLUB Backend останавливается...")
    logger.info("🛑 SOUTH CLUB Backend остановлен")

# Корневой эндпоинт
@app.get("/")
async def root():
    """
    Корневой эндпоинт
    """
    logger.info("Запрос к корневому эндпоинту")
    return {
        "message": "SOUTH CLUB Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Эндпоинт для проверки здоровья
@app.get("/health")
async def health_check():
    """
    Проверка здоровья приложения
    """
    logger.debug("Запрос health check")
    return {"status": "healthy", "message": "SOUTH CLUB Backend работает"}

# Тестовый эндпоинт для проверки слайдера
@app.get("/test-slider")
async def test_slider():
    """
    Тестовый эндпоинт для проверки слайдера
    """
    try:
        from .database import SessionLocal
        from .models.slider_photo import SliderPhoto
        from sqlalchemy import select
        
        db = SessionLocal()
        try:
            # Проверяем количество фотографий в слайдере
            stmt = select(SliderPhoto)
            result = db.execute(stmt)
            photos = result.scalars().all()
            
            return {
                "message": "Слайдер проверен",
                "total_photos": len(photos),
                "photos": [{"id": str(p.id), "name": p.name, "order": p.order_number} for p in photos]
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка при проверке слайдера: {str(e)}")
        return {"error": str(e)}
