from rest_framework.routers import DefaultRouter
from .views import BookmarkViewSet,BookmarkViewSet
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()


router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')


urlpatterns = [
    path('', include(router.urls)),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
