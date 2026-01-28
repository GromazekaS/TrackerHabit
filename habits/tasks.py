from celery import shared_task
from django.utils import timezone
from .models import Habit
from .telegram_bot import TelegramBotService  # Убедитесь, что это новая синхронная версия
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_reminders():
    """Задача для отправки напоминаний о привычках по расписанию."""

    now = timezone.localtime()
    current_time = now.replace(second=0, microsecond=0)

    logger.info(f"=== Запуск задачи в {current_time.strftime('%H:%M:%S')} ===")

    # Находим привычки, которые должны быть выполнены в эту минуту
    habits_to_remind = Habit.objects.filter(
        action_time__hour=current_time.hour,
        action_time__minute=current_time.minute,
        user__profile__telegram_chat_id__isnull=False
    ).select_related('user__profile')

    logger.info(f"Найдено привычек: {habits_to_remind.count()}")

    if not habits_to_remind:
        logger.info("Нет привычек для напоминания в это время.")
        return

    # Инициализируем сервис ОДИН раз
    bot_service = TelegramBotService()

    for habit in habits_to_remind:
        logger.info(f"Обработка привычки: {habit.action} в {habit.action_time}")
        logger.info(f"Chat ID пользователя: {habit.user.profile.telegram_chat_id}")

        # Проверка периодичности
        days_since_creation = (now.date() - habit.created_at.date()).days
        logger.info(f"Дней с создания: {days_since_creation}, частота: {habit.frequency}")

        if days_since_creation % habit.frequency != 0:
            logger.info("Пропуск: не подходит по периодичности")
            continue

        # Формируем сообщение
        chat_id = habit.user.profile.telegram_chat_id
        message = (
            f"⏰ Напоминание о привычке!\n"
            f"Я буду <b>{habit.action}</b> в <b>{habit.action_time.strftime('%H:%M')}</b> "
            f"в <b>{habit.action_place}</b>.\n"
            f"Время на выполнение: {habit.duration} сек."
        )

        # ОТПРАВЛЯЕМ СООБЩЕНИЕ - только один вызов
        logger.info(f"Вызываем bot_service.send_reminder() для чата {chat_id}")

        # Прямой вызов синхронного метода
        success = bot_service.send_reminder(chat_id, message)

        if success:
            logger.info("✅ Сообщение отправлено успешно (из Celery)")
        else:
            logger.error("❌ Ошибка отправки сообщения (из Celery)")

    logger.info("=== Задача завершена ===")
