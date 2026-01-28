from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    telegram_chat_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Telegram Chat ID'
    )
    # При необходимости добавьте другие поля (например, подписку на уведомления)

    def __str__(self):
        return f'{self.user.username} - {self.telegram_chat_id}'
