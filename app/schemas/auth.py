from pydantic import BaseModel, Field


class AdminLogin(BaseModel):
    """Схема для входа админа"""
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")


class AdminLoginResponse(BaseModel):
    """Схема ответа при успешном входе"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Схема данных токена"""
    username: str

