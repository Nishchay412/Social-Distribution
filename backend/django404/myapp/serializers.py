from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Following, Post, Comment, Like, Notif, CommentLike, Node
import markdown

User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for User model with password hashing."""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # Uses create_user() to hash passwords

# Serializer for Following model (by Christine Bao)
class FollowingSerializer(serializers.ModelSerializer):
    """
    Serializer for Following Model
    - follower and followee are read-only.
    """
    follower_username = serializers.ReadOnlyField(source='follower.username')
    followee_username = serializers.ReadOnlyField(source='followee.username')
    
    class Meta:
        model = Following
        fields  = ['friends', 'follower_username', 'followee_username', 'followed_at']

# Serializer for Node model (by Yicheng Lin)
class NodeSerializer(serializers.ModelSerializer):
    """Ensures safe handling of node data without exposing passwords."""
    class Meta:
        model = Node
        fields = ['id', 'base_url', 'username', 'is_active']
        read_only_fields = ['id']  # Prevent clients from modifying node ID

    def create(self, validated_data):
        """Prevents exposing password in API responses."""
        node = Node.objects.create(**validated_data)
        return node

    def update(self, instance, validated_data):
        """Ensure password is not updated accidentally."""
        validated_data.pop("password", None)  # Ignore password updates
        return super().update(instance, validated_data)

# Serializer for Comment model (by QingqiuTan)
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author_username', 'text', 'created', 'likes_count']
        read_only_fields = ['id', 'post', 'author_username', 'created', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

# Serializer for Post model (by QingqiuTan/Nishchay Ranjan/Riyasat Zaman)
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    title = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    comments = CommentSerializer(many=True, read_only=True)
    content_html = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'author_username',
            'title',
            'content',
            'content_html',
            'image',
            'visibility',
            'published',
            'likes_count', 
            'comments_count',
            'comments',
            'updated',
            'deleted_at'
        ]
        read_only_fields = ['id', 'author_username', 'published', 'updated', 'likes_count', 'comments_count', 'comments']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_content_html(self, obj):
        # Convert the markdown content to HTML.
        return markdown.markdown(obj.content or '')
    
    def validate(self, data):
        # Ensure that at least one of title, content, or image is provided.
        if not data.get('title') and not data.get('content') and not data.get('image'):
            raise serializers.ValidationError("At least one of title/content/image is required.")
        return data

# Serializer for Like model (by QingqiuTan)
class LikeSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Like
        fields = ['id', 'post', 'author_username', 'created']
        read_only_fields = ['id', 'author_username', 'created']

# Serializer for Notif model (by Christine Bao)
class NotifSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    
    class Meta:
        model = Notif
        fields = ['id', 'receiver', 'sender_username', 'notif_type', 'post', 'comment', 'created_at']

# Serializer for CommentLike model (by Yicheng Lin)
class CommentLikeSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = CommentLike
        fields = ['id', 'author_username', 'comment', 'created']
        read_only_fields = ['id', 'author_username', 'created', 'comment']
