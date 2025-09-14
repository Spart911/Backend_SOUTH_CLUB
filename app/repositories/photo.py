from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from .base import BaseRepository
from ..models.photo import ProductPhoto
from ..schemas.photo import ProductPhotoCreate, ProductPhotoUpdate


class ProductPhotoRepository(BaseRepository[ProductPhoto]):
    """
    Репозиторий для работы с фотографиями товаров
    """
    
    def __init__(self):
        super().__init__(ProductPhoto)
    
    def get_by_product_id(self, db: Session, product_id: UUID) -> List[ProductPhoto]:
        """
        Получить все фотографии товара
        """
        stmt = select(ProductPhoto).where(
            ProductPhoto.product_id == product_id
        ).order_by(ProductPhoto.priority.desc())
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_by_priority(self, db: Session, product_id: UUID, priority: int) -> List[ProductPhoto]:
        """
        Получить фотографии товара по приоритету
        """
        stmt = select(ProductPhoto).where(
            ProductPhoto.product_id == product_id,
            ProductPhoto.priority == priority
        )
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_main_photo(self, db: Session, product_id: UUID) -> Optional[ProductPhoto]:
        """
        Получить главную фотографию товара (с наивысшим приоритетом)
        """
        stmt = select(ProductPhoto).where(
            ProductPhoto.product_id == product_id
        ).order_by(ProductPhoto.priority.desc()).limit(1)
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    
    def delete_by_product_id(self, db: Session, product_id: UUID) -> bool:
        """
        Удалить все фотографии товара
        """
        photos = self.get_by_product_id(db, product_id)
        for photo in photos:
            db.delete(photo)
        db.commit()
        return True

