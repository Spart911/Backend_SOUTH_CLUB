from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database import Base


class SliderPhoto(Base):
    """
    Модель фотографии слайдера
    """
    __tablename__ = "slider_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, comment="Имя фотографии")
    file_path = Column(Text, nullable=False, comment="Абсолютный путь к файлу")
    order_number = Column(Integer, nullable=False, default=0, comment="Порядковый номер")

    def __repr__(self):
        return f"<SliderPhoto(id={self.id}, name='{self.name}', order_number={self.order_number})>"

