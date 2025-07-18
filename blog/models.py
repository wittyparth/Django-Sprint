import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=3000)  # title can be very long
    content = models.TextField()
    image = models.ImageField(
        upload_to='blog_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True) # RElated name will give a custom to access posts from tag like tag = Tag.object.get(name="js") tag.posts.all()
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField(null=True, blank=True)

    def is_published(self):
        return self.status == 'published' and (self.publish_date is None or self.publish_date <= timezone.now())
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:50]
            unique_suffix = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    def is_reply(self):
        return self.parent is not None

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
    
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import Profile  # avoid circular imports
        Profile.objects.create(user=instance)

from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # 💡 Prevents double-bookmarking

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"
