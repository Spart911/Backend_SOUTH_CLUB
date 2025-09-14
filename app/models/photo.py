from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class ProductPhoto(Base):
    """
    Модель фотографии товара
    """
    __tablename__ = "product_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    name = Column(Text, nullable=False, comment="Имя фотографии")
    file_path = Column(Text, nullable=False, comment="Абсолютный путь к файлу")
    priority = Column(Integer, nullable=False, default=0, comment="Приоритет (0-2)")

    # Связи
    product = relationship("Product", back_populates="photos")

    def __repr__(self):
        return f"<ProductPhoto(id={self.id}, name='{self.name}', priority={self.priority})>"

