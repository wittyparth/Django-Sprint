from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet,RegisterView,MeView,CommentViewSet,LikeViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet)  # GET /posts/, POST /posts/, etc.
router.register('comments', CommentViewSet)
router.register('likes', LikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("register/",RegisterView.as_view(),name="register"),
    path("me/",MeView.as_view(),name="me")
]
