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
    
class CommentLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} liked comment {self.comment.id}"
