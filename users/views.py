from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserRegistrationSerializer

from .models import Profile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор JWT токена с добавлением username"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Вью для получения JWT токена"""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Вью для регистрации пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []  # Разрешаем доступ без аутентификации

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем токен для нового пользователя
        token_serializer = CustomTokenObtainPairSerializer()
        token = token_serializer.get_token(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'access': str(token.access_token),
            'refresh': str(token),
        }, status=status.HTTP_201_CREATED)


class TelegramConnectView(generics.UpdateAPIView):
    """Эндпоинт для привязки Telegram chat_id"""

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        telegram_chat_id = request.data.get('telegram_chat_id')

        if not telegram_chat_id:
            return Response(
                {'error': 'telegram_chat_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем или создаем профиль
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'telegram_chat_id': telegram_chat_id}
        )

        if not created:
            profile.telegram_chat_id = telegram_chat_id
            profile.save()

        return Response({
            'message': 'Telegram успешно привязан',
            'telegram_chat_id': telegram_chat_id
        })
