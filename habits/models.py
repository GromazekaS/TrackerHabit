from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


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
    frequency = models.PositiveSmallIntegerField(
        choices=FREQUENCY_CHOICES,
        default=1,
        verbose_name='Периодичность (дней)',
        validators = [MinValueValidator(1), MaxValueValidator(7)]
    )
    duration = models.PositiveIntegerField(
        verbose_name='Время на выполнение (секунды)',
        help_text='Не более 120 секунд',
        validators=[MaxValueValidator(120)]
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка'
    )
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
        """Валидации по ТЗ"""
        errors = {}

        # 2. Проверка: либо related_habit, либо reward, но не оба одновременно
        if self.related_habit and self.reward:
            errors['related_habit'] = 'Нельзя одновременно указывать связанную привычку и вознаграждение.'
            errors['reward'] = 'Нельзя одновременно указывать связанную привычку и вознаграждение.'

        # 3. Проверка: связанная привычка должна быть приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            errors['related_habit'] = 'Связанная привычка должна быть приятной (is_pleasant=True).'

        # 4. Проверка: у приятной привычки не может быть связанной привычки или вознаграждения
        if self.is_pleasant:
            if self.related_habit:
                errors['related_habit'] = 'У приятной привычки не может быть связанной привычки.'
            if self.reward:
                errors['reward'] = 'У приятной привычки не может быть вознаграждения.'

        # 5. Проверка: связанная привычка не может ссылаться сама на себя
        if self.related_habit and self.related_habit.id == self.id:
            errors['related_habit'] = 'Привычка не может быть связана сама с собой.'

        # 6. Проверка: связанная привычка должна принадлежать тому же пользователю
        if self.related_habit and self.related_habit.user != self.user:
            errors['related_habit'] = 'Связанная привычка должна принадлежать вам.'

        # 7. Проверка: для полезной привычки должно быть либо вознаграждение, либо связанная привычка
        if not self.is_pleasant and not self.related_habit and not self.reward:
            errors['related_habit'] = 'Для полезной привычки укажите либо связанную привычку, либо вознаграждение.'
            errors['reward'] = 'Для полезной привычки укажите либо связанную привычку, либо вознаграждение.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)