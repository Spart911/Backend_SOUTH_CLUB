from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from uuid import UUID


class ProductBase(BaseModel):
    """Базовая схема товара"""
    name: str = Field(..., description="Название товара")
    color: Optional[str] = Field(None, description="Цвет")
    composition: Optional[str] = Field(None, description="Состав")
    print_technology: Optional[str] = Field(None, description="Технология печати")
    size: List[int] = Field(
        ...,
        description="Размеры (массив чисел 0-4). Может быть пустым, если soon=true",
        example=[1, 2, 3]
    )
    price: int = Field(..., ge=0, description="Цена. Может быть 0, если soon=true")
    order_number: Optional[int] = Field(None, ge=0, description="Порядковый номер отображения")
    soon: bool = Field(False, description="Товар скоро в продаже (SOON)")

    @field_validator('size')
    @classmethod
    def validate_sizes(cls, v):
        # Пустой список допустим, дальнейшая проверка ниже в model_validator
        for size in (v or []):
            if not isinstance(size, int) or size < 0 or size > 4:
                raise ValueError('Каждый размер должен быть числом от 0 до 4')
        return v

    @model_validator(mode="after")
    def validate_size_with_soon(self):
        # Если soon=false, sizes должен быть непустым
        if not getattr(self, 'soon', False):
            if self.size is None or len(self.size) == 0:
                raise ValueError('Поле size не может быть пустым, когда soon=false')
        # Цена 0 допустима только при soon=true
        if getattr(self, 'price', None) == 0 and not getattr(self, 'soon', False):
            raise ValueError('price=0 разрешен только при soon=true')
        return self


class ProductCreate(ProductBase):
    """Схема для создания товара"""
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Худи SOUTH CLUB",
                    "color": "Черный",
                    "composition": "80% хлопок, 20% полиэстер",
                    "print_technology": "Вышивка",
                    "size": [1, 2, 3],
                    "price": 4500,
                    "order_number": 1,
                    "soon": False
                }
            ]
        }


class ProductUpdate(BaseModel):
    """Схема для обновления товара"""
    name: Optional[str] = Field(None, description="Название товара")
    color: Optional[str] = Field(None, description="Цвет")
    composition: Optional[str] = Field(None, description="Состав")
    print_technology: Optional[str] = Field(None, description="Технология печати")
    size: Optional[List[int]] = Field(
        None,
        description="Размеры (массив чисел 0-4). Может быть пустым, если soon=true",
        example=[0, 1, 2, 3, 4]
    )
    price: Optional[int] = Field(None, ge=0, description="Цена. Может быть 0, если soon=true")
    order_number: Optional[int] = Field(None, ge=0, description="Порядковый номер отображения")
    soon: Optional[bool] = Field(None, description="Товар скоро в продаже (SOON)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Худи SOUTH CLUB обновленный",
                    "size": [0, 1, 2, 3, 4],
                    "price": 4700,
                    "order_number": 2,
                    "soon": True
                }
            ]
        }

    @field_validator('size')
    @classmethod
    def validate_sizes(cls, v):
        if v is not None:
            # Пустой список допустим, если soon=true — проверяется ниже в model_validator
            for size in v:
                if not isinstance(size, int) or size < 0 or size > 4:
                    raise ValueError('Каждый размер должен быть числом от 0 до 4')
        return v

    @model_validator(mode="after")
    def validate_size_with_soon(self):
        # В update допускаем пустой size только если soon явно true
        if self.size is not None and len(self.size) == 0:
            if not (self.soon is True):
                raise ValueError('Пустой size разрешен только при soon=true')
        # В update допускаем price=0 только если soon явно true в этом же запросе
        if self.price is not None and self.price == 0:
            if not (self.soon is True):
                raise ValueError('price=0 разрешен только при soon=true')
        return self


class ProductResponse(ProductBase):
    """Схема для ответа с товаром"""
    id: UUID
    photos: List['ProductPhotoResponse'] = []

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "examples": [
                {
                    "id": "58289d8c-6015-467d-97f3-7c87ccaf0d42",
                    "name": "Худи SOUTH CLUB",
                    "color": "Черный",
                    "composition": "80% хлопок, 20% полиэстер",
                    "print_technology": "Вышивка",
                    "size": [1, 2, 3],
                    "price": 4500,
                    "order_number": 1,
                    "soon": False,
                    "photos": []
                }
            ]
        }


class ProductListResponse(BaseModel):
    """Схема для списка товаров"""
    products: List[ProductResponse]
    total: int
    page: int
    size: int


# Импорт для избежания циклических зависимостей
from .photo import ProductPhotoResponse

# Обновляем forward references
ProductResponse.model_rebuild()
