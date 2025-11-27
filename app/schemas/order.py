from pydantic import BaseModel, Field, EmailStr, field_serializer, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

# Московский часовой пояс (UTC+3)
MSK = timezone(timedelta(hours=3))

# Размеры товаров
SIZE_LABELS = {
    0: 'XS',
    1: 'S',
    2: 'M',
    3: 'L',
    4: 'XL'
}

def get_size_label(size_value: int) -> str:
    """Преобразует числовое значение размера в текстовую метку"""
    return SIZE_LABELS.get(size_value, f'Размер {size_value}')


class OrderItem(BaseModel):
    """Элемент заказа"""
    name: str = Field(..., description="Название товара")
    quantity: int = Field(..., gt=0, description="Количество товара")
    price: float = Field(..., gt=0, description="Цена за единицу")
    size: int = Field(..., ge=0, le=4, description="Размер товара (0=XS, 1=S, 2=M, 3=L, 4=XL)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Футболка черная",
                "quantity": 2,
                "price": 1500.0
            }
        }


class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    customer_name: str = Field(..., description="Имя клиента")
    email: EmailStr = Field(..., description="Email клиента")
    phone: str = Field(..., min_length=10, max_length=20, description="Телефон клиента")
    address: str = Field(..., min_length=10, description="Адрес доставки")
    delivery_time: datetime = Field(..., description="Время доставки")
    # order_time теперь необязателен, будет заполняться автоматически при создании заказа
    order_time: Optional[datetime] = Field(None, description="Время заказа")
    items: List[OrderItem] = Field(..., min_items=1, description="Список товаров в заказе")
    total_amount: float = Field(..., gt=0, description="Общая сумма заказа")

    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Иванов Иван Иванович",
                "email": "client@example.com",
                "phone": "+7 (999) 123-45-67",
                "address": "ул. Пушкина, д. 1, кв. 1",
                "delivery_time": "2024-01-15T14:00:00",
                "order_time": "2024-01-15T10:30:00",
                "items": [
                    {
                        "name": "Футболка черная",
                        "quantity": 2,
                        "price": 1500.0,
                        "size": 2
                    }
                ],
                "total_amount": 3000.0
            }
        }


class OrderResponse(BaseModel):
    """Схема ответа с данными заказа"""
    id: int = Field(..., description="ID заказа")
    customer_name: str = Field(..., description="Имя клиента")
    email: str = Field(..., description="Email клиента")
    phone: str = Field(..., description="Телефон клиента")
    address: str = Field(..., description="Адрес доставки")
    delivery_time: datetime = Field(..., description="Время доставки")
    order_time: datetime = Field(..., description="Время заказа")
    items: List[Dict[str, Any]] = Field(..., description="Товары в заказе (name, quantity, price, size)")
    total_amount: float = Field(..., description="Общая сумма заказа")
    status: str = Field(..., description="Статус заказа")
    payment_id: Optional[str] = Field(None, description="ID платежа в ЮKassa")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    @field_serializer('delivery_time', 'order_time', 'created_at', 'updated_at')
    def serialize_datetime(self, value: datetime, info) -> str:
        """Сериализует datetime в ISO формат с московским timezone"""
        field_name = info.field_name

        print(f"DEBUG: Serializing {field_name} - value: {value}, tzinfo: {value.tzinfo}")

        if value.tzinfo is None:
            # Это не должно происходить, но на всякий случай
            value = value.replace(tzinfo=timezone.utc)

        # Конвертируем все в MSK timezone
        if value.tzinfo != MSK:
            value = value.astimezone(MSK)

        result = value.isoformat()
        print(f"DEBUG: Final {field_name}: {result}")
        return result

    class Config:
        from_attributes = True


class OrderStatusResponse(BaseModel):
    """Схема ответа со статусом заказа"""
    order_id: int = Field(..., description="ID заказа")
    status: str = Field(..., description="Статус заказа")
    total_amount: float = Field(..., description="Сумма заказа")
    payment_id: Optional[str] = Field(None, description="ID платежа в ЮKassa")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1,
                "status": "paid",
                "total_amount": 3000.0,
                "payment_id": "2c7d4b5a-8f3e-4c1d-9b2a-1e5f8c3d7a9b"
            }
        }


class PaymentResponse(BaseModel):
    """Схема ответа с данными платежа"""
    order_id: int = Field(..., description="ID заказа")
    confirmation_token: str = Field(..., description="Токен подтверждения для ЮKassa")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1,
                "confirmation_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }


class YooKassaNotification(BaseModel):
    """Схема уведомления от ЮKassa"""
    type: str = Field(..., description="Тип уведомления")
    event: str = Field(..., description="Событие")
    object: Dict[str, Any] = Field(..., description="Данные объекта")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "notification",
                "event": "payment.succeeded",
                "object": {
                    "id": "2c7d4b5a-8f3e-4c1d-9b2a-1e5f8c3d7a9b",
                    "status": "succeeded",
                    "amount": {
                        "value": "3000.00",
                        "currency": "RUB"
                    }
                }
            }
        }

