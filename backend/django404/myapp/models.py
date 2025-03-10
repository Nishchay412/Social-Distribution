from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid
import markdown

# Nishchay Ranjan
class User(AbstractUser):
    """
    Custom User model with the following fields:
    - email (unique)
    - first_name
    - last_name
    - profile_image
    - friends (ManyToManyField to 'self')
    - is_approved (BooleanField)
    - is_admin (BooleanField)
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # Mutual friendship: when one user adds another, it's automatically mutual.
    friends = models.ManyToManyField("self", blank=True, symmetrical=True)
    is_admin = models.BooleanField(default=False)  # Admins can manage users/nodes
    # New users need approval (default set to False)
    is_approved = models.BooleanField(default=False, editable=True)

    def __str__(self):
        return self.username

# Following model (by Christine Bao)
class Following(models.Model):
    """
    Following model
    - 'follower' userId of user who wants to follow
    - 'followee' userId of user being followed
    - 'followed_at' is DateTimeField of when follower follows followee
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='follower'
    )
    followee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='followee'
    )
    # This field can be used to denote additional friend-related info
    friends = models.CharField(
        max_length=10,
        default='NO'
    )
    followed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} followed {self.followee}"

# QingqiuTan / Nishchay Ranjan / Riyasat Zaman
class Post(models.Model):
    """
    A Post model demonstrating:
    - 'author' linked to the custom User model
    - 'content' field that can hold plain text or markdown
    - An optional 'image' field for images
    - A 'published' datetime
    - A 'visibility' field with options: 'PUBLIC', 'UNLISTED', 'FRIENDS', 'PRIVATE', 'DRAFT', 'DELETED'
    """
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),        # Visible to everyone
        ('UNLISTED', 'Unlisted'),    # Visible to followers and anyone with the link
        ('FRIENDS', 'Friends Only'), # Visible to friends (and the author)
        ('PRIVATE', 'Private'),      # Visible only to the author
        ('DRAFT', 'Draft'),          # Not published yet
        ('DELETED', 'Deleted'),      # Soft delete (not actually removed, only node admin can see)
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='PUBLIC'
    )
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft Delete

    def is_deleted(self):
        return self.deleted_at is not None  # Check if post is deleted

    def __str__(self):
        return f"{self.title} by {self.author.username}"

# QingqiuTan 
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

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"

# QingqiuTan
class Like(models.Model):
    """
    Represents a 'like' from a specific user on a specific post.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} liked {self.post.id}"

# Notification Model (by Christine Bao)
class Notif(models.Model):
    """
    Notification Model that holds notifications when an author receives a like, comment, or follow request.
    
    - 'receiver': User receiving the notification.
    - 'sender': User sending the notification.
    - 'notif_type': Type of notification: 'LIKE', 'COMMENT', or 'FOLLOW_REQUEST'.
    - 'post': Optional field, linked to a Post if the notification is for a like or comment.
    - 'comment': Optional field, linked to a Comment if the notification is for a comment.
    - 'created_at': Datetime when the notification was created.
    """
    NOTIF_CHOICES = [
        ('LIKE', 'like'),
        ('COMMENT', 'comment'),
        ('FOLLOW_REQUEST', 'follow_request')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='receiver'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sender'
    )
    notif_type = models.CharField(
        max_length=20,
        choices=NOTIF_CHOICES,
        default='PUBLIC'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        blank=True,
        null=True,
        related_name="post_notif"
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE, 
        blank=True,
        null=True,
        related_name="comment_notif"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receiver} has {self.notif_type} {self.sender}"

# Yicheng Lin
class Node(models.Model):
    """
    Represents a remote node that this server can communicate with.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_url = models.URLField(unique=True)  # URL of the remote node
    username = models.CharField(max_length=255)  # For Basic Auth
    password = models.CharField(max_length=255)  # For Basic Auth
    is_active = models.BooleanField(default=True)  # Can be disabled
    description = models.TextField(blank=True, null=True)  # Optional description
    last_connected = models.DateTimeField(blank=True, null=True)  # Last successful connection

    def __str__(self):
        return f"Node {self.base_url} (Active: {self.is_active})"

class CommentLike(models.Model):
    """
    Represents a 'like' from a specific user on a specific comment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} liked comment {self.comment.id}"
