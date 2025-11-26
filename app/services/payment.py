import yookassa
from yookassa import Payment
from ..config import settings
from ..core.logging import get_logger
import uuid
from typing import Dict, Any, Optional, List
from decimal import Decimal, ROUND_HALF_UP

logger = get_logger(__name__)


class PaymentService:
    """Сервис для работы с платежами ЮKassa"""
    
    def __init__(self):
        # Настройка ЮKassa
        yookassa.Configuration.account_id = settings.yookassa_shop_id
        yookassa.Configuration.secret_key = settings.yookassa_secret_key
    
    def create_payment(
        self,
        order_id: int,
        amount: float,
        description: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Создать платеж в ЮKassa
        
        Args:
            order_id: ID заказа
            amount: Сумма платежа
            description: Описание платежа
            
        Returns:
            Словарь с данными платежа
        """
        try:
            if not description:
                description = f"Заказ №{order_id}"
            
            # Генерируем уникальный ключ идемпотентности
            idempotence_key = str(uuid.uuid4())
            
            # Данные для создания платежа
            payment_data = {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "embedded"  # Для встраиваемого виджета
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "order_id": str(order_id)
                }
            }

            # Добавляем чек (receipt), если есть данные о клиенте/товарах
            receipt: Dict[str, Any] = {}

            # Данные покупателя
            customer: Dict[str, str] = {}
            if customer_email:
                customer["email"] = customer_email
            if customer_phone:
                customer["phone"] = customer_phone
            if customer:
                receipt["customer"] = customer

            # Позиции чека
            # Формируем позиции исходя из товаров заказа
            # и рассчитываем общую сумму по чеку, чтобы она совпадала с суммой платежа
            items_total = Decimal("0.00")

            if items:
                receipt_items: List[Dict[str, Any]] = []
                for item in items:
                    try:
                        name = str(item.get("name", "Товар"))[:128]
                        quantity = Decimal(str(item.get("quantity", 1)))
                        price_per_unit = Decimal(str(item.get("price", amount)))
                    except Exception:
                        # Если данные кривые, просто пропускаем позицию
                        continue

                    # Сумма по позиции = цена * количество, с округлением до копеек
                    line_total = (price_per_unit * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    items_total += line_total

                    receipt_items.append({
                        "description": name,
                        # Количество ЮKassa принимает как число, но мы приводим к float для сериализации
                        "quantity": float(quantity),
                        "amount": {
                            # В чеке указывается цена за единицу
                            "value": str(price_per_unit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                            "currency": "RUB"
                        },
                        # 1 = без НДС (подходит для упрощёнки, при необходимости поменяй под свою схему)
                        "vat_code": 1
                    })

                if receipt_items:
                    receipt["items"] = receipt_items

            # Если по чеку что-то насчитали, синхронизируем сумму платежа с суммой по чеку
            if items and items_total > 0:
                # Логгируем расхождение для отладки
                expected = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if items_total != expected:
                    logger.warning(
                        f"Сумма по чеку ({items_total}) не совпадает с amount ({expected}) для заказа {order_id}. "
                        f"Используем сумму по чеку."
                    )
                payment_data["amount"]["value"] = str(items_total)

            if receipt:
                payment_data["receipt"] = receipt
            
            # Создаем платеж
            payment = Payment.create(payment_data, idempotence_key)
            
            logger.info(f"Создан платеж {payment.id} для заказа {order_id} на сумму {amount} руб.")
            
            return {
                "payment_id": payment.id,
                "confirmation_token": payment.confirmation.confirmation_token,
                "status": payment.status,
                "amount": payment.amount.value,
                "currency": payment.amount.currency
            }
            
        except Exception as e:
            # пробуем вытащить тело ответа
            extra = ""
            try:
                # у ошибок SDK ЮKassa обычно есть .response или .args с JSON
                if hasattr(e, "response") and hasattr(e.response, "text"):
                    extra = f" YooKassa response: {e.response.text}"
                elif e.args:
                    extra = f" Details: {e.args!r}"
            except Exception:
                pass

            logger.error(
                f"Ошибка при создании платежа для заказа {order_id}: {e}{extra}"
            )
            raise
    
    def get_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить статус платежа
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Словарь с данными платежа или None
        """
        try:
            payment = Payment.find_one(payment_id)
            
            return {
                "payment_id": payment.id,
                "status": payment.status,
                "amount": payment.amount.value,
                "currency": payment.amount.currency,
                "description": payment.description,
                "metadata": payment.metadata
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статуса платежа {payment_id}: {str(e)}")
            return None
    
    def cancel_payment(self, payment_id: str) -> bool:
        """
        Отменить платеж
        
        Args:
            payment_id: ID платежа
            
        Returns:
            True если успешно отменен, False иначе
        """
        try:
            payment = Payment.cancel(payment_id)
            
            if payment.status == "canceled":
                logger.info(f"Платеж {payment_id} успешно отменен")
                return True
            else:
                logger.warning(f"Не удалось отменить платеж {payment_id}, статус: {payment.status}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при отмене платежа {payment_id}: {str(e)}")
            return False
    
    def process_webhook(self, notification_data: Dict[str, Any]) -> bool:
        """
        Обработать webhook от ЮKassa
        
        Args:
            notification_data: Данные уведомления
            
        Returns:
            True если успешно обработано, False иначе
        """
        try:
            notification_type = notification_data.get("type")
            event = notification_data.get("event")
            payment_object = notification_data.get("object", {})
            
            if notification_type != "notification":
                logger.warning(f"Неизвестный тип уведомления: {notification_type}")
                return False
            
            payment_id = payment_object.get("id")
            status = payment_object.get("status")
            
            logger.info(f"Получено уведомление: {event} для платежа {payment_id} со статусом {status}")
            
            # Здесь можно добавить дополнительную логику обработки
            # в зависимости от типа события
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {str(e)}")
            return False

