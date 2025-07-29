from django.urls import path,include
from .views import RegisterView,MeView
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet,VerifyEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("register/",RegisterView.as_view(),name="register"),
    path("me/",MeView.as_view(),name="me"),
        path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # refresh
]
