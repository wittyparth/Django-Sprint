from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet,RegisterView,MeView,CommentViewSet,LikeViewSet,ProfileViewSet
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet)  # GET /posts/, POST /posts/, etc.
router.register('comments', CommentViewSet)
router.register('likes', LikeViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("register/",RegisterView.as_view(),name="register"),
    path("me/",MeView.as_view(),name="me")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
