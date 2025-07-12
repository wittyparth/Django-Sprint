from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet)  # GET /posts/, POST /posts/, etc.

urlpatterns = [
    path('', include(router.urls)),
]
