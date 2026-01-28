from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Habit
from .serializers import HabitSerializer


class HabitPagination(PageNumberPagination):
    """Пагинация для привычек"""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек текущего пользователя"""

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращаем только привычки текущего пользователя"""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании назначаем текущего пользователя"""
        serializer.save(user=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для публичных привычек (только чтение)"""

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Возвращаем только публичные привычки"""
        return Habit.objects.filter(is_public=True)