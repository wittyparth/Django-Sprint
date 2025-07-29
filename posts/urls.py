from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BlogPostViewSet,related_posts

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet)

urlpatterns = [
    path("",include(router.urls)),
    path('posts/<int:post_id>/related/', related_posts, name='related-posts'),
]