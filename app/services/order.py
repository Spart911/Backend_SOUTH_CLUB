from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.order import Order
from ..schemas.order import OrderCreate, OrderResponse, OrderStatusResponse
from ..repositories.order import OrderRepository
from ..core.logging import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self):
        self.repository = OrderRepository()
    
    def create_order(self, db: Session, order_data: OrderCreate) -> OrderResponse:
        """
        Создать новый заказ
        """
        try:
            # Преобразуем items в список словарей для сохранения в JSON
            items_data = []
            for item in order_data.items:
                items_data.append({
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price
                })
            
            # Определяем время заказа: если не передано, используем текущее
            order_time = order_data.order_time or datetime.now()

            # Создаем объект заказа
            order = Order(
                customer_name=order_data.customer_name,
                email=order_data.email,
                phone=order_data.phone,
                address=order_data.address,
                delivery_time=order_data.delivery_time,
                order_time=order_time,
                items=items_data,
                total_amount=order_data.total_amount,
                status="created"
            )
            
            # Сохраняем в базу данных
            created_order = self.repository.create(db, order)
            logger.info(f"Создан заказ {created_order.id} для {order_data.email}")
            
            return OrderResponse.model_validate(created_order)
            
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {str(e)}")
            raise
    
    def get_order(self, db: Session, order_id: int) -> Optional[OrderResponse]:
        """
        Получить заказ по ID
        """
        try:
            order = self.repository.get(db, order_id)
            if not order:
                return None
            
            return OrderResponse.model_validate(order)
            
        except Exception as e:
            logger.error(f"Ошибка при получении заказа {order_id}: {str(e)}")
            raise
    
    def get_order_by_payment_id(self, db: Session, payment_id: str) -> Optional[OrderResponse]:
        """
        Получить заказ по ID платежа
        """
        try:
            order = self.repository.get_by_payment_id(db, payment_id)
            if not order:
                return None
            
            return OrderResponse.model_validate(order)
            
        except Exception as e:
            logger.error(f"Ошибка при получении заказа по payment_id {payment_id}: {str(e)}")
            raise
    
    def get_order_status(self, db: Session, order_id: int) -> Optional[OrderStatusResponse]:
        """
        Получить статус заказа
        """
        try:
            order = self.repository.get(db, order_id)
            if not order:
                return None
            
            return OrderStatusResponse(
                order_id=order.id,
                status=order.status,
                total_amount=order.total_amount,
                payment_id=order.payment_id
            )
            
        except Exception as e:
            logger.error(f"Ошибка при получении статуса заказа {order_id}: {str(e)}")
            raise
    
    def update_order_status(self, db: Session, order_id: int, status: str) -> bool:
        """
        Обновить статус заказа
        """
        try:
            order = self.repository.get(db, order_id)
            if not order:
                return False
            
            order.status = status
            # Поскольку мы работаем напрямую с ORM-объектом Order,
            # просто фиксируем изменения через сессию, не используя generic update
            db.add(order)
            db.commit()
            db.refresh(order)
            logger.info(f"Статус заказа {order_id} обновлен на {status}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса заказа {order_id}: {str(e)}")
            raise
    
    def update_payment_id(self, db: Session, order_id: int, payment_id: str) -> bool:
        """
        Обновить ID платежа для заказа
        """
        try:
            order = self.repository.get(db, order_id)
            if not order:
                return False
            
            order.payment_id = payment_id
            # Аналогично статусу, сохраняем изменения напрямую через сессию
            db.add(order)
            db.commit()
            db.refresh(order)
            logger.info(f"Payment ID {payment_id} добавлен к заказу {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении payment_id для заказа {order_id}: {str(e)}")
            raise
    
    def get_orders_by_email(self, db: Session, email: str, skip: int = 0, limit: int = 100) -> List[OrderResponse]:
        """
        Получить заказы по email
        """
        try:
            orders = self.repository.get_by_email(db, email, skip, limit)
            return [OrderResponse.model_validate(order) for order in orders]
            
        except Exception as e:
            logger.error(f"Ошибка при получении заказов для {email}: {str(e)}")
            raise
    
    def get_orders_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[OrderResponse]:
        """
        Получить заказы по статусу
        """
        try:
            orders = self.repository.get_by_status(db, status, skip, limit)
            return [OrderResponse.model_validate(order) for order in orders]
            
        except Exception as e:
            logger.error(f"Ошибка при получении заказов со статусом {status}: {str(e)}")
            raise
    
    def get_recent_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[OrderResponse]:
        """
        Получить последние заказы
        """
        try:
            orders = self.repository.get_recent_orders(db, skip, limit)
            return [OrderResponse.model_validate(order) for order in orders]
            
        except Exception as e:
            logger.error(f"Ошибка при получении последних заказов: {str(e)}")
            raise
    
    def get_orders_statistics(self, db: Session) -> dict:
        """
        Получить статистику заказов
        """
        try:
            total_orders = self.repository.get_orders_count(db)
            paid_orders = self.repository.get_orders_count_by_status(db, "paid")
            created_orders = self.repository.get_orders_count_by_status(db, "created")
            canceled_orders = self.repository.get_orders_count_by_status(db, "canceled")
            total_revenue = self.repository.get_total_revenue(db)
            
            return {
                "total_orders": total_orders,
                "paid_orders": paid_orders,
                "created_orders": created_orders,
                "canceled_orders": canceled_orders,
                "total_revenue": total_revenue
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики заказов: {str(e)}")
            raise

