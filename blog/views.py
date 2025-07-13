from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import BlogPost,Comment,Like,Tag
from .serializers import BlogPostSerializer,UserRegisterSerializer,UserSerializer,CommentSerializer,LikeSerializer,TagSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsAuthorOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models


class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.all()  # What data it operates on
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter,DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_fields = ['author','created_at','tags']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    def get_serializer_context(self):
        return {'request': self.request}
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return BlogPost.objects.filter(models.Q(status='published') | models.Q(author=user))
        return BlogPost.objects.filter(status='published')


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        post_id = request.data.get('post')

        if Like.objects.filter(user=user, post_id=post_id).exists():
            return Response({'detail': 'Already liked'}, status=400)

        like = Like.objects.create(user=user, post_id=post_id)
        serializer = self.get_serializer(like)
        return Response(serializer.data, status=201)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Unauthorized'}, status=403)
        self.perform_destroy(instance)
        return Response(status=204)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]