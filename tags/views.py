from django.shortcuts import render
from .models import Tag
from rest_framework import viewsets
from .serializers import TagSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer