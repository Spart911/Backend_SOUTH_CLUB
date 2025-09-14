from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class SliderPhotoBase(BaseModel):
    """Базовая схема фотографии слайдера"""
    name: str = Field(..., description="Имя фотографии")
    order_number: int = Field(0, ge=0, description="Порядковый номер")


class SliderPhotoCreate(SliderPhotoBase):
    """Схема для создания фотографии слайдера"""
    file_path: str = Field(..., description="Путь к файлу")


class SliderPhotoUpdate(BaseModel):
    """Схема для обновления фотографии слайдера"""
    name: Optional[str] = Field(None, description="Имя фотографии")
    order_number: Optional[int] = Field(None, ge=0, description="Порядковый номер")


class SliderPhotoResponse(SliderPhotoBase):
    """Схема для ответа с фотографией слайдера"""
    id: UUID
    file_path: str

    class Config:
        from_attributes = True


class SliderPhotoUpload(BaseModel):
    """Схема для загрузки фотографии в слайдер"""
    order_number: int = Field(0, ge=0, description="Порядковый номер")


class SliderPhotoSimple(BaseModel):
    """Схема элемента слайдера в списке"""
    id: UUID
    name: str
    file_path: str = Field(..., description="Путь к файлу (абсолютный URL)")
    order_number: int = Field(0, ge=0, description="Порядковый номер")


class SliderListResponse(BaseModel):
    """Схема для списка фотографий слайдера"""
    photos: List[SliderPhotoSimple]
    total: int

