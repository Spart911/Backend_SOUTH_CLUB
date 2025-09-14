from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from uuid import UUID
from ..repositories.product import ProductRepository
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from ..core.exceptions import ProductNotFoundException


class ProductService:
    """
    Сервис для работы с товарами
    """
    
    def __init__(self):
        self.repository = ProductRepository()
    
    def create_product(self, db: Session, product_data: ProductCreate) -> ProductResponse:
        """
        Создать новый товар
        """
        # Автоматически назначаем order_number начиная с 1, если не передан
        try:
            if getattr(product_data, "order_number", None) is None:
                max_stmt = select(func.max(self.repository.model.order_number))
                max_val = db.execute(max_stmt).scalar()
                next_order = 1 if max_val is None else int(max_val) + 1
                # Устанавливаем значение в входные данные
                try:
                    product_data.order_number = next_order
                except Exception:
                    # На случай если модель иммутабельна — игнорируем, тогда репозиторий должен уметь принять dict
                    pass
        except Exception:
            # Если вычисление не удалось, оставляем как есть (NULL)
            pass

        product = self.repository.create(db, product_data)
        return ProductResponse.model_validate(product)
    
    def get_product(self, db: Session, product_id: UUID) -> ProductResponse:
        """
        Получить товар по ID
        """
        product = self.repository.get_with_photos(db, product_id)
        if not product:
            raise ProductNotFoundException(str(product_id))
        return ProductResponse.model_validate(product)
    
    def get_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> ProductListResponse:
        """
        Получить список товаров с пагинацией
        """
        products = self.repository.get_all(db, skip, limit)
        total = self.repository.count(db)
        
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    
    def update_product(
        self, 
        db: Session, 
        product_id: UUID, 
        product_data: ProductUpdate
    ) -> ProductResponse:
        """
        Обновить товар
        """
        product = self.repository.update(db, product_id, product_data)
        if not product:
            raise ProductNotFoundException(str(product_id))
        return ProductResponse.model_validate(product)
    
    def delete_product(self, db: Session, product_id: UUID) -> bool:
        """
        Удалить товар
        """
        product = self.repository.get(db, product_id)
        if not product:
            raise ProductNotFoundException(str(product_id))
        return self.repository.delete(db, product_id)
    
    def search_products(
        self, 
        db: Session, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> ProductListResponse:
        """
        Поиск товаров
        """
        products = self.repository.search_products(db, query, skip, limit)
        total = len(products)  # Для поиска считаем только найденные
        
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    
    def get_products_by_size(
        self, 
        db: Session, 
        size: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> ProductListResponse:
        """
        Получить товары по размеру
        """
        products = self.repository.get_by_size(db, size, skip, limit)
        total = len(products)
        
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    
    def get_products_by_price_range(
        self, 
        db: Session, 
        min_price: int, 
        max_price: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> ProductListResponse:
        """
        Получить товары по диапазону цен
        """
        products = self.repository.get_by_price_range(db, min_price, max_price, skip, limit)
        total = len(products)
        
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=skip // limit + 1,
            size=limit
        )

