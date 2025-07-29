from django.shortcuts import render
from .models import Like
from rest_framework import viewsets
from .serializers import LikeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
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