from .models import CommentLike,Comment
from rest_framework import serializers

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        if self.parent and self.parent.parent:
            serializer = self.parent.parent.__class__(value, context=self.context)
            return serializer.data
        return None
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveField(many=True, read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'author_username',
            'content',
            'parent',
            'replies',
            'created_at',
            'likes_count'
        ]
        read_only_fields = ['author', 'author_username', 'replies', 'created_at']


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'comment', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']