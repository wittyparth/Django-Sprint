from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bookmarks.urls')),  # All API endpoints now under /api/
    path("api/",include("users.urls")),
    path("api/",include("posts.urls")),
    path("api/",include("comments.urls")),
    path("api/",include("likes.urls")),
    path("api/",include("categories.urls")),
    path("api/",include("tags.urls")),
]
