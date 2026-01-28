from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from habits.models import Habit


class HabitModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        # Создаем приятную привычку для использования в связанных
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='10:00:00',
            action='Принять ванну',
            is_pleasant=True,
            duration=60,
        )

    def test_create_habit(self):
        """Тест создания полезной привычки с вознаграждением"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать книгу',
            is_pleasant=False,
            frequency=1,
            duration=60,
            reward='Кофе',  # Добавляем вознаграждение
            is_public=False,
        )

        self.assertEqual(habit.user.username, 'testuser')
        self.assertEqual(habit.action, 'Читать книгу')
        self.assertEqual(habit.reward, 'Кофе')
        self.assertFalse(habit.is_pleasant)

    def test_create_pleasant_habit(self):
        """Тест создания приятной привычки (без вознаграждения)"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='11:00:00',
            action='Слушать музыку',
            is_pleasant=True,  # Приятная привычка
            duration=60,
        )

        self.assertTrue(habit.is_pleasant)
        self.assertEqual(habit.reward, '')
        self.assertIsNone(habit.related_habit)

    def test_create_habit_with_related(self):
        """Тест создания привычки со связанной привычкой"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Гулять',
            is_pleasant=False,
            related_habit=self.pleasant_habit,  # Используем приятную привычку
            duration=90,
        )

        self.assertEqual(habit.related_habit, self.pleasant_habit)
        self.assertFalse(habit.is_pleasant)

    def test_habit_string_representation(self):
        """Тест строкового представления привычки"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать книгу',
            is_pleasant=False,
            reward='Чай',
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
            is_pleasant=False,
            reward='Тест',
            duration=150,  # Больше 120 секунд
        )

        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_habit_default_values(self):
        """Тест значений по умолчанию для приятной привычки"""
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Тест',
            is_pleasant=True,  # Приятная привычка не требует reward
            duration=60,
        )

        self.assertTrue(habit.is_pleasant)
        self.assertEqual(habit.frequency, 1)
        self.assertFalse(habit.is_public)
        self.assertEqual(habit.reward, '')
