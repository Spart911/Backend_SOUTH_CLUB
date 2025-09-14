from pydantic_settings import BaseSettings
from typing import List
import os
from pydantic import Field, validator


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/south_club_db",
        description="URL базы данных PostgreSQL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here",
        min_length=32,
        description="Секретный ключ для JWT токенов"
    )
    algorithm: str = Field(
        default="HS256",
        description="Алгоритм шифрования JWT"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="Время жизни JWT токена в минутах"
    )
    
    # Admin credentials
    admin_username: str = Field(
        default="admin",
        min_length=3,
        max_length=50,
        description="Имя пользователя админа"
    )
    admin_password: str = Field(
        default="admin123",
        min_length=8,
        description="Пароль админа"
    )
    
    # Telegram Bot
    telegram_bot_token: str = Field(
        default="your-telegram-bot-token",
        description="Токен Telegram бота"
    )
    telegram_chat_id: str = Field(
        default="your-chat-id",
        description="ID чата Telegram"
    )
    
    # YooKassa
    yookassa_shop_id: str = Field(
        default="your-shop-id",
        description="ID магазина в ЮKassa"
    )
    yookassa_secret_key: str = Field(
        default="your-secret-key",
        description="Секретный ключ ЮKassa"
    )
    
    # File uploads
    upload_dir: str = Field(
        default="./uploads",
        description="Директория для загрузки файлов"
    )
    max_file_size: int = Field(
        default=10485760,  # 10MB
        ge=1024,  # Минимум 1KB
        le=52428800,  # Максимум 50MB
        description="Максимальный размер файла в байтах"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173/",
        "http://localhost:8080/",
        "http://127.0.0.1:8080/",
        "http://192.168.0.14:5173/"
    ],
        description="Разрешенные CORS origins"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    # Валидаторы отключены для разработки
    # В продакшене обязательно включить!
    
    # @validator('secret_key')
    # def validate_secret_key(cls, v):
    #     if v == "your-secret-key-here":
    #         raise ValueError("Необходимо установить уникальный SECRET_KEY")
    #     return v
    
    # @validator('admin_password')
    # def validate_admin_password(cls, v):
    #     if v == "admin123":
    #         raise ValueError("Необходимо изменить пароль админа по умолчанию")
    #     return v
    
    # @validator('database_url')
    # def validate_database_url(cls, v):
    #     if not v.startswith(('postgresql://', 'postgres://')):
    #         raise ValueError("DATABASE_URL должен начинаться с postgresql:// или postgres://")
    #     return v


# Создаем экземпляр настроек
settings = Settings()

# Создаем директории для загрузки если их нет
os.makedirs(os.path.join(settings.upload_dir, "products"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "slider"), exist_ok=True)
