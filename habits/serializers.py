from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычки"""

    class Meta:
        model = Habit
        fields = [
            'id',
            'user',
            'action',
            'action_place',
            'action_time',

            'is_pleasant',
            'related_habit',
            'frequency',
            'reward',
            'duration',
            'is_public',
            'created_at',
        ]
        read_only_fields = ['user', 'created_at']
