from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from .base import BaseRepository
from ..models.slider_photo import SliderPhoto
from ..schemas.slider import SliderPhotoCreate, SliderPhotoUpdate


class SliderPhotoRepository(BaseRepository[SliderPhoto]):
    """
    Репозиторий для работы с фотографиями слайдера
    """
    
    def __init__(self):
        super().__init__(SliderPhoto)
    
    def get_ordered(self, db: Session) -> List[SliderPhoto]:
        """
        Получить все фотографии слайдера в правильном порядке
        """
        stmt = select(SliderPhoto).order_by(SliderPhoto.order_number.asc())
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_by_order_number(self, db: Session, order_number: int) -> Optional[SliderPhoto]:
        """
        Получить фотографию по порядковому номеру
        """
        stmt = select(SliderPhoto).where(SliderPhoto.order_number == order_number)
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_next_order_number(self, db: Session) -> int:
        """
        Получить следующий доступный порядковый номер
        """
        stmt = select(SliderPhoto).order_by(SliderPhoto.order_number.desc()).limit(1)
        result = db.execute(stmt)
        last_photo = result.scalar_one_or_none()
        return (last_photo.order_number + 1) if last_photo else 0
    
    def reorder_photos(self, db: Session) -> bool:
        """
        Пересчитать порядковые номера фотографий
        """
        photos = self.get_ordered(db)
        for i, photo in enumerate(photos):
            photo.order_number = i
        db.commit()
        return True
    
    def update_order(self, db: Session, photo_id: UUID, new_order: int) -> Optional[SliderPhoto]:
        """
        Обновить порядковый номер фотографии
        """
        photo = self.get(db, photo_id)
        if photo:
            # Проверяем, не занят ли новый порядковый номер
            existing_photo = self.get_by_order_number(db, new_order)
            if existing_photo and existing_photo.id != photo_id:
                # Если номер занят, сдвигаем существующие
                photos_to_update = db.execute(
                    select(SliderPhoto).where(SliderPhoto.order_number >= new_order)
                ).scalars().all()
                for p in photos_to_update:
                    p.order_number += 1
            
            photo.order_number = new_order
            db.commit()
            db.refresh(photo)
        return photo

