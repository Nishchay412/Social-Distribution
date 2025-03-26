from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Following, Post, Comment, Like, Notif, CommentLike, Node,RemoteFollower
import markdown
import base64
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings

User = get_user_model()
class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image uploads through base64 encoding.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # Base64 encoded image - decode
            format, datastr = data.split(';base64,')
            ext = format.split('/')[-1]
            
            data = ContentFile(base64.b64decode(datastr), name=f'temp.{ext}')
        
        return super().to_internal_value(data)

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

class CrossNodePostSerializer(PostSerializer):
    """
    Extended version of PostSerializer with cross-node functionality.
    """
    image = Base64ImageField(required=False, allow_null=True)
    content_type = serializers.ChoiceField(
        choices=['text/plain', 'text/markdown'], 
        default='text/markdown',
        required=False
    )
    local_copy = serializers.BooleanField(read_only=True)
    original_node = serializers.CharField(read_only=True)
    needs_sync = serializers.BooleanField(read_only=True)
    is_deleted = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            'content_type', 'local_copy', 'original_node', 
            'needs_sync', 'is_deleted'
        ]
        read_only_fields = PostSerializer.Meta.read_only_fields + [
            'local_copy', 'original_node', 'is_deleted'
        ]
    
    def get_is_deleted(self, obj):
        return obj.is_deleted()
    
    def get_content_html(self, obj):
        # Only render markdown if content_type is markdown
        if hasattr(obj, 'content_type') and obj.content_type == 'text/markdown':
            return markdown.markdown(obj.content or '')
        # Otherwise return plain text
        return obj.content or ''
    
    def create(self, validated_data):
        # Set cross-node specific fields
        validated_data['author'] = self.context['request'].user
        validated_data['original_node'] = settings.INSTANCE_NAME
        validated_data['local_copy'] = True
        validated_data['needs_sync'] = True
        
        # Use default markdown if not specified
        if 'content_type' not in validated_data:
            validated_data['content_type'] = 'text/markdown'
        
        # Create the post using the parent class method
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Mark for sync
        validated_data['needs_sync'] = True
        validated_data['updated'] = timezone.now()
        
        # Update the post
        return super().update(instance, validated_data)


class RemotePostSerializer(serializers.Serializer):
    """
    Serializer for processing posts from remote nodes
    """
    id = serializers.UUIDField()
    title = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    content_type = serializers.CharField(default='text/markdown')
    author = serializers.DictField()
    visibility = serializers.CharField()
    published = serializers.DateTimeField()
    updated = serializers.DateTimeField(required=False)
    image_content = serializers.CharField(allow_null=True, required=False)
    is_deleted = serializers.BooleanField(default=False)
    original_node = serializers.CharField()
    
    def create(self, validated_data):
        """
        Create or update a post received from a remote node
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Extract author data
        author_data = validated_data.pop('author')
        
        # Create or get remote user
        author, created = User.objects.get_or_create(
            username=f"{author_data['username']}@{validated_data['original_node']}",
            defaults={
                'first_name': author_data.get('displayName', author_data['username']),
                'last_name': '',  # Could be left empty or set to a default value
                'is_approved': True,  # Remote users should be considered approved
                'email': f"{author_data['username']}@{validated_data['original_node']}.remote"  # Required email field
            }
        )
        
        # Extract media and deletion info
        image_content = validated_data.pop('image_content', None)
        is_deleted = validated_data.pop('is_deleted', False)
        
        # Try to find existing post
        post_id = validated_data['id']
        try:
            post = Post.objects.get(id=post_id)
            
            # Update existing post
            for attr, value in validated_data.items():
                setattr(post, attr, value)
            
            post.author = author
            post.local_copy = False
            
            # Handle deletion
            if is_deleted:
                post.deleted_at = timezone.now()
                post.visibility = 'DELETED'
            
            # Handle image if provided
            if image_content and not is_deleted:
                # Parse image format from content_type or default to jpeg
                format_type = 'jpeg'
                if 'content_type' in validated_data and '/' in validated_data['content_type']:
                    format_parts = validated_data['content_type'].split('/')
                    if len(format_parts) > 1 and format_parts[0] == 'image':
                        format_type = format_parts[1]
                
                post.image.save(
                    f"{post_id}.{format_type}", 
                    ContentFile(base64.b64decode(image_content)),
                    save=False
                )
            
            post.save()
            
        except Post.DoesNotExist:
            # Create new post
            validated_data['author'] = author
            validated_data['local_copy'] = False
            
            # Handle deletion status
            if is_deleted:
                validated_data['deleted_at'] = timezone.now()
                validated_data['visibility'] = 'DELETED'
            
            post = Post.objects.create(**validated_data)
            
            # Handle image if provided
            if image_content and not is_deleted:
                format_type = 'jpeg'
                if 'content_type' in validated_data and '/' in validated_data['content_type']:
                    format_parts = validated_data['content_type'].split('/')
                    if len(format_parts) > 1 and format_parts[0] == 'image':
                        format_type = format_parts[1]
                
                post.image.save(
                    f"{post_id}.{format_type}", 
                    ContentFile(base64.b64decode(image_content)),
                    save=True
                )
            
        return post


class RemoteFollowerSerializer(serializers.ModelSerializer):
    """Serializer for the RemoteFollower model"""
    class Meta:
        model = RemoteFollower
        fields = ['local_user', 'remote_username', 'remote_node', 'created_at']
        read_only_fields = ['created_at']