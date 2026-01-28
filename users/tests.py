from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    """Тесты для регистрации и аутентификации"""

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'password2': 'TestPass123',
        }

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

        # Проверяем, что пользователь создан в БД
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_passwords_not_match(self):
        """Тест регистрации с несовпадающими паролями"""
        data = self.valid_user_data.copy()
        data['password2'] = 'DifferentPass123'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_existing_username(self):
        """Тест регистрации с существующим именем пользователя"""
        # Создаем пользователя
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='password123'
        )

        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_login_success(self):
        """Тест успешного входа"""
        # Создаем пользователя
        User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )

        login_data = {
            'username': 'testuser',
            'password': 'TestPass123',
        }

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_wrong_credentials(self):
        """Тест входа с неверными учетными данными"""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass',
        }

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(APITestCase):
    """Тесты для обновления токена"""

    def setUp(self):
        self.refresh_url = reverse('token_refresh')

        # Создаем пользователя и получаем refresh токен
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )

        login_data = {
            'username': 'testuser',
            'password': 'TestPass123',
        }

        login_response = self.client.post(reverse('login'), login_data)
        self.refresh_token = login_response.data['refresh']

    def test_token_refresh_success(self):
        """Тест успешного обновления токена"""
        data = {'refresh': self.refresh_token}
        response = self.client.post(self.refresh_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        """Тест обновления с невалидным токеном"""
        data = {'refresh': 'invalid.token.here'}
        response = self.client.post(self.refresh_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)