from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, CommentLikeViewSet
from django.urls import path, include

router = DefaultRouter()

router.register('comments', CommentViewSet)
router.register(r'comment-likes', CommentLikeViewSet)

urlpatterns = [
    path("",include(router.urls))
]