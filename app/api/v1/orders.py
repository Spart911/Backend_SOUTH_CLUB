from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import ipaddress

from ...dependencies import get_db_session
from ...schemas.order import (
    OrderCreate, OrderResponse, OrderStatusResponse, 
    PaymentResponse, YooKassaNotification
)
from ...services.order import OrderService
from ...services.payment import PaymentService
from ...services.feedback import FeedbackService
from ...core.logging import get_logger
from ...config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

# Инициализация сервисов
order_service = OrderService()
payment_service = PaymentService()
feedback_service = FeedbackService()

# IP-адреса ЮKassa для проверки webhook'ов
YOOKASSA_IPS = [
    ipaddress.ip_network("185.71.76.0/27"),
    ipaddress.ip_network("185.71.77.0/27"),
    ipaddress.ip_network("77.75.153.0/25"),
    ipaddress.ip_network("77.75.156.11/32"),
    ipaddress.ip_network("77.75.156.35/32"),
    ipaddress.ip_network("77.75.154.128/25"),
    ipaddress.ip_network("2a02:5180::/32"),
]


def get_client_ip(request: Request) -> str:
    """
    Получает реальный IP адрес клиента из заголовков.
    Сначала проверяет X-Forwarded-For, затем X-Real-IP, затем request.client.host
    """
    # X-Forwarded-For может содержать цепочку IP, разделенных запятыми
    # Первый IP - оригинальный клиент
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Берем первый IP из цепочки
        real_ip = x_forwarded_for.split(",")[0].strip()
        return real_ip

    # X-Real-IP (для Nginx)
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()

    # Fallback на client.host
    return request.client.host


