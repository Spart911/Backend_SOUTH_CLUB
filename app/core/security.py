from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from ..config import settings
from .logging import get_logger

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Логгер
logger = get_logger("Security")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля
    """
    return pwd_context.hash(password)


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Проверка учетных данных админа
    Используем безопасное сравнение строк для предотвращения timing attacks
    """
    import hmac
    
    # Безопасное сравнение строк
    expected_username = settings.admin_username.encode('utf-8')
    expected_password = settings.admin_password.encode('utf-8')
    
    username_match = hmac.compare_digest(
        username.encode('utf-8'), 
        expected_username
    )
    password_match = hmac.compare_digest(
        password.encode('utf-8'), 
        expected_password
    )
    
    result = username_match and password_match
    
    if result:
        logger.info(f"Успешная аутентификация админа: {username}")
    else:
        logger.warning(f"Неудачная попытка аутентификации админа: {username}")
    
    return result


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Создание JWT токена
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        logger.info(f"JWT токен создан для пользователя: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Ошибка при создании JWT токена: {str(e)}")
        raise
