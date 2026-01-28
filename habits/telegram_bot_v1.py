import logging
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Сервис для работы с Telegram Bot API."""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.bot = Bot(token=self.token)

    async def send_reminder(self, chat_id: str, message: str):
        """Асинхронная отправка напоминания."""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Напоминание отправлено в чат {chat_id}")
        except TelegramError as e:
            logger.error(f"Ошибка отправки в чат {chat_id}: {e}")

    # Синхронная обёртка для использования из Celery
    def send_reminder_sync(self, chat_id: str, message: str):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.send_reminder(chat_id, message))
        finally:
            loop.close()
