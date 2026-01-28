from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Habit(models.Model):
    """Модель привычки"""

    FREQUENCY_CHOICES = [
        (1, 'Ежедневно'),
        (2, 'Каждые 2 дня'),
        (3, 'Каждые 3 дня'),
        (4, 'Каждые 4 дня'),
        (5, 'Каждые 5 дней'),
        (6, 'Каждые 6 дней'),
        (7, 'Еженедельно'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='Пользователь')
    action = models.CharField(max_length=500, verbose_name='Действие')
    action_place = models.CharField(max_length=255, verbose_name='Место выполнения')
    action_time = models.TimeField(verbose_name='Время выполнения')
    frequency = models.PositiveSmallIntegerField(choices=FREQUENCY_CHOICES, default=1, verbose_name='Периодичность (дней)')
    duration = models.PositiveIntegerField(verbose_name='Время на выполнение (секунды)', help_text='Не более 120 секунд')

    related_habit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Связанная привычка')
    reward = models.CharField(max_length=255, blank=True, verbose_name='Вознаграждение')
    # Флаги
    is_pleasant = models.BooleanField(default=False, verbose_name='Приятная привычка')
    is_public = models.BooleanField(default=False, verbose_name='Публичная привычка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['action_time']

    def __str__(self):
        return f"Я буду {self.action} в {self.action_time} в {self.action_place}"

    def clean(self):
        """Базовые валидации (позже расширим)"""
        if self.duration > 120:
            raise ValidationError(
                {'duration': 'Время выполнения не должно превышать 120 секунд'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)