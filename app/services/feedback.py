import asyncio
from typing import Optional
from ..schemas.feedback import FeedbackCreate
from ..core.exceptions import TelegramBotException
from ..utils.telegram import TelegramBot


class FeedbackService:
    """
    Сервис для работы с обратной связью
    """
    
    def __init__(self):
        self.telegram_bot = TelegramBot()
    
    async def send_feedback(self, feedback_data: FeedbackCreate) -> bool:
        """
        Отправить обратную связь в Telegram
        """
        try:
            # Формируем сообщение
            message = self._format_feedback_message(feedback_data)
            
            # Отправляем в Telegram
            await self.telegram_bot.send_message(message)
            
            return True
            
        except Exception as e:
            raise TelegramBotException(str(e))
    
    def _format_feedback_message(self, feedback: FeedbackCreate) -> str:
        """
        Форматирование сообщения обратной связи
        """
        message = f"🆕 Новая обратная связь\n\n"
        message += f"👤 Имя: {feedback.name}\n"
        message += f"📧 Email: {feedback.email}\n"
        
        if feedback.phone:
            message += f"📱 Телефон: {feedback.phone}\n"
        
        message += f"💬 Сообщение:\n{feedback.message}\n"
        
        return message
    
    async def send_test_message(self) -> bool:
        """
        Отправить тестовое сообщение в Telegram
        """
        try:
            message = "🧪 Тестовое сообщение от бекенда SOUTH CLUB"
            await self.telegram_bot.send_message(message)
            return True
        except Exception as e:
            raise TelegramBotException(str(e))

    async def send_telegram_message(self, message: str) -> bool:
        """
        Отправить произвольное сообщение в Telegram
        """
        try:
            await self.telegram_bot.send_message(message)
            return True
        except Exception as e:
            raise TelegramBotException(str(e))

