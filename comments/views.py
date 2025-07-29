from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import CommentLike,Comment
from .serializers import CommentSerializer, CommentLikeSerializer
from rest_framework import viewsets, permissions
# Create your views here.

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        post_id = self.request.GET.get('post')
        if post_id:
            return Comment.objects.filter(post_id=post_id, parent=None)
        return Comment.objects.none()
    

class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_like(self, request):
        comment_id = request.data.get('comment')
        user = request.user

        try:
            like = CommentLike.objects.get(user=user, comment_id=comment_id)
            like.delete()
            return Response({'status': 'unliked'})
        except CommentLike.DoesNotExist:
            CommentLike.objects.create(user=user, comment_id=comment_id)
            return Response({'status': 'liked'})