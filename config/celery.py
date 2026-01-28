# config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Установите переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Используем настройки Django для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

# Для Windows используем eventlet/gevent пул
app.conf.worker_pool = 'eventlet'

# Периодические задачи
app.conf.beat_schedule = {
    'send-habit-reminders': {
        'task': 'habits.tasks.send_scheduled_reminders',
        'schedule': 60.0,  # Каждые 60 секунд
    },
}