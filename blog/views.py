from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import BlogPost,Comment,Like,Tag
from .serializers import BlogPostSerializer,UserRegisterSerializer,UserSerializer,CommentSerializer,LikeSerializer,TagSerializer,CommentLikeSerializer
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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from .permissions import IsOwnerOrReadOnly,IsAuthorOrReadOnly
from .pagination import CustomPagination
from django.db.models import Count, Q
from rest_framework.decorators import action


class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.all()  # What data it operates on
    serializer_class = BlogPostSerializer # Whivh serializer it uses
    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter,DjangoFilterBackend,filters.OrderingFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['author','created_at','tags']
    ordering_fields = ['created_at', 'title','like_count']
    ordering = ['-created_at']
    lookup_field = 'slug'
    pagination_class = CustomPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Get IP
        ip = get_client_ip(request)

        # Check if already viewed in last 24 hours
        already_viewed = PostView.objects.filter(
            post=instance,
            ip_address=ip,
            viewed_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()

        # If not viewed recently, increment view count
        if not already_viewed:
            instance.view_count += 1
            instance.save(update_fields=['view_count'])
            PostView.objects.create(post=instance, ip_address=ip)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    def get_serializer_context(self):
        return {'request': self.request}
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return BlogPost.objects.filter(models.Q(status='published') | models.Q(author=user))
    #     return BlogPost.objects.filter(status='published')
    

    def get_queryset(self):
        queryset = BlogPost.objects.all().prefetch_related('tags', 'category')
        user = self.request.user
        if not user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
                # 👤 Authenticated users can see:
                # - Their own drafts + published
                # - Others' only published
                queryset = queryset.filter(
                    Q(status='published') | Q(author=user)
                )

        # Sort by newest, most_liked, etc. (already added)
        sort = self.request.query_params.get('sort')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'most_liked':
            queryset = queryset.annotate(likes_count=Count('likes')).order_by('-likes_count')
        elif sort == 'most_commented':
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count')

        # ✅ NEW: Filtering
        category_id = self.request.query_params.get('category')
        tag_ids = self.request.query_params.getlist('tags')  # ?tags=1&tags=3

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if tag_ids:
            queryset = queryset.filter(tags__in=tag_ids).distinct()

        return queryset

    def perform_create(self, serializer):
        tags_data = self.request.data.getlist('tags', [])
        serializer.save(author=self.request.user, tags=tags_data)


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


from rest_framework import viewsets, permissions
from .models import Profile
from .serializers import ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]


    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

from .models import Bookmark
from .serializers import BookmarkSerializer
from rest_framework import viewsets, permissions

from .models import Bookmark

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


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        post_id = self.request.query_params.get('post')
        if post_id:
            return Comment.objects.filter(post_id=post_id, parent=None)
        return Comment.objects.none()
    
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import CommentLike

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

from .models import Category, Tag
from rest_framework import generics
from .serializers import TagSerializer,CategorySerializer

class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def related_posts(request, post_id):
    try:
        current_post = BlogPost.objects.get(id=post_id)
    except BlogPost.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    # Step 1: Get posts with at least 1 shared tag
    tag_ids = current_post.tags.values_list('id', flat=True)
    tag_related = BlogPost.objects.filter(tags__in=tag_ids).exclude(id=post_id)

    # Step 2: Also check same category
    if current_post.category:
        category_related = BlogPost.objects.filter(category=current_post.category).exclude(id=post_id)
    else:
        category_related = BlogPost.objects.none()

    # Combine and remove duplicates
    related_qs = tag_related.union(category_related).distinct().order_by('-created_at')[:5]

    serializer = BlogPostSerializer(related_qs, many=True, context={'request': request})
    return Response(serializer.data)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import verify_token
from .models import User

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

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
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


    



# Use ModelViewSet to create an API for the Note model. Implement methods to allow users to create, view, update, and delete notes. Use perform_create() to assign the currently logged-in user as the owner.