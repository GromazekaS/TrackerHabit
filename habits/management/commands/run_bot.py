from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запускает Telegram-бота в режиме Polling'

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start. Показывает chat_id."""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)

        # Безопасное получение имени пользователя
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = user.username or "пользователь"

        # Простой текст без Markdown
        message_text = (
            f"Привет, {full_name}!\n"
            f"Твой ID чата: {chat_id}\n\n"
            "Чтобы получать напоминания о привычках:\n"
            "1. Зарегистрируйся в трекере привычек\n"
            "2. В настройках профиля введи этот chat_id\n"
            "3. Настрой привычки с временем выполнения\n\n"
            "Напоминания будут приходиться автоматически!"
        )

        await update.message.reply_text(message_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help."""
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start - показать ID чата для привязки\n"
            "/help - эта справка"
        )

    def handle(self, *args, **options):
        """Основной метод запуска бота."""
        try:
            application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

            # Регистрация обработчиков
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help_command))

            # Добавляем обработчик ошибок
            application.add_error_handler(self.error_handler)

            self.stdout.write(self.style.SUCCESS('Бот запущен...'))
            application.run_polling()
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок."""
        logger.error(f"Ошибка при обработке обновления: {context.error}")

        try:
            # Отправляем сообщение об ошибке пользователю
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Произошла ошибка при обработке команды. Попробуйте позже."
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")
