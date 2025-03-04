from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

#Nishchay Ranjan
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # Mutual friendship: when one user adds another, it's automatically mutual.
    friends = models.ManyToManyField("self", blank=True, symmetrical=True)
    is_approved = models.BooleanField(default=True)  # New users need approval
    is_admin = models.BooleanField(default=False)  # Admins can manage users/nodes

    def __str__(self):
        return self.username



from django.db import models
from django.conf import settings
import uuid

#QingqiuTan/Nishchay Ranjan/Riyasat Zaman
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
    ('PUBLIC', 'Public'),       # Visible to everyone
    ('UNLISTED', 'Unlisted'),   # Visible to followers and anyone with the link
    ('FRIENDS', 'Friends Only'),# Visible to friends (and the author)
    ('PRIVATE', 'Private'),     # Visible only to the author
    ('DRAFT', 'Draft'),         # Not published yet
    ('DELETED', 'Deleted'),     # Soft delete (not actually removed, only node admin can see)
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
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft Delete
    
    def is_deleted(self):
        return self.deleted_at is not None  # ✅ Check if post is deleted

    def __str__(self):
        return f"{self.title} by {self.author.username}"

#QingqiuTan 
class Comment(models.Model):
    """
    A comment left by a user on a specific Post.
    Each comment is tied to exactly one Post, and one author (User).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"

#QingqiuTan
class Like(models.Model):
    """
    Represents a 'like' from a specific user on a specific post.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.author.username} liked {self.post.id}"

#Yicheng Lin
class Node(models.Model):
    """
    Represents a remote node that this server can communicate with.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_url = models.URLField(unique=True)  # URL of the remote node
    username = models.CharField(max_length=255)  # For Basic Auth
    password = models.CharField(max_length=255)  # For Basic Auth
    is_active = models.BooleanField(default=True)  # Can be disabled

    def __str__(self):
        return f"Node {self.base_url} (Active: {self.is_active})"
