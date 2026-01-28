from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyHabitViewSet, PublicHabitViewSet

router = DefaultRouter()
router.register(r'my-habits', MyHabitViewSet, basename='my-habits')
router.register(r'public-habits', PublicHabitViewSet, basename='public-habits')

urlpatterns = [
    path('', include(router.urls)),
]
