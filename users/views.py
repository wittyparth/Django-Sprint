from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import UserRegisterSerializer, UserSerializer,ProfileSerializer,UserSummarySerializer
from users.models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from config.permissions import IsOwnerOrReadOnly
from django.db.models import Count, Q
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
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


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]


    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

from .serializers import UserSummarySerializer

User = get_user_model()

@api_view(['GET'])
def admin_user_summary(request):
    users = User.objects.annotate(
        posts_count=Count('blogpost'),
        comments_count=Count('comment'),
        likes_given=Count('likes_given')  # adjust to your like model
    )
    data = UserSummarySerializer(users, many=True).data
    return Response({'users': data})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Ensure verify_token is correctly imported from its actual location
from config.utils import verify_token  # Verify this path or define verify_token in config/utils.py
from users.models import User

class VerifyEmailView(APIView):
    def get(self, request, token):
        user_id = verify_token(token)
        if not user_id:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)