from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from .base import BaseRepository
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product]):
    """
    Репозиторий для работы с товарами
    """
    
    def __init__(self):
        super().__init__(Product)
    
    def get_by_name(self, db: Session, name: str) -> Optional[Product]:
        """
        Получить товар по названию
        """
        stmt = select(Product).where(Product.name == name)
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_size(self, db: Session, size: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Получить товары по размеру (проверяет наличие размера в массиве)
        """
        stmt = select(Product).where(Product.size.contains([size])).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_by_price_range(self, db: Session, min_price: int, max_price: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Получить товары по диапазону цен
        """
        stmt = select(Product).where(
            Product.price >= min_price,
            Product.price <= max_price
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    
    def search_products(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Поиск товаров по названию или характеристикам
        """
        search_term = f"%{query}%"
        stmt = select(Product).where(
            (Product.name.ilike(search_term)) |
            (Product.color.ilike(search_term))
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_with_photos(self, db: Session, product_id: UUID) -> Optional[Product]:
        """
        Получить товар с фотографиями
        """
        stmt = select(Product).where(Product.id == product_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

