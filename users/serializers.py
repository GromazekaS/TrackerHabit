from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    telegram_chat_id = serializers.CharField(
        source='profile.telegram_chat_id',
        allow_blank=True,
        required=False
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'telegram_chat_id']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают."}
            )
        return attrs

    def create(self, validated_data):
        """Создание пользователя с хэшированием пароля"""
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """Обновление профиля с telegram_chat_id"""
        profile_data = validated_data.pop('profile', {})

        # Обновляем пользователя
        instance = super().update(instance, validated_data)

        # Обновляем профиль
        if profile_data and 'telegram_chat_id' in profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            profile.telegram_chat_id = profile_data['telegram_chat_id']
            profile.save()

        return instance