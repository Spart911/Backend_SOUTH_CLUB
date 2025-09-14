from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ProductPhotoBase(BaseModel):
    """Базовая схема фотографии товара"""
    name: str = Field(..., description="Имя фотографии")
    priority: int = Field(0, ge=0, le=2, description="Приоритет (0-2)")


class ProductPhotoCreate(ProductPhotoBase):
    """Схема для создания фотографии товара"""
    pass


class ProductPhotoUpdate(BaseModel):
    """Схема для обновления фотографии товара"""
    name: Optional[str] = Field(None, description="Имя фотографии")
    priority: Optional[int] = Field(None, ge=0, le=2, description="Приоритет (0-2)")


class ProductPhotoResponse(ProductPhotoBase):
    """Схема для ответа с фотографией товара"""
    id: UUID
    product_id: UUID
    file_path: str

    class Config:
        from_attributes = True


class ProductPhotoUpload(BaseModel):
    """Схема для загрузки фотографии"""
    priority: int = Field(0, ge=0, le=2, description="Приоритет (0-2)")

