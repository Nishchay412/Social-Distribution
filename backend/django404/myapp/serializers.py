from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like


User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # ✅ Uses create_user() to hash passwords

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author_username', 'text', 'created']
        read_only_fields = ['id','post','author_username', 'created']

""" Serializer for Post model with author_username as a read-only field. """
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'author_username',
            'title',
            'content',
            'image',
            'visibility',
            'published',
            'likes_count', 
            'comments_count',
            'comments',
        ]
        read_only_fields = ['id', 'author_username', 'published', 'likes_count', 'comments_count','comments']  # ✅ Prevents modification of these fields
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class LikeSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Like
        fields = ['id', 'post', 'author_username', 'created']
        read_only_fields = ['id', 'author_username', 'created']

