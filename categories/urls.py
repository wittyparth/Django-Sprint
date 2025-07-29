from django.urls import path, include
from .views import CategoryListView


urlpatterns = [
    path('categories/', CategoryListView.as_view()),
]