from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid
import markdown
from django.utils import timezone


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
    home_node = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Identifier or URL of the node where this user is registered"
    )

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
    - Support for cross-node distribution
    """
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),  # Visible to everyone
        ('UNLISTED', 'Unlisted'),  # Visible to followers and anyone with the link
        ('FRIENDS', 'Friends Only'),  # Visible to friends (and the author)
        ('PRIVATE', 'Private'),  # Visible only to the author
        ('DRAFT', 'Draft'),  # Not published yet
        ('DELETED', 'Deleted'),  # Soft delete (not actually removed, only node admin can see)
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('text/plain', 'Plain Text'),
        ('text/markdown', 'CommonMark'),
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
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='text/markdown'
    )
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft Delete
    
    # Fields for cross-node synchronization
    local_copy = models.BooleanField(default=True, 
                                   help_text='Is this post native to this node?')
    original_node = models.CharField(max_length=50, blank=True, 
                                  help_text='Which node created this post')
    remote_nodes_sent = models.JSONField(default=list, blank=True, 
                                     help_text='List of node identifiers this post has been sent to')
    needs_sync = models.BooleanField(default=False, 
                                  help_text='Track if changes need to be synced')
    
    def is_deleted(self):
        return self.deleted_at is not None or self.visibility == 'DELETED'
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def mark_for_sync(self):
        """Mark this post as needing to be synced to remote nodes"""
        self.needs_sync = True
        self.save(update_fields=['needs_sync', 'updated'])
    
    def add_remote_node_sent(self, node_id):
        """Add a node to the list of nodes this post has been sent to"""
        if not self.remote_nodes_sent:
            self.remote_nodes_sent = []
            
        if node_id not in self.remote_nodes_sent:
            self.remote_nodes_sent.append(node_id)
            self.save(update_fields=['remote_nodes_sent', 'updated'])
    
    def to_dict(self):
        """Convert post to dictionary format for API transmission"""
        # Get node configuration from settings
        from django.conf import settings
        
        # Determine if post is considered deleted
        is_deleted = self.is_deleted()
        
        # Get node URL for source/origin
        node_url = settings.NODE_CONFIG[settings.INSTANCE_NAME]['url']
        
        return {
            'id': str(self.id),
            'title': self.title,
            'source': f"{node_url}/posts/{self.id}/",
            'origin': f"{node_url}/posts/{self.id}/",
            'content_type': self.content_type,
            'content': self.content,
            'author': {
                'id': str(self.author.id),
                'username': self.author.username,
                'displayName': getattr(self.author, 'displayName', self.author.username),
            },
            'visibility': self.visibility,
            'published': self.published.isoformat(),
            'updated': self.updated.isoformat(),
            'is_deleted': is_deleted,
            'original_node': self.original_node or settings.INSTANCE_NAME,
            'has_image': bool(self.image),
        }

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

class RemoteFollower(models.Model):
    """
    Tracks remote users who follow local users.
    This is used to know which remote nodes to send posts to.
    """
    local_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='remote_followers'
    )
    remote_username = models.CharField(max_length=255)
    remote_node = models.CharField(max_length=50)  # Node identifier
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['local_user', 'remote_username', 'remote_node']
        
    def __str__(self):
        return f"{self.remote_username}@{self.remote_node} follows {self.local_user.username}"