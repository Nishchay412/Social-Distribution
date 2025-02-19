from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Ensures unique email
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Post(models.Model):
    """
    A simple Post model demonstrating:
    - 'author' linked to custom User model
    - A 'content' field that can hold plain text or markdown
    - An optional 'image' field for images
    - A 'published' datetime
    - A 'visibility' field so we can do 'PUBLIC' or 'DELETED' if we like
    """
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('DELETED', 'Deleted'),
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