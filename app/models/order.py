from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from ..database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, comment="ID заказа")
    email = Column(String(255), nullable=False, comment="Email клиента")
    phone = Column(String(20), nullable=False, comment="Телефон клиента")
    address = Column(Text, nullable=False, comment="Адрес доставки")
    delivery_time = Column(String(100), nullable=False, comment="Время доставки")
    order_time = Column(String(100), nullable=False, comment="Время заказа")
    items = Column(JSON, nullable=False, comment="Товары в заказе (JSON)")
    total_amount = Column(Float, nullable=False, comment="Общая сумма заказа")
    status = Column(String(50), nullable=False, default="created", comment="Статус заказа")
    payment_id = Column(String(255), nullable=True, comment="ID платежа в ЮKassa")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Дата создания")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Дата обновления")

