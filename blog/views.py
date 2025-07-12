from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import BlogPost
from .serializers import BlogPostSerializer

class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.all()  # What data it operates on
    serializer_class = BlogPostSerializer
