from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import viewsets, permissions


from .models import Bookmark
from .serializers import BookmarkSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_bookmark(self, request):
        post_id = request.data.get('post')
        user = request.user

        try:
            bookmark = Bookmark.objects.get(user=user, post_id=post_id)
            bookmark.delete()
            return Response({'status': 'removed'})
        except Bookmark.DoesNotExist:
            Bookmark.objects.create(user=user, post_id=post_id)
            return Response({'status': 'saved'})








