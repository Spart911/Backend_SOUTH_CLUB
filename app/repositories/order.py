from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from ..models.order import Order
from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Репозиторий для работы с заказами"""
    
    def __init__(self):
        super().__init__(Order)
    
    def get_by_payment_id(self, db: Session, payment_id: str) -> Optional[Order]:
        """
        Получить заказ по ID платежа
        """
        stmt = select(Order).where(Order.payment_id == payment_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_email(self, db: Session, email: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Получить заказы по email клиента
        """
        stmt = select(Order).where(Order.email == email).offset(skip).limit(limit).order_by(Order.created_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Получить заказы по статусу
        """
        stmt = select(Order).where(Order.status == status).offset(skip).limit(limit).order_by(Order.created_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_recent_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Получить последние заказы
        """
        stmt = select(Order).offset(skip).limit(limit).order_by(Order.created_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()
    
    def get_orders_count(self, db: Session) -> int:
        """
        Получить общее количество заказов
        """
        stmt = select(func.count(Order.id))
        result = db.execute(stmt)
        return result.scalar() or 0
    
    def get_orders_count_by_status(self, db: Session, status: str) -> int:
        """
        Получить количество заказов по статусу
        """
        stmt = select(func.count(Order.id)).where(Order.status == status)
        result = db.execute(stmt)
        return result.scalar() or 0
    
    def get_total_revenue(self, db: Session) -> float:
        """
        Получить общую выручку (сумма всех оплаченных заказов)
        """
        stmt = select(func.sum(Order.total_amount)).where(Order.status == "paid")
        result = db.execute(stmt)
        return result.scalar() or 0.0

