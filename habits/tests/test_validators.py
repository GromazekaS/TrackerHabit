from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from habits.models import Habit


class HabitValidatorsTests(TestCase):
    """Тесты для валидаторов привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Принять ванну',
            is_pleasant=True,
            duration=60,
        )

    def test_validation_errors(self):
        """Тест всех валидаций в одном тесте"""
        # Базовые данные для всех тестовых случаев
        base_data = {
            'user': self.user,
            'action_place': 'Дома',
            'action_time': '09:00:00',
            'action': 'Тест',
            'duration': 60,
        }

        test_cases = [
            # (описание, дополнительные_данные, ожидаемое_поле_ошибки)
            ("duration > 120", {'duration': 150}, 'duration'),
            ("и related_habit и reward",
             {'related_habit': self.pleasant_habit, 'reward': 'Шоколадка'},
             ['related_habit', 'reward']),
            ("полезная привычка без related_habit и reward",
             {'is_pleasant': False, 'related_habit': None, 'reward': ''},
             ['related_habit', 'reward']),
            ("приятная привычка с reward",
             {'is_pleasant': True, 'reward': 'Шоколадка'},
             'reward'),
        ]

        for description, extra_data, expected_error in test_cases:
            with self.subTest(description):
                # Создаем копию базовых данных и добавляем/обновляем тестовыми данными
                habit_data = base_data.copy()
                habit_data.update(extra_data)

                habit = Habit(**habit_data)

                with self.assertRaises(ValidationError) as context:
                    habit.full_clean()

                if isinstance(expected_error, list):
                    for field in expected_error:
                        self.assertIn(field, context.exception.message_dict)
                else:
                    self.assertIn(expected_error, context.exception.message_dict)

    def test_successful_habit_creation(self):
        """Тест успешного создания привычек"""
        # Полезная привычка с reward
        habit1 = Habit(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать',
            is_pleasant=False,
            duration=60,
            reward='Кофе'
        )
        habit1.full_clean()  # Не должно вызывать ошибку
        habit1.save()  # Сохраняем в БД для дальнейших тестов

        # Полезная привычка с related_habit
        habit2 = Habit(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Гулять',
            is_pleasant=False,
            duration=90,
            related_habit=self.pleasant_habit
        )
        habit2.full_clean()  # Не должно вызывать ошибку

        # Приятная привычка
        habit3 = Habit(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Ванна',
            is_pleasant=True,
            duration=60
        )
        habit3.full_clean()  # Не должно вызывать ошибку

    def test_habit_self_reference(self):
        """Тест: привычка не может ссылаться сама на себя"""
        # Сначала создаем и сохраняем привычку
        habit = Habit.objects.create(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Тест',
            duration=60,
            is_pleasant=False,
            reward='Награда'
        )

        # Пытаемся связать привычку саму с собой
        habit.related_habit = habit
        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('related_habit', context.exception.message_dict)

    def test_cross_user_habit_reference(self):
        """Тест: нельзя ссылаться на привычку другого пользователя"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass'
        )

        other_pleasant_habit = Habit.objects.create(
            user=other_user,
            action_place='Дома',
            action_time='09:00:00',
            action='Приятная привычка другого пользователя',
            is_pleasant=True,
            duration=60,
        )

        habit = Habit(
            user=self.user,
            action_place='Дома',
            action_time='09:00:00',
            action='Тест',
            duration=60,
            related_habit=other_pleasant_habit
        )

        with self.assertRaises(ValidationError) as context:
            habit.full_clean()

        self.assertIn('related_habit', context.exception.message_dict)