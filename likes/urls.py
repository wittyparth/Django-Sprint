from .views import LikeViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register('likes', LikeViewSet)
urlpatterns = [
    path('', include(router.urls)),
]