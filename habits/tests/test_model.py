from django.test import TestCase
from django.contrib.auth.models import User
from habits.models import Habit


class HabitModelTests(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать книгу',
            is_pleasant=False,
            frequency=1,
            duration=60,
            is_public=False,
        )

        self.assertEqual(habit.user.username, 'testuser')
        self.assertEqual(habit.action, 'Читать книгу')
        self.assertEqual(habit.duration, 60)
        self.assertFalse(habit.is_pleasant)
        self.assertFalse(habit.is_public)

    def test_habit_string_representation(self):
        """Тест строкового представления привычки"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать книгу',
            duration=60,
        )

        expected_str = f"Я буду {habit.action} в {habit.action_time} в {habit.action_place}"
        self.assertEqual(str(habit), expected_str)

    def test_habit_duration_validation(self):
        """Тест валидации времени выполнения"""
        # Создаем привычку с duration > 120
        habit = Habit(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Тест',
            duration=150,  # Больше 120 секунд
        )

        # Должна возникнуть ошибка валидации
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_habit_default_values(self):
        """Тест значений по умолчанию"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Тест',
            duration=60,
        )

        self.assertFalse(habit.is_pleasant)
        self.assertEqual(habit.frequency, 1)  # Ежедневно по умолчанию
        self.assertFalse(habit.is_public)
        self.assertEqual(habit.reward, '')