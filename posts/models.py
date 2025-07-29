from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import math
from django.conf import settings
import uuid
from django.utils.text import slugify
from tags.models import Tag
from categories.models import Category
# Create your models here.

class BlogPost(models.Model):
    title = models.CharField(max_length=3000)  # title can be very long
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField(null=True, blank=True)
    reading_time = models.PositiveIntegerField(default=1)  # minutes


    def is_published(self):
        return self.status == 'published' and (self.publish_date is None or self.publish_date <= timezone.now())
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:50]
            unique_suffix = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_suffix}"
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = math.ceil(word_count / 200)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class PostView(models.Model):
    post = models.ForeignKey(BlogPost,related_name="views",on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} viewed {self.post.title}"