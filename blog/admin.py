from django.contrib import admin
from .models import BlogPost, Comment, Tag, Like

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'tags']
    search_fields = ['title', 'content']
