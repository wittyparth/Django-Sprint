from rest_framework import serializers
from tags.serializers import TagSerializer
from tags.models import Tag
from bookmarks.models import Bookmark
from .models import BlogPost

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  # shows author's username
    slug = serializers.ReadOnlyField()
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source='tags',
        required=False,
        allow_null=True
    )
    like_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    is_bookmarked = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if user and user.is_authenticated:
            return Bookmark.objects.filter(user=user, post=obj).exists()
        return False

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_liked_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = BlogPost.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


    class Meta:
        model = BlogPost
        fields = '__all__'
        read_only_fields = ['author']