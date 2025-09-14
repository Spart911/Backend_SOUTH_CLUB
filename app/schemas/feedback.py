from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class FeedbackCreate(BaseModel):
    """Схема для создания обратной связи"""
    name: str = Field(..., min_length=2, max_length=100, description="Имя")
    email: EmailStr = Field(..., description="Email")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    message: str = Field(..., min_length=10, max_length=1000, description="Сообщение")


class FeedbackResponse(BaseModel):
    """Схема ответа при отправке обратной связи"""
    success: bool
    message: str
