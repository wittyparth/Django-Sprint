from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, TagListView

router = DefaultRouter()

router.register(r'tags', TagViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('tags/', TagListView.as_view()),
]