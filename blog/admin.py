from django.contrib import admin
from .models import BlogPost,PostView
from django.contrib import admin
from .models import User

admin.site.register(User)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'tags']
    search_fields = ['title', 'content']


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'created_at')
    search_fields = ('ip_address',)
    list_filter = ('created_at',)
    