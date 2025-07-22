from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet,RegisterView,MeView,CommentViewSet,LikeViewSet,ProfileViewSet,TagViewSet,BookmarkViewSet,TagListView,CategoryListView,related_posts,VerifyEmailView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
from .views import BookmarkViewSet
from .views import CommentLikeViewSet

router.register(r'comment-likes', CommentLikeViewSet)

router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')

router.register(r'tags', TagViewSet)


router.register(r'posts', BlogPostViewSet)  # GET /posts/, POST /posts/, etc.
router.register('comments', CommentViewSet)
router.register('likes', LikeViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("register/",RegisterView.as_view(),name="register"),
    path("me/",MeView.as_view(),name="me"),
    path('tags/', TagListView.as_view()),
    path('categories/', CategoryListView.as_view()),
    path('posts/<int:post_id>/related/', related_posts, name='related-posts'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
