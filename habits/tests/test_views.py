from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from habits.models import Habit


class HabitAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )

        # Приятная привычка для user1
        self.pleasant_habit_user1 = Habit.objects.create(
            user=self.user1,
            action_place='Дома',
            action_time='20:00:00',
            action='Принять ванну',
            is_pleasant=True,
            duration=60,
        )

        # Приятная привычка для user2
        self.pleasant_habit_user2 = Habit.objects.create(
            user=self.user2,
            action_place='Дома',
            action_time='20:00:00',
            action='Посмотреть сериал',
            is_pleasant=True,
            duration=60,
        )

        # Полезные привычки user1 с reward
        self.habit1 = Habit.objects.create(
            user=self.user1,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать книгу',
            duration=60,
            reward='Кофе',
            is_public=False,
        )

        self.habit2 = Habit.objects.create(
            user=self.user1,
            action_place='Парк',
            action_time='18:00:00',
            action='Гулять',
            duration=90,
            reward='Мороженое',
            is_public=True,
        )

        # Полезная привычка user2 с related_habit (своей приятной привычкой)
        self.habit3 = Habit.objects.create(
            user=self.user2,
            action_place='Офис',
            action_time='12:00:00',
            action='Обед',
            duration=30,
            related_habit=self.pleasant_habit_user2,  # Используем приятную привычку user2
            is_public=False,
        )

        self.list_url = reverse('my-habits-list')
        self.public_list_url = reverse('public-habits-list')

    def test_get_habits_unauthenticated(self):
        """Тест получения списка привычек без аутентификации"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_habits_authenticated(self):
        """Тест получения списка привычек аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # user1 должен видеть habit1 и habit2, но не habit3 (другого пользователя)
        self.assertEqual(len(response.data['results']), 3)

        # Проверяем, что не видим привычки user2
        habit_actions = [habit['action'] for habit in response.data['results']]
        self.assertIn('Читать книгу', habit_actions)
        self.assertIn('Гулять', habit_actions)
        self.assertNotIn('Обед', habit_actions)

    def test_create_habit_authenticated(self):
        """Тест создания привычки аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)

        new_habit_data = {
            'action_place': 'Спортзал',
            'action_time': '19:00:00',
            'action': 'Тренировка',
            'duration': 90,
            'reward': 'Протеин',  # Добавляем reward
        }

        response = self.client.post(self.list_url, new_habit_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Тренировка')
        self.assertEqual(response.data['user'], self.user1.id)

        # Проверяем, что привычка создана в БД
        self.assertTrue(Habit.objects.filter(action='Тренировка').exists())

    def test_create_habit_with_related(self):
        """Тест создания привычки со связанной привычкой"""
        self.client.force_authenticate(user=self.user1)

        new_habit_data = {
            'action_place': 'Дома',
            'action_time': '21:00:00',
            'action': 'Йога',
            'duration': 60,
            'related_habit': self.pleasant_habit_user1.id,  # Используем приятную привычку user1
        }

        response = self.client.post(self.list_url, new_habit_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['related_habit'], self.pleasant_habit_user1.id)

    def test_create_pleasant_habit(self):
        """Тест создания приятной привычки"""
        self.client.force_authenticate(user=self.user1)

        new_habit_data = {
            'action_place': 'Дома',
            'action_time': '22:00:00',
            'action': 'Медитация',
            'duration': 120,
            'is_pleasant': True,  # Приятная привычка
        }

        response = self.client.post(self.list_url, new_habit_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_pleasant'])
        # Приятная привычка не должна иметь reward
        self.assertEqual(response.data['reward'], '')

    def test_get_public_habits_unauthenticated(self):
        """Тест получения публичных привычек без аутентификации"""
        response = self.client.get(self.public_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть только публичные привычки (habit2)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['action'], 'Гулять')


class HabitPermissionTests(APITestCase):
    """Тесты для проверки прав доступа"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )

        self.habit = Habit.objects.create(
            user=self.user1,
            action_place='Дома',
            action_time='09:00:00',
            action='Привычка',
            duration=60,
            reward='Награда',  # Добавляем reward
            is_public=False,
        )

        self.list_url = reverse('my-habits-list')
        self.detail_url = reverse('my-habits-detail', args=[self.habit.id])

    def test_cannot_access_others_habits_via_detail(self):
        """Тест, что нельзя получить детали чужой приватной привычки"""
        other_user = User.objects.create_user(
            username='other',
            password='password123'
        )

        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
