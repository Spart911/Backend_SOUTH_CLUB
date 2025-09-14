from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...dependencies import get_db_session
from ...core.security import verify_admin_credentials, create_access_token
from ...schemas.auth import AdminLogin, AdminLoginResponse
from ...config import settings
from ...core.logging import get_logger

router = APIRouter(prefix="/auth", tags=["Аутентификация"])
logger = get_logger("AuthAPI")


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    """
    Вход в админку
    """
    logger.info(f"Попытка входа в админку: {form_data.username}")
    
    try:
        # Проверяем учетные данные
        if not verify_admin_credentials(form_data.username, form_data.password):
            logger.warning(f"Неудачная попытка входа в админку: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создаем токен доступа
        access_token = create_access_token(
            data={"sub": form_data.username}
        )
        
        logger.info(f"Успешный вход в админку: {form_data.username}")
        
        return AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при входе в админку {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post("/login-json", response_model=AdminLoginResponse)
async def admin_login_json(
    login_data: AdminLogin,
    db: Session = Depends(get_db_session)
):
    """
    Вход в админку через JSON
    """
    logger.info(f"Попытка входа в админку через JSON: {login_data.username}")
    
    try:
        # Проверяем учетные данные
        if not verify_admin_credentials(login_data.username, login_data.password):
            logger.warning(f"Неудачная попытка входа в админку через JSON: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создаем токен доступа
        access_token = create_access_token(
            data={"sub": login_data.username}
        )
        
        logger.info(f"Успешный вход в админку через JSON: {login_data.username}")
        
        return AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при входе в админку через JSON {login_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
