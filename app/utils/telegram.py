import aiohttp
from typing import Optional
from ..config import settings


class TelegramBot:
    """
    Класс для работы с Telegram Bot API
    """
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_message(self, message: str) -> bool:
        """
        Отправить сообщение в Telegram
        """
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot token или chat ID не настроены")
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("ok", False)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ошибка отправки: {response.status} - {error_text}")
                        
        except Exception as e:
            raise Exception(f"Ошибка отправки в Telegram: {str(e)}")
    
    async def send_photo(self, photo_path: str, caption: Optional[str] = None) -> bool:
        """
        Отправить фотографию в Telegram
        """
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot token или chat ID не настроены")
        
        url = f"{self.base_url}/sendPhoto"
        data = {"chat_id": self.chat_id}
        
        if caption:
            data["caption"] = caption
        
        try:
            async with aiohttp.ClientSession() as session:
                with open(photo_path, "rb") as photo_file:
                    files = {"photo": photo_file}
                    async with session.post(url, data=data, files=files) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result.get("ok", False)
                        else:
                            error_text = await response.text()
                            raise Exception(f"Ошибка отправки фото: {response.status} - {error_text}")
                            
        except Exception as e:
            raise Exception(f"Ошибка отправки фото в Telegram: {str(e)}")
    
    async def get_me(self) -> Optional[dict]:
        """
        Получить информацию о боте
        """
        if not self.bot_token:
            raise ValueError("Telegram bot token не настроен")
        
        url = f"{self.base_url}/getMe"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result") if result.get("ok") else None
                    else:
                        return None
                        
        except Exception:
            return None
    
    def is_configured(self) -> bool:
        """
        Проверить, настроен ли бот
        """
        return bool(self.bot_token and self.chat_id)

