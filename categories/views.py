from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import Category
from .serializers import CategorySerializer
# Create your views here.
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer