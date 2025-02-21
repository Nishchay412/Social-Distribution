from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Image field

    def __str__(self):
      return f"{self.username}"



from django.db import models
from django.conf import settings
import uuid

class Post(models.Model):
    """
    A Post model demonstrating:
    - 'author' linked to the custom User model
    - 'content' field that can hold plain text or markdown
    - An optional 'image' field for images
    - A 'published' datetime
    - A 'visibility' field with options: 'PUBLIC', 'PRIVATE', 'DRAFT', 'DELETED'
    """
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),      # Visible to everyone
        ('PRIVATE', 'Private'),    # Only visible to the author
        ('DRAFT', 'Draft'),        # Not published yet
        ('DELETED', 'Deleted'),    # Soft delete (not actually removed)
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='PUBLIC'
    )
    published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Comment(models.Model):
    """
    A comment belongs to a single post, and has an author (User).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"
    
class Like(models.Model):
    """
    A like belongs to a single post and has an author (User).
    If you want 'likes on comments', you can add a separate field or a separate model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} liked post {self.post.id}"
    
