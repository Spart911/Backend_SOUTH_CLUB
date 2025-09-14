from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class Product(Base):
    """
    Модель товара
    """
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, comment="Название товара")
    color = Column(Text, nullable=True, comment="Цвет")
    composition = Column(Text, nullable=True, comment="Состав")
    print_technology = Column(Text, nullable=True, comment="Технология печати")
    size = Column(JSON, nullable=False, comment="Размеры (массив чисел 0-4)")
    price = Column(Integer, nullable=False, comment="Цена")
    order_number = Column(Integer, nullable=True, comment="Порядковый номер отображения")
    soon = Column(Boolean, nullable=False, default=False, server_default='false', comment="Скоро в продаже")

    # Связи
    photos = relationship("ProductPhoto", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