def is_yookassa_ip(ip: str) -> bool:
    """Проверяет, принадлежит ли IP-адрес ЮKassa"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return any(ip_obj in network for network in YOOKASSA_IPS)
    except ValueError:
        return False


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED,
             summary="Создать заказ", 
             description="Создает новый заказ и инициирует платеж через ЮKassa. Возвращает токен подтверждения для встраиваемого виджета.")
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db_session)
):
    """
    Создать новый заказ с оплатой через ЮKassa
    """
    try:
        logger.info(f"Создание заказа для {order_data.email}")
        
        # Создаем заказ в базе данных
        order = order_service.create_order(db, order_data)
        
        # Создаем платеж в ЮKassa
        payment_data = payment_service.create_payment(
            order_id=order.id,
            amount=order.total_amount,
            description=f"Заказ №{order.id}",
            customer_email=order.email,
            customer_phone=order.phone,
            items=order.items,
        )
        
        # Обновляем заказ с ID платежа
        order_service.update_payment_id(db, order.id, payment_data["payment_id"])
        
        logger.info(f"Заказ {order.id} создан, платеж {payment_data['payment_id']} инициирован")
        
        return PaymentResponse(
            order_id=order.id,
            confirmation_token=payment_data["confirmation_token"]
        )
        
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании заказа"
        )


@router.get("/{order_id}", response_model=OrderResponse,
            summary="Получить заказ", 
            description="Возвращает полную информацию о заказе по его ID.")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Получить заказ по ID
    """
    try:
        order = order_service.get_order(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении заказа {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении заказа"
        )


@router.get("/{order_id}/status", response_model=OrderStatusResponse,
            summary="Получить статус заказа", 
            description="Возвращает текущий статус заказа и ID платежа.")
async def get_order_status(
    order_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Получить статус заказа
    """
    try:
        order_status = order_service.get_order_status(db, order_id)
        if not order_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )
        
        return order_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении статуса заказа {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статуса заказа"
        )


@router.get("/email/{email}", response_model=List[OrderResponse],
            summary="Получить заказы по email", 
            description="Возвращает список заказов для указанного email адреса.")
async def get_orders_by_email(
    email: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    Получить заказы по email
    """
    try:
        orders = order_service.get_orders_by_email(db, email, skip, limit)
        return orders
        
    except Exception as e:
        logger.error(f"Ошибка при получении заказов для {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении заказов"
        )


@router.post("/webhook", status_code=status.HTTP_200_OK,
             summary="Webhook ЮKassa", 
             description="Обрабатывает уведомления от ЮKassa о статусе платежей.")
async def yookassa_webhook(
    request: Request,
    notification: YooKassaNotification,
    db: Session = Depends(get_db_session)
):
    """
    Обработка webhook от ЮKassa
    """
    try:
        # Проверка IP-адреса
        client_ip = get_client_ip(request)
        logger.info(f"Webhook IP check: client_ip={client_ip}, X-Forwarded-For={request.headers.get('X-Forwarded-For')}, X-Real-IP={request.headers.get('X-Real-IP')}")

        if not is_yookassa_ip(client_ip):
            logger.warning(f"Получен webhook с неавторизованного IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Неавторизованный IP"
            )
        
        logger.info(f"Получен webhook: {notification.event} для платежа {notification.object.get('id')}")
        
        # Обработка различных событий
        if notification.event == "payment.succeeded":
            payment_id = notification.object.get("id")
            if payment_id:
                # Получаем заказ по ID платежа
                order = order_service.get_order_by_payment_id(db, payment_id)
                if order:
                    # Проверяем статус платежа через API
                    payment_status = payment_service.get_payment_status(payment_id)
                    if payment_status and payment_status["status"] == "succeeded":
                        # Обновляем статус заказа
                        order_service.update_order_status(db, order.id, "paid")
                        
                        # Отправляем уведомление в Telegram
                        try:
                            items_text = "\n".join([
                                f"- {item['name']} x{item['quantity']} ({item['price']} руб.)" 
                                for item in order.items
                            ])
                            
                            message = (
                                f"✅ <b>Оплачен заказ №{order.id}</b>\n\n"
                                f"💰 <b>Сумма:</b> {order.total_amount} руб.\n"
                                f"📧 <b>Email:</b> {order.email}\n"
                                f"📱 <b>Телефон:</b> {order.phone}\n"
                                f"📍 <b>Адрес:</b> {order.address}\n"
                                f"🕒 <b>Время доставки:</b> {order.delivery_time}\n"
                                f"⏰ <b>Время заказа:</b> {order.order_time}\n\n"
                                f"📋 <b>Состав заказа:</b>\n{items_text}"
                            )
                            
                            await feedback_service.send_telegram_message(message)
                            logger.info(f"Уведомление в Telegram отправлено для заказа {order.id}")
                            
                        except Exception as e:
                            logger.error(f"Ошибка при отправке уведомления в Telegram: {str(e)}")
        
        elif notification.event == "payment.waiting_for_capture":
            logger.info(f"Платеж {notification.object.get('id')} ожидает подтверждения")
            
        elif notification.event == "payment.canceled":
            payment_id = notification.object.get("id")
            if payment_id:
                order = order_service.get_order_by_payment_id(db, payment_id)
                if order:
                    order_service.update_order_status(db, order.id, "canceled")
                    logger.info(f"Заказ {order.id} отменен")
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке webhook"
        )


@router.get("/", response_model=List[OrderResponse],
            summary="Получить все заказы", 
            description="Возвращает список всех заказов (для админа).")
async def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    Получить все заказы (для админа)
    """
    try:
        orders = order_service.get_recent_orders(db, skip, limit)
        return orders
        
    except Exception as e:
        logger.error(f"Ошибка при получении всех заказов: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении заказов"
        )


@router.get("/statistics/summary", 
            summary="Получить статистику заказов", 
            description="Возвращает статистику по заказам (для админа).")
async def get_orders_statistics(
    db: Session = Depends(get_db_session)
):
    """
    Получить статистику заказов
    """
    try:
        stats = order_service.get_orders_statistics(db)
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики заказов: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статистики"
        )

