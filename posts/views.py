from django.utils import timezone
from django.shortcuts import render
from django.db.models import Count, Q
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework.viewsets import ModelViewSet
from config.permissions import IsAdminUserOrReadOnly, IsAuthorOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from config.pagination import CustomPagination
from rest_framework import filters
from config.permissions import IsAuthorOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.



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
        tags_data = self.request.POST.getlist('tags', [])
        serializer.save(author=self.request.user, tags=tags_data)

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
        sort = self.request.GET.get('sort')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'most_liked':
            queryset = queryset.annotate(likes_count=Count('likes')).order_by('-likes_count')
        elif sort == 'most_commented':
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count')

        # ✅ NEW: Filtering
        category_id = self.request.GET.get('category')
        tag_ids = self.request.GET.getlist('tags')  # ?tags=1&tags=3

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if tag_ids:
            queryset = queryset.filter(tags__in=tag_ids).distinct()

        return queryset
    
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

