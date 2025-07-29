from rest_framework import serializers
from .models import User,Profile
# from django.contrib.auth.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=6)
    class Meta:
        model = User
        fields = ["username","email","password"]
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password=validated_data["password"]
        )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'username',
            'email',
            'avatar_url',
            'bio',
            'website',
            'location',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'username', 'email']


class UserSummarySerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    likes_given = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['name', 'email', 'bio', 'joined', 'posts_count', 'comments_count', 'likes_given']