import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Упрощенный синхронный сервис для работы с Telegram Bot API через requests."""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_reminder(self, chat_id: str, message: str):
        """Синхронная отправка напоминания через requests."""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()  # Выбросит исключение при ошибке HTTP

            logger.info(f"✅ Напоминание отправлено в чат {chat_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            return False


# Устаревший метод для обратной совместимости
def send_reminder_sync(chat_id: str, message: str):
    service = TelegramBotService()
    return service.send_reminder(chat_id, message)