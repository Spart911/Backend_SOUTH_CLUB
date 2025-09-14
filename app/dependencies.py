from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import get_db
from .config import settings
from .core.logging import get_logger
# from .core.security import verify_admin_credentials

# Схема аутентификации
security = HTTPBearer()
logger = get_logger("Dependencies")


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency для проверки аутентификации админа
    """
    try:
        # Проверяем что токен не пустой
        if not credentials.credentials or not credentials.credentials.strip():
            logger.warning("Попытка аутентификации с пустым токеном")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не предоставлен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = jwt.decode(
            credentials.credentials, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        
        # Проверяем что username не None и соответствует админу
        if username is None or username != settings.admin_username:
            logger.warning(f"Попытка аутентификации с неверным username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Успешная аутентификация админа: {username}")
        return username
        
    except JWTError as e:
        logger.warning(f"Ошибка JWT при аутентификации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при аутентификации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


def get_db_session(db: Session = Depends(get_db)) -> Session:
    """
    Dependency для получения сессии базы данных.
    Возвращает реальный объект Session.
    """
    return db
