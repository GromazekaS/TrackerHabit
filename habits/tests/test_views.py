from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from habits.models import Habit


class HabitAPITests(APITestCase):
    """Тесты для API привычек"""

    def setUp(self):
        # Создаем двух пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )

        # Создаем привычки для user1
        self.habit1 = Habit.objects.create(
            user=self.user1,
            action_place='Дома',
            action_time='09:00:00',
            action='Читать книгу',
            duration=60,
            is_public=False,
        )

        self.habit2 = Habit.objects.create(
            user=self.user1,
            action_place='Парк',
            action_time='18:00:00',
            action='Гулять',
            duration=90,
            is_public=True,  # Публичная привычка
        )

        # Создаем привычку для user2
        self.habit3 = Habit.objects.create(
            user=self.user2,
            action_place='Офис',
            action_time='12:00:00',
            action='Обед',
            duration=30,
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
        self.assertEqual(len(response.data['results']), 2)  # Только привычки user1

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
        }

        response = self.client.post(self.list_url, new_habit_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Тренировка')
        self.assertEqual(response.data['user'], self.user1.id)

        # Проверяем, что привычка создана в БД
        self.assertTrue(Habit.objects.filter(action='Тренировка').exists())

    def test_create_habit_unauthenticated(self):
        """Тест создания привычки без аутентификации"""
        new_habit_data = {
            'action_place': 'Спортзал',
            'action_time': '19:00:00',
            'action': 'Тренировка',
            'duration': 90,
        }

        response = self.client.post(self.list_url, new_habit_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_habit_owner(self):
        """Тест обновления привычки владельцем"""
        self.client.force_authenticate(user=self.user1)

        update_data = {
            'action': 'Читать 30 минут',
            'duration': 120,
        }

        detail_url = reverse('my-habits-detail', args=[self.habit1.id])
        response = self.client.patch(detail_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'Читать 30 минут')

        # Обновляем объект из БД
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.action, 'Читать 30 минут')
        self.assertEqual(self.habit1.duration, 120)

    def test_update_habit_not_owner(self):
        """Тест обновления привычки не владельцем"""
        self.client.force_authenticate(user=self.user2)  # user2 пытается обновить привычку user1

        update_data = {'action': 'Измененное действие'}
        detail_url = reverse('my-habits-detail', args=[self.habit1.id])
        response = self.client.patch(detail_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_habit_owner(self):
        """Тест удаления привычки владельцем"""
        self.client.force_authenticate(user=self.user1)

        detail_url = reverse('my-habits-detail', args=[self.habit1.id])
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit1.id).exists())

    def test_delete_habit_not_owner(self):
        """Тест удаления привычки не владельцем"""
        self.client.force_authenticate(user=self.user2)

        detail_url = reverse('my-habits-detail', args=[self.habit1.id])
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Habit.objects.filter(id=self.habit1.id).exists())

    def test_get_public_habits_unauthenticated(self):
        """Тест получения публичных привычек без аутентификации"""
        response = self.client.get(self.public_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть только публичные привычки
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['action'], 'Гулять')

    def test_pagination(self):
        """Тест пагинации в списке привычек"""
        self.client.force_authenticate(user=self.user1)

        # Создаем еще несколько привычек для теста пагинации
        for i in range(10):
            Habit.objects.create(
                user=self.user1,
                action_place=f'Место {i}',
                action_time='09:00:00',
                action=f'Действие {i}',
                duration=60,
            )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

        # По умолчанию page_size = 5
        self.assertEqual(len(response.data['results']), 5)

    def test_habit_detail_view(self):
        """Тест получения деталей привычки"""
        self.client.force_authenticate(user=self.user1)

        detail_url = reverse('my-habits-detail', args=[self.habit1.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.habit1.id)
        self.assertEqual(response.data['action'], 'Читать книгу')


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